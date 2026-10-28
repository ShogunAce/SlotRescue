# Architecture

```mermaid
flowchart LR
 O[Operator + private key] --> API[API Gateway HTTP API]
 J[Judge: no sign-in workspace] --> API
 API --> L[Lambda: validate, plan, confirm]
 L --> D[(DynamoDB: cases + inventory + audit)]
 L --> B[OpenAI structured scheduling planner]
 L --> S[SES v2 SendEmail]
 S --> E[Customer inbox]
 E --> W[Private web link]
 W --> API
 L --> C[CloudWatch: bounded logs]
 L --> P[Public session: email preview only]
 L --> F[Private S3: same-origin design assets]
```

```mermaid
sequenceDiagram
 participant O as Operator
 participant A as App on AWS
 participant D as DynamoDB
 participant S as SES
 participant U as Customer
 O->>A: Create offer + idempotency key
 A->>A: Plan against available inventory
 A->>D: Conditional save case and send intent
 A->>S: SendEmail offer
 S-->>A: SES message ID (acceptance only)
 A->>D: Record result
 U->>A: Open private link, revise constraints
 A->>D: Save revised proposal and version
 U->>A: Confirm slot + proposal version
 A->>D: Atomic claim, mark booked
 A->>S: SendEmail confirmation
 A->>D: Record result and audit event
```

The LLM proposes only a slot identifier and a reason. The application checks that the identifier is currently available; the customer sees the actual date and full time window and must explicitly confirm. The LLM has no email, database or booking credentials. Model-generated content is rendered as text. Invalid JSON fails closed; unavailable slots become clarification requests. Rehearsal mode is a fixture planner, not AI.

Consistency: each public session has a separate versioned record and fresh inventory. Original operator cases share the existing operator record. Compare-and-swap rejects concurrent writes within a record. This trades throughput for simple correctness at hackathon scale. The state is capped below DynamoDB's item limit. Concurrent customers cannot claim the same slot. Slot proposals are not reservations.

Public access: a server-signed 24-hour session isolates the judge workspace. It reuses the planner and booking service but returns email previews unconditionally; it cannot invoke SES. A daily quota record reserves each planner call before inference (150/day), with 80 starts/day and 8 messages/session. Public records have a seven-day TTL. See [public workspace](PUBLIC-WORKSPACE.md).

Delivery: persist SENDING_OR_UNKNOWN before invoking SES with SDK retries disabled. Persist ACCEPTED_BY_SES plus message ID only after an SDK response. Preserve FAILED_OR_UNKNOWN on an exception. No automatic retries of uncertain sends. Actual delivery/bounce webhooks are not implemented.
