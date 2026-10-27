# Submission work package

## Readiness checklist

- [x] New source repository initialized locally; MIT license.
- [x] Deployment and public web URL.
- [x] SES v2 actually called at runtime; offer and confirmation acceptance IDs saved.
- [x] Real demo ledger booking and duplicate protection tested.
- [x] Architecture and setup instructions.
- [ ] Bedrock live inference enabled and tested (currently account-blocked).
- [ ] Partner organization/profile and corporate registration details verified.
- [x] Corrected ACE opportunity created and verified: O30450854 (Pending Submission).
- [x] Required hackathon campaign and USD 5/month estimate verified on the new ACE record. See ACE-STATUS.md.
- [ ] GitHub/GitLab repository published, with judge access.
- [ ] Approximately three-minute real demo footage uploaded publicly to YouTube/Vimeo.
- [ ] Final Devpost submission checked and submitted before deadline.

Deadline: October 28, 2026, 1 PM PDT. Official rules require an eligible AWS Partner entrant, a deployed AI solution with qualifying CDS runtime use, source access, architecture, text, video and ACE opportunity. AgentCore is optional. Maintain judge access until judging closes November 12, 2026. Check the current official rules before final submission.

Sources: https://aws-cds-partner.devpost.com/rules and https://aws-cds-partner.devpost.com/details/faq

## Project fields (draft; update after live AI verification)

**Name:** SlotRescue

**Tagline:** Turn cancelled service appointments into confirmed customer conversations.

**Problem:** Appliance-service cancellations leave technicians idle while waiting customers still need help. Dispatchers spend time calling people whose availability may have changed.

**What it does:** An operator opens a conversation with a waiting customer. Amazon SES sends a private scheduling link. The customer revises their constraints, reviews a proposed window, and explicitly confirms. SlotRescue atomically claims the available demo appointment and sends an SES confirmation. An audit trail distinguishes a proposal, booking, email preview, SES acceptance and uncertain send outcome.

**How it is built:** Python Lambda behind API Gateway, DynamoDB conditional writes, SES v2 SendEmail, and an optional Amazon Bedrock Converse planner. The current deployment uses a labeled rehearsal planner while account model access is resolved; do not omit this qualification until successful live inference is recorded.

**Impact:** The demo measures confirmed recoveries and conversation-to-booking conversion. Future pilots can measure dispatcher time and cancellation fill rates. No measured customer revenue gain is claimed.

**Limitations:** Three demo slots; one test email recipient; no actual technician dispatch; no inbound email parsing; no confirmed inbox-delivery events; shared operator secret; single bounded database aggregate. No WhatsApp prize claim.

**Disclosure:** Built during the hackathon window with AI coding assistance. No pre-existing product source incorporated. Uses Python standard library and the AWS SDK.

## Three-minute recording script

0:00–0:20 — Show an empty appointment window and explain the lost capacity. Introduce the narrow recovery loop.

0:20–0:55 — Create an offer in the deployed operator UI. Show the SES acceptance event and the actual received offer in the approved inbox. Hide operator key and unrelated email.

0:55–1:35 — Open the customer's private link. Change the constraint. Show live Bedrock interpretation only if enabled and verified; otherwise explicitly identify rehearsal and do not submit it as completed AI.

1:35–2:05 — Review the exact time window, click Confirm, and show the ledger transition. Refresh or repeat the request to demonstrate no double booking.

2:05–2:30 — Show the real confirmation email and SES message ID. Explain acceptance versus delivery evidence.

2:30–3:00 — Show architecture, cost controls, test results and remaining production boundaries. End on the confirmed recovery, not a feature list.

## ACE content ready to use

Partner project title: SlotRescue — conversational service appointment recovery

Business problem: Service operators lose capacity to cancelled appointments and manual waiting-list outreach. This new hackathon concept explores an AWS-based offering that uses email and conversational scheduling to recover available appointment windows.

Solution: AWS Lambda/API Gateway application with DynamoDB booking state, SES customer offers and confirmations, and a Bedrock scheduling planner pending account enablement. Initial implementation is a controlled demonstration, not a signed customer deployment.

Campaign: AWS CDS Agentic AI Hackathon -Sept. 2026

Customer, geography, opportunity stage, target date, company details and estimated AWS revenue must come from accurate user information. The FAQ allows concepts without a ready customer deal, but this is not permission to fabricate a company or commitment.
