"""Small live OpenAI + SES smoke test. Sends two emails to the approved recipient."""
import argparse
import json
import pathlib
import urllib.error
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--send-to', required=True)
    parser.add_argument('--request-id', required=True, help='Reuse this value if retrying creation.')
    args = parser.parse_args()
    root = pathlib.Path(__file__).resolve().parents[1]
    base = 'https://tidx9k8p3g.execute-api.us-east-1.amazonaws.com'
    key = (root / '.private/operator-key.txt').read_text().strip()

    def call(path, body=None, token=None):
        headers = {'Content-Type': 'application/json'}
        headers.update({'X-Customer-Token': token} if token else {'Authorization': 'Bearer ' + key})
        request = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
            headers=headers, method='POST' if body is not None else 'GET')
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            raise RuntimeError('HTTP ' + str(exc.code) + ': ' + exc.read().decode()) from None

    health = call('/api/health')
    if health['ai'] != 'openai':
        raise RuntimeError('OpenAI deployment is not active; no emails sent.')
    private = root / '.private/openai-live-offer.json'
    if private.exists():
        saved = json.loads(private.read_text())
        if saved.get('request_id') != args.request_id:
            raise RuntimeError('Existing live smoke checkpoint belongs to another request. Archive it explicitly before a new run.')
        offer = saved['offer']
    else:
        offer = call('/api/cases', {'email': args.send_to, 'message': 'I need the appointment to finish by 3 PM.',
            'request_id': args.request_id})
        private.write_text(json.dumps({'request_id': args.request_id, 'offer': offer}), encoding='utf-8')
    if not offer.get('customer_url'):
        raise RuntimeError('Duplicate creation recognized. Use the original private customer link; no send retry performed.')
    fragment = urllib.parse.parse_qs(urllib.parse.urlparse(offer['customer_url']).fragment)
    token = fragment['token'][0]
    path = '/api/cases/' + offer['case']['id']
    current = call(path, token=token)
    cases = [
        ('Add earlier constraint', 'I can only start after noon; keep the finish-by-3-PM requirement.', 'B'),
        ('Impossible window', 'Change my requirement: I must be finished before 8 AM.', None),
        ('Restore valid window', 'Replace earlier timing constraints: start after noon and finish by 3 PM.', 'B')]
    evidence = {'health': health, 'case_id': current['id'], 'checks': [], 'live_provider': 'openai'}
    if current['status'] != 'BOOKED':
        for name, message, expected in cases:
            current = call(path + '/reply', {'message': message, 'version': current['version']}, token)
            actual = current['proposal']['slot_id']
            evidence['checks'].append({'name': name, 'expected': expected, 'actual': actual,
                'proposal': current['proposal'], 'passed': actual == expected})
            if actual != expected:
                (root / 'docs/openai-live-evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
                raise RuntimeError('Live scheduling evaluation failed: ' + name)
        current = call(path + '/confirm', {'slot_id': current['proposal']['slot_id'], 'version': current['version']}, token)
    again = call(path + '/confirm', {'slot_id': current['proposal']['slot_id'], 'version': current['version']}, token)
    evidence.update({'status': current['status'], 'mail': current['mail'],
        'duplicate_event_count_unchanged': len(current['events']) == len(again['events'])})
    (root / 'docs/openai-live-evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
