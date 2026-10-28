# Public judge workspace

The homepage describes the implemented product. `/workspace` opens without an account or operator key. `/operator` retains protected SES sending and the existing operator ledger. Original customer links at `/#case=...&token=...` still work.

## Try it

1. Open `/workspace` and start with a morning preference.
2. Change to an afternoon that finishes by 3 PM: expect B, 1–3 PM.
3. Add “the entire appointment must finish before 8 AM”: expect “No matching window yet” and no confirm button.
4. Explicitly replace previous constraints with an afternoon ending by 3 PM.
5. Confirm. The isolated ledger claims B and produces a confirmation **preview**.
6. Start a fresh workspace to try again. No other visitor’s inventory is changed.

This runs the same planner and booking service as the operator path. Public email steps always bypass SES and return `PREVIEW_ONLY`, even when the deployment uses `MAIL_MODE=ses`. The user-facing UI labels this distinction. The public workspace does not collect an email address.

## The AI decision panel

The panel under the email previews explains each proposal in plain language:

- A recommendation card with the chosen window, or “No matching window yet” when nothing fits.
- The AI’s reason, then three steps: what you said, what was checked, and whose move it is. Nothing is reserved until you confirm.
- “Windows considered” lists each window’s factual state (selected, open, or already booked). It does not invent per-window reasoning the model did not return.
- “How the recommendation changed” appears once a proposal has been replanned.
- “Technical details” shows decision engine, model version, request ID (with a Copy button), token usage and conversation version. Raw JSON is under “View raw JSON (for developers)”.
- A “Start a fresh workspace” button resets the session without scrolling back up.

## Isolation and cost controls

- A server-issued, HMAC-signed random session expires in 24 hours. It is carried in `X-Demo-Session`, not a URL.
- Each session gets its own DynamoDB item, three slots, and a hashed customer bearer token. The session secret and token remain in tab-scoped sessionStorage. Restart drops the browser reference and creates a new session only on the next Start action.
- Sessions and daily quota records have a seven-day DynamoDB TTL. Expired sessions are rejected independently of eventual TTL deletion.
- A shared per-UTC-day CAS-protected budget permits 80 session starts and 150 planner calls. Reservations occur before inference; errors still count. These are usage controls, not a guarantee of total dollar spend.
- Eight messages per case; 500 characters per message; 180 completion tokens; no silent model fallback. Failed quota checks return a clear 429 response.
- API Gateway permits 4 requests/second, burst 12, including assets. Public quotas can be exhausted by abuse; production needs stronger controls.
- Operator authentication, fixed SES recipient, original inventory and previous evidence are preserved.

## Static assets

The build uses local, same-origin assets from a private encrypted S3 bucket through an allowlisted Lambda `/assets/` route. No signed generation URL is embedded. Upload the files in `assets/` after stack creation; see README. The CloudFormation inline source is losslessly compressed to remain below the inline template size limit; the readable source remains `app.py` and `index.html`.

The site is responsive and honors reduced motion. Public preview content and AI output are escaped before rendering. The ordinary operator/customer UI shares the updated typography and visual system.

## Confirmation experience

A successful confirmation opens an accessible modal only after the server returns BOOKED. View my appointment (or Escape) closes it and focuses the appointment card. The card shows the window, date, Pacific time zone, reference and saved state. Email previews and a readable AI explanation remain visible, while the original recovery timeline stays in place. Verify saved appointment performs a fresh server read; refreshing the tab restores the booking with an explicit restoration message. The workspace header omits its redundant Try the workspace link.
