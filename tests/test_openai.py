import json
import os
import unittest
import urllib.error
from unittest.mock import MagicMock, patch
import app


class OpenAiTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'AI_MODE': 'openai', 'OPENAI_API_KEY': 'test-only-key'})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def response(self, proposal, finish='stop', refusal=None):
        reply = MagicMock()
        reply.__enter__.return_value.read.return_value = json.dumps({
            'id': 'chatcmpl-test', 'model': 'gpt-4.1-mini',
            'usage': {'prompt_tokens': 500, 'completion_tokens': 30, 'total_tokens': 530},
            'choices': [{'finish_reason': finish, 'message': {'content': json.dumps(proposal), 'refusal': refusal}}]
        }).encode()
        return reply

    def test_structured_request_and_inference_evidence(self):
        history = ['must finish by 3 pm', 'afternoon', 'same date', 'yes', 'still before 3']
        with patch('urllib.request.urlopen', return_value=self.response({'slot_id': 'B', 'reason': 'Ends at 3 pm.'})) as call:
            result = app.plan('please offer it', app.initial()['slots'], history)
        request = call.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, 'https://api.openai.com/v1/chat/completions')
        self.assertFalse(payload['store'])
        self.assertEqual(payload['max_completion_tokens'], 180)
        self.assertTrue(payload['response_format']['json_schema']['strict'])
        self.assertEqual(json.loads(payload['messages'][1]['content'])['prior_messages'], history)
        self.assertEqual(result['inference']['request_id'], 'chatcmpl-test')
        self.assertEqual(result['slot_id'], 'B')

    def test_refusal_and_truncation_fail_without_fixture_fallback(self):
        for finish, refusal in [('length', None), ('stop', 'Unable to comply')]:
            with patch('urllib.request.urlopen', return_value=self.response({'slot_id': 'A', 'reason': 'x'}, finish, refusal)):
                with self.assertRaises(app.Problem) as err:
                    app.plan('morning', app.initial()['slots'], [])
                self.assertEqual(err.exception.status, 502)

    def test_api_error_does_not_expose_provider_body_or_key(self):
        exc = urllib.error.HTTPError('https://api.openai.com/v1/chat/completions', 401, 'secret-body', {}, None)
        with patch('urllib.request.urlopen', side_effect=exc):
            with self.assertRaises(app.Problem) as err:
                app.plan('morning', app.initial()['slots'], [])
        self.assertNotIn('secret-body', err.exception.message)
        self.assertNotIn('test-only-key', err.exception.message)

    def test_missing_key_fails_before_network(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}), patch('urllib.request.urlopen') as call:
            with self.assertRaises(app.Problem):
                app.plan('morning', app.initial()['slots'], [])
            call.assert_not_called()

    def test_invented_slot_is_rejected(self):
        with patch('urllib.request.urlopen', return_value=self.response({'slot_id': 'MIDNIGHT', 'reason': 'x'})):
            with self.assertRaises(app.Problem):
                app.plan('midnight', app.initial()['slots'], [])


if __name__ == '__main__':
    unittest.main()
