# SlotRescue

Recover cancelled appliance-service appointments through a conversation: SES email → private customer page → preference update → explicit confirmation → atomic booking → SES confirmation.

**Live demo:** https://tidx9k8p3g.execute-api.us-east-1.amazonaws.com/

**Public source:** https://github.com/ShogunAce/SlotRescue

## Verified status

- Deployed on AWS, `us-east-1`, stack `slotrescue-demo`.
- Real SES offer and confirmation accepted by AWS during an end-to-end HTTP test. See [evidence](docs/live-evidence.json). Acceptance is not inbox delivery.
- Twenty-two local workflow and AI/AWS adapter contract tests pass; JavaScript syntax checked; deployed page visually inspected. Adapter tests use fake responses and do not prove live model inference.
- **Live AI verified:** OpenAI GPT-4.1 mini is active on the deployed AWS application. Real inference preserved prior constraints, declined an impossible window, and selected the correct slot after a changed preference. The complete loop booked the slot and obtained SES acceptance IDs for both emails. See [live AI evidence](docs/openai-live-evidence.json). Bedrock remains an optional, account-blocked adapter.
- Booking changes a demo service ledger, not an external dispatch system. Customer replies arrive through the secure web page, not inbound email.
- Corrected ACE opportunity O30450854 is created with the required campaign and a verified USD 5/month estimate. Its review status is Pending Submission. Partner eligibility details and the public demo video remain submission gates; see [submission checklist](docs/SUBMISSION.md).

## Run locally (zero AWS calls)

Python 3.11+; no dependencies needed for rehearsal.

```powershell
python app.py
```

Open http://localhost:8765. Operator key: `local-demo-key`. Enter any well-formed email and `any time`. Open the customer link; reply `after 3 pm`; confirm. All emails are previews locally. Local state persists in `slotrescue.db`.

```powershell
python -m unittest discover -s tests -v
python scripts/build_template.py
```

The deployed operator key is in `.private/operator-key.txt` on the build machine; it is excluded from Git. Share it privately with judges. Never commit credentials or live customer links. This bounded demo uses a shared operator secret, not a production identity system.

## Deploy to your AWS account

Prerequisites: AWS CLI credentials with CloudFormation/IAM/Lambda/API Gateway/DynamoDB/Logs access; verified SES sender and recipient in the SAME region. SES sandbox is sufficient for a controlled test. For OpenAI, store a funded API key as described in [OpenAI setup](docs/OPENAI-SETUP.md). Lambda supplies boto3; no dependency download is needed for this template.

```powershell
python scripts/build_template.py
# Use a random operator secret of at least 24 characters. Keep parameters.json private.
# See scripts/parameters.example.json for the required keys.
aws cloudformation validate-template --template-body file://template.json --region us-east-1
aws cloudformation create-stack --stack-name slotrescue-demo --template-body file://template.json --parameters file://.private/parameters.json --capabilities CAPABILITY_IAM --region us-east-1
aws cloudformation wait stack-create-complete --stack-name slotrescue-demo --region us-east-1
aws cloudformation describe-stacks --stack-name slotrescue-demo --query 'Stacks[0].Outputs' --region us-east-1
```

On later changes regenerate `template.json`, then use `update-stack` with the same parameters and `CAPABILITY_IAM`. Wait for `stack-update-complete`. Keep the operator key unchanged unless deliberately rotating it. `MailMode=ses` performs real sends; `preview` does not. `AiMode=openai` uses GPT-4.1 mini and an AWS Secrets Manager dynamic reference; `bedrock` calls `amazon.nova-micro-v1:0`; `rehearsal` matches only four fixture phrases and is explicitly labeled. There is no silent AI fallback.

Check `/api/health` after deployment. Create a fresh offer, follow the email, change a preference, confirm, inspect the ledger and mail message IDs, then repeat confirmation to prove idempotency. Live OpenAI tests cover historical constraints and impossible windows; prompt-injection robustness still needs broader evaluation.

## Architecture and boundaries

See [architecture](docs/ARCHITECTURE.md), [execution specification](docs/EXECUTION_SPEC.md), and [decision memo](docs/DECISION.md).

The HTTP API serves the HTML and API from one origin. Lambda uses a single DynamoDB item with conditional revision writes to keep the small demo's slot claims atomic. At most 20 cases and eight customer turns per case; 48-hour customer links; 500-character messages; 180-token model responses; API throttling at 2 requests/sec with burst 5; seven-day log retention; no VPC/NAT, provisioned compute, phone numbers or always-on database.

SES permissions are restricted to the configured sender and one test recipient. Links keep their bearer token in the URL fragment and send it in a header; token hashes are stored, pages use no third-party assets, and responses disallow caching/referrer forwarding. Operator access is required to create offers/read the ledger. Logs include exception types, not message bodies or credentials.

The single-item store is intentionally bounded, not a scalable multi-tenant architecture. A production version needs Cognito/OIDC, per-tenant records, transactional booking inventory, queue-backed outbox, deliverability events, consent/unsubscribe handling, audit retention, and a real scheduling adapter. SES has no send-email idempotency token: an uncertain outcome is retained for manual reconciliation, never automatically resent. A crash before the send can leave an unsent intent; a crash after booking can leave confirmation unsent. Booking state remains authoritative.

## Cost and teardown

This is a small usage-based deployment, not a guaranteed-free service. Current AWS pricing and account credits determine charges. Rate limits and per-case limits reduce use but are **not a dollar cap**. Stop at a small manual demo cohort; review Billing before expanding. Keep access working through judging if submitting. Export evidence, then delete only the dedicated stack when no longer needed:

```powershell
aws cloudformation delete-stack --stack-name slotrescue-demo --region us-east-1
aws cloudformation wait stack-delete-complete --stack-name slotrescue-demo --region us-east-1
```

Deleting the stack deletes the demo ledger and logs. The verified SES identity was created separately and remains. It has no reserved sending infrastructure.

## Original work and license

New project built during the 2026 hackathon window with AI coding assistance. Python standard library, AWS SDK supplied by Lambda, and AWS managed services are used. No previous application code, stock images, or music included. MIT license.
