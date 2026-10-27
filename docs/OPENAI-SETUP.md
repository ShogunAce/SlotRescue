# OpenAI replacement for blocked Bedrock

The hackathon requires an AI solution deployed on AWS using a qualifying AWS CDS service. Bedrock/AgentCore is recommended, not required. SlotRescue keeps Lambda, API Gateway, DynamoDB and SES, and adds GPT-4.1 mini for scheduling proposals.

## Secret setup

AWS Secrets Manager secret `slotrescue/openai` in us-east-1 is created. The owner must set its value to a JSON object with an `api_key` field containing a funded OpenAI API project's key. Enter it directly in the AWS Console, never in chat or Git. No agent tool should retrieve the value.

CloudFormation resolves `{{resolve:secretsmanager:slotrescue/openai:SecretString:api_key}}` into Lambda's encrypted environment when AiMode=openai. The Lambda role does not receive Secrets Manager read access. Authorized Lambda configuration readers can access environment values; restrict that access. Rotate the key by updating the secret and redeploying the function with a configuration change, as CloudFormation does not automatically refresh dynamic references when a secret rotates.

The secret is billed according to AWS Secrets Manager pricing. Keep it only as long as needed; remove it separately after final teardown if no longer used.

## Activate

After the owner confirms saving the key, check only DescribeSecret's version metadata, not its value. Rebuild template.json, validate it, and update the existing stack with AiMode=openai, OpenAiSecretName=slotrescue/openai, and OpenAiModel=gpt-4.1-mini. Preserve other parameters. Wait for UPDATE_COMPLETE.

Use a small direct Lambda invocation through the customer-reply route for model validation against an existing unbooked case, or create one fresh controlled demo offer. Verify response engine=openai, inference request ID, selected slot, and token usage. Test historical constraints, ambiguity and an impossible window; then exercise the full SES offer-to-confirmation loop. Record actual outputs in a separate evidence file. Mock tests are not proof of successful live inference.

## Request boundary

The standard-library HTTPS adapter calls only https://api.openai.com/v1/chat/completions with store=false, temperature=0 and max_completion_tokens=180. Structured output is required. It includes current inventory and at most the application's eight-turn history, not recipient addresses, bearer tokens or operator credentials. Model refusals, truncation, timeouts, API errors and invalid slot identifiers fail closed. There is no silent fixture fallback.

Source documentation:
- https://developers.openai.com/api/docs/models/gpt-4.1-mini
- https://developers.openai.com/api/docs/guides/structured-outputs
- https://aws-cds-partner.devpost.com/details/faq
