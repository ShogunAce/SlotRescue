# Live AI access blocker

Checked again October 27, 2026. Amazon Nova Micro in us-east-1:

- GetFoundationModelAvailability: agreement AVAILABLE, authorization AUTHORIZED, entitlement AVAILABLE, region AVAILABLE.
- Actual Converse request (8 output tokens): ValidationException, `Error 002: Access to Bedrock models is not allowed for this account`.
- No successful inference, no AI-enabled deployment, no claim of a completed AI submission.

The account-level runtime restriction remains even though model availability checks succeed. Do not broaden IAM policies, buy provisioned capacity, subscribe to unrelated models, or incur arbitrary AWS usage to try to remove it. An authorized account owner should ask AWS Support to review the restriction.

## Copyable AWS Support case

Subject: Bedrock Error 002 blocks AWS CDS hackathon internal pilot

Our AWS account is building SlotRescue, an internal Try AI Strategies pilot for the AWS CDS Agentic AI Partner Hackathon, due October 28, 2026 at 1 PM PDT. The deployed application uses Lambda, API Gateway, DynamoDB, and verified real SES sends. Bedrock is the remaining runtime blocker.

In us-east-1, GetFoundationModelAvailability for amazon.nova-micro-v1:0 returns agreement AVAILABLE, authorization AUTHORIZED, entitlement AVAILABLE and region AVAILABLE. A minimal bedrock-runtime Converse request with maxTokens=8 fails with ValidationException: Error 002: Access to Bedrock models is not allowed for this account. The same error occurred on October 26 and October 27 Pacific time.

Please investigate the account-level restriction and explain the required remediation. We need only small, on-demand text inference for scheduling preferences, with an eight-turn conversation cap and 180 output tokens per application call. We are not requesting provisioned throughput or a paid support-plan upgrade.

## Unblocking test

Once AWS confirms access, perform one tiny Converse probe. Only after success set AiMode=bedrock in the existing CloudFormation stack, preserving all other parameters. Test the full customer preference/confirmation flow and record the model evidence. Do not silently fall back to rehearsal on model failure.
