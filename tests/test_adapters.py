"""Contract tests with fake SDK modules; these do not imply live AI verification."""
import json
import os
import sys
import types
import unittest
from unittest.mock import Mock, patch
import app


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.factory = Mock(return_value=self.client)
        modules = {'boto3': types.SimpleNamespace(client=self.factory),
                   'botocore': types.ModuleType('botocore'),
                   'botocore.config': types.SimpleNamespace(Config=lambda **kw: kw)}
        self.modules = patch.dict(sys.modules, modules)
        self.modules.start()
        self.env = patch.dict(os.environ, {'AI_MODE': 'bedrock', 'MAIL_MODE': 'ses',
            'SES_SENDER': 'sender@example.com', 'TEST_RECIPIENT': 'recipient@example.com'})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.modules.stop()

    def reply(self, value):
        self.client.converse.return_value = {'output': {'message': {'content': [{'text': json.dumps(value)}]}}}

    def test_model_receives_inventory_history_and_token_cap(self):
        self.reply({'slot_id': 'C', 'reason': 'The late window fits.'})
        out = app.plan('after 3 pm', app.initial()['slots'], ['any time'])
        self.assertEqual(out['slot_id'], 'C')
        args = self.client.converse.call_args.kwargs
        payload = json.loads(args['messages'][0]['content'][0]['text'])
        self.assertEqual(payload['prior_messages'], ['any time'])
        self.assertEqual(len(payload['available_slots']), 3)
        self.assertEqual(args['inferenceConfig']['maxTokens'], 180)
        self.assertEqual(self.factory.call_args.kwargs['config']['retries']['total_max_attempts'], 1)

    def test_model_clarification_is_preserved(self):
        self.reply({'slot_id': None, 'reason': 'Do you mean before noon or after noon?'})
        out = app.plan('around lunch', app.initial()['slots'], [])
        self.assertIsNone(out['slot_id'])
        self.assertIn('before noon', out['reason'])

    def test_model_cannot_propose_a_booked_slot(self):
        slots = app.initial()['slots']
        slots[0]['booked_by'] = 'another-customer'
        self.reply({'slot_id': 'A', 'reason': 'Book it.'})
        self.assertIsNone(app.plan('morning', slots, [])['slot_id'])

    def test_malformed_model_output_fails_closed(self):
        for value in ([], {'slot_id': ['A'], 'reason': 'invalid'}, {'slot_id': 'D', 'reason': 'invented'}):
            self.reply(value)
            with self.assertRaises(app.Problem) as err:
                app.plan('morning', app.initial()['slots'], [])
            self.assertEqual(err.exception.status, 502)

    def test_model_failure_is_not_replaced_by_fixture(self):
        self.client.converse.side_effect = RuntimeError('model unavailable')
        with self.assertRaises(RuntimeError):
            app.plan('morning', app.initial()['slots'], [])

    def test_ses_acceptance_evidence_comes_from_sdk(self):
        self.client.send_email.return_value = {'MessageId': 'sdk-message-id'}
        out = app.mail('recipient@example.com', 'Offer', 'Review your slot')
        self.assertEqual(out, {'status': 'ACCEPTED_BY_SES', 'message_id': 'sdk-message-id'})
        args = self.client.send_email.call_args.kwargs
        self.assertEqual(args['Destination'], {'ToAddresses': ['recipient@example.com']})
        self.assertEqual(self.factory.call_args.kwargs['config']['retries']['total_max_attempts'], 1)

    def test_wrong_recipient_never_reaches_ses(self):
        with self.assertRaises(app.Problem):
            app.mail('other@example.com', 'Offer', 'body')
        self.client.send_email.assert_not_called()


if __name__ == '__main__':
    unittest.main()
