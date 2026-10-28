import json
import os
import tempfile
import unittest
from unittest.mock import patch
import app


class PublicDemoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'DB_PATH': self.tmp.name + '/state.db', 'TABLE_NAME': '',
            'AI_MODE': 'rehearsal', 'MAIL_MODE': 'ses', 'TEST_RECIPIENT': 'owner@example.com', 'OPERATOR_KEY': 'test-secret'})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def request(self, path, data=None, session=None):
        headers = {} if session is None else {'x-demo-session': session['session'], 'x-customer-token': session['token']}
        out = app.handler({'rawPath': path, 'headers': headers, 'body': json.dumps(data or {}),
            'requestContext': {'http': {'method': 'GET' if data is None else 'POST'}}})
        return out['statusCode'], json.loads(out['body'])

    def start(self):
        status, result = self.request('/api/demo/start', {'message': 'morning'})
        self.assertEqual(status, 201)
        return result

    def test_full_loop_never_sends_and_preserves_operator_inventory(self):
        with patch('app.mail') as send:
            s = self.start()
            c = s['case']
            status, booked = self.request('/api/demo/' + c['id'] + '/confirm', {'slot_id': 'A', 'version': 1}, s)
            self.assertEqual(status, 200)
            self.assertEqual(booked['status'], 'BOOKED')
            self.assertTrue(all(m['status'] == 'PREVIEW_ONLY' for m in booked['mail'].values()))
            self.assertTrue(all(x['booked_by'] is None for x in app.Store().read()['slots']))
            send.assert_not_called()

    def test_sessions_cannot_access_one_another(self):
        a, b = self.start(), self.start()
        status, _ = self.request('/api/demo/' + a['case']['id'], session=b)
        self.assertEqual(status, 404)
        self.assertNotEqual(a['session'], b['session'])

    def test_tampered_and_expired_sessions_rejected(self):
        s = self.start()
        s['session'] = '0' + s['session'][1:] if s['session'][0] != '0' else '1' + s['session'][1:]
        self.assertEqual(self.request('/api/demo/' + s['case']['id'], session=s)[0], 401)
        s = self.start()
        with patch('app.time.time', return_value=9999999999):
            self.assertEqual(self.request('/api/demo/' + s['case']['id'], session=s)[0], 401)

    def test_daily_budget_fails_before_inference(self):
        budget = app.Store('budget:' + app.dt.datetime.now(app.dt.timezone.utc).date().isoformat())
        state = budget.read()
        state['inference'] = 150
        budget.save(state, 0)
        with patch('app.plan') as planner:
            self.assertEqual(self.request('/api/demo/start', {'message': 'morning'})[0], 429)
            planner.assert_not_called()

    def test_operator_stays_protected_and_asset_traversal_rejected(self):
        self.assertEqual(self.request('/api/dashboard')[0], 401)
        self.assertEqual(self.request('/assets/../app.py')[0], 404)

    def test_no_match_stale_version_and_duplicate_confirmation(self):
        s = self.start()
        path = '/api/demo/' + s['case']['id']
        status, c = self.request(path + '/reply', {'message': 'before dawn', 'version': 1}, s)
        self.assertEqual(c['status'], 'NEEDS_INPUT')
        self.assertEqual(self.request(path + '/confirm', {'slot_id': 'A', 'version': 1}, s)[0], 409)
        status, c = self.request(path + '/reply', {'message': 'afternoon', 'version': 2}, s)
        args = {'slot_id': 'B', 'version': 3}
        status, first = self.request(path + '/confirm', args, s)
        status, second = self.request(path + '/confirm', args, s)
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()
