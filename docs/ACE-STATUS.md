# ACE verification — October 27, 2026

Opportunity ID: **O30427665**

Title: SlotRescue — internal pilot for conversational appointment recovery

Organization/customer: Try AI Strategies (internal pilot, as confirmed by the user).

Created: October 27, 2026 UTC (October 26 Pacific). This is within the competition's submission window.

API review status: Submitted. Console status: Pending approval. Stage: Prospect.

The user completed the wizard outside the agent's interrupted sequence. This record was discovered by ListOpportunities and verified by GetOpportunity; the agent did not create a duplicate.

## Outstanding corrections

- Marketing.Source is Marketing Activity, but Marketing.CampaignName was absent from GetOpportunity. The exact required campaign still needs to be added and verified: `AWS CDS Agentic AI Hackathon -Sept. 2026`.
- Estimated AWS monthly usage is approximately $1,268 (console $1,268.41), which is much higher than the intended small pilot. The user explicitly approved correcting it to a $5/month planning estimate. This estimate is not an AWS spending commitment or a billing limit.
- Existing target date is November 11, 2026. Preserve it unless the user asks to change it.
- The user explicitly approved a fresh-read/full-preservation update adding the campaign and adjusting the estimate to $5/month. The authorized update was attempted on October 27. AWS rejected it with `ACTION_NOT_PERMITTED: The opportunity cannot be modified in Submitted, Rejected or In review status.` No mutation occurred. Authorization persists; do not ask for the same approval again when the record becomes editable.

Do not mark the ACE campaign requirement complete based solely on this opportunity ID.

## Correction request for AWS Partner Central support

Please unlock or correct opportunity O30427665, titled "SlotRescue — internal pilot for conversational appointment recovery," for Try AI Strategies. It is currently Submitted / Pending approval, so UpdateOpportunity rejects changes with ACTION_NOT_PERMITTED.

The owner has authorized exactly these corrections:

1. Set Marketing campaign to `AWS CDS Agentic AI Hackathon -Sept. 2026`.
2. Set estimated monthly AWS customer spend to USD 5, reflecting a small internal pilot planning estimate, not a customer contract or spending commitment.

Preserve the existing customer, project description, target close date, ownership and other fields. This correction is needed for the AWS CDS hackathon submission deadline of October 28, 2026 at 1 PM PDT. Please advise how to correct the record while it is pending review, without creating a duplicate opportunity.

This request is prepared but has not been sent to support.
