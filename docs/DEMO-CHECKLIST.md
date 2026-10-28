# SlotRescue: test and recording checklist

Landing: https://tidx9k8p3g.execute-api.us-east-1.amazonaws.com/

Judge workspace: https://tidx9k8p3g.execute-api.us-east-1.amazonaws.com/workspace

Operator: https://tidx9k8p3g.execute-api.us-east-1.amazonaws.com/operator

Source: https://github.com/ShogunAce/SlotRescue

## Start here

- [ ] Use a normal Chrome window at 100% zoom. Reload after the image update; Ctrl+Shift+R forces a fresh load.
- [ ] Close unrelated tabs and hide the bookmarks bar before recording. Enable Do Not Disturb and check microphone audio.
- [ ] Keep the operator key and private customer URLs off camera. Never publish the key or the URL fragment containing the customer token.
- [ ] Rehearse in the public workspace. It has fresh isolated inventory and sends no emails.
- [ ] Reserve the protected operator's last available slot for the real SES recording. At last verification, A (9–11 AM) was available; B and C were booked. Refresh its ledger before relying on this.

## Public workspace: one complete test (about 4 minutes)

| Check | Action / exact input | Expected result |
|---|---|---|
| Landing image | Open the homepage and scroll to the hero | Kitchen/appliance visible; image sharp; offer card and caption readable |
| Navigation | Click “See it in action” or “Try the workspace” | Workspace opens without a password or sign-in |
| Start | Click “Start a fresh workspace” if continuing a previous session. Enter `A morning appointment, please.` and Start | Morning, 9–11 AM proposal; offer email marked preview only |
| Change preference | Send `Replace all earlier time constraints: I need an afternoon appointment that finishes by 3 PM.` | Afternoon, 1–3 PM proposal |
| Preserve constraints | Send `It also needs to start after noon.` | Still 1–3 PM; earlier finish-by-3 constraint preserved |
| Impossible request | Send `I also need the entire appointment to finish before 8 AM.` | No valid window; useful explanation; no Confirm button |
| Recover | Send `Replace all previous time constraints: a 1–3 PM appointment works for me.` | 1–3 PM proposal and Confirm button return |
| Explicit confirmation | Click “Confirm this appointment” once | Confirmation popup opens. Click View my appointment: focus moves to the appointment card with date, time, zone and booking reference; reply form hidden |
| Email evidence | Read the visible Appointment offer and Booking confirmation previews | Both explicitly say preview only; no claim that email was sent |
| AI evidence | Read The AI decision, then expand “Technical details” (raw JSON is under “View raw JSON”) | BOOKED; engine openai; model/request ID; PREVIEW_ONLY mail statuses |
| Persistence | Refresh, or go to homepage and return in the same tab | Same confirmed card returns with “Restored from the server.” Click Verify saved appointment for a fresh server read; no extra booking |
| Restart | Click “Start a fresh workspace,” then Start | Fresh case and all three windows available again |
| Independence | Open an incognito window and start another session | Separate schedule; no other visitor's conversation visible |

Use fictional scheduling details. Eight messages maximum per conversation, including the first. Restart for another scenario. Public sessions expire after 24 hours. All visitors share a limit of 80 starts and 150 AI requests per UTC day; avoid repeated rapid testing.

## Additional checks (separate fresh sessions)

- [ ] **Ambiguous input:** `I might be free, but I don't know when.` Expect a clarification rather than a claimed booking. Exact model wording can vary.
- [ ] **Invalid input:** Try submitting an empty preference. The UI/server should reject it. Text fields cap input at 500 characters.
- [ ] **Busy state:** While a request is running, action buttons disable. One click should create one action.
- [ ] **No fake booking:** A proposal alone leaves the slot unbooked. Confirmation is required.
- [ ] **Small screen:** Narrow the browser or open on a phone. Cards stack, text stays readable, buttons remain usable, and no horizontal scrolling is needed.
- [ ] **Keyboard:** Tab through links/forms/buttons; visible focus; Enter submits a valid form; details expand with keyboard activation.
- [ ] **Reduced motion:** With reduced motion enabled in the OS/browser, content remains visible and usable without scroll animation.
- [ ] **Access control:** Open `/operator` without entering a key and click Refresh ledger. It should ask for the key and show no private ledger data.
- [ ] **Error honesty:** If the AI/network fails, the UI should show an error, not pretend the appointment was confirmed. Refresh to inspect saved state before retrying a confirmation.

## Real SES loop: perform once when ready to record

This is the protected workflow, separate from public previews. Do not repeatedly create or confirm cases: the operator ledger has finite inventory.

1. Open `/operator`. Enter the key from `.private/operator-key.txt` privately. Enter `coleslaysolutions@gmail.com`, the configured verified test recipient.
2. Refresh the ledger. Verify a slot is available. Use that slot's actual date and window in the recording.
3. Start an offer with `A morning appointment that finishes by 11 AM, please.` Only proceed if the morning window is available.
4. Inspect the offer status. `ACCEPTED_BY_SES` and a message ID mean AWS accepted the send; they do not prove inbox delivery.
5. Check the approved Gmail inbox/spam folder yourself. If the message arrives, show only the relevant message, with unrelated mail hidden. If it does not arrive, say “SES accepted the request; inbox delivery is not confirmed.” Do not claim delivery.
6. Open the private customer link, or use “Open customer experience” if needed. Hide the address bar/token when recording.
7. Send `I also need to finish before 8 AM.` Show the no-match response. Then send `Replace all previous time constraints: 9–11 AM works for me.`
8. Review the date and time, then confirm. This consumes the operator's available slot. Show BOOKED and the confirmation's SES acceptance ID.
9. Check the confirmation email. Refresh the customer page and operator ledger: the booking should remain single, not duplicate.

There is no built-in operator inventory reset. Once the last slot is booked, use the public workspace for additional rehearsals. Keep the recorded evidence.

## Three-minute demo outline

| Time | Show | Say |
|---|---|---|
| 0:00–0:20 | Landing and hero | “A cancelled service appointment leaves unused capacity. SlotRescue turns that opening into a conversation.” |
| 0:20–0:50 | Protected operator offer; SES status; received email if available | “Amazon SES sends the invitation at runtime. The customer continues through a private scheduling link.” |
| 0:50–1:35 | Customer constraints, impossible request, replacement preference | “The AI keeps the customer's constraints, checks available windows, and asks for clarification when none fit.” |
| 1:35–2:10 | Confirm; ledger; confirmation email/status | “Only an explicit confirmation claims the slot. The ledger prevents double booking, and SES handles the confirmation.” |
| 2:10–2:35 | Public workspace and Restart | “Judges can try live AI without signing in. Each session has its own schedule; public emails are clearly labeled previews.” |
| 2:35–3:00 | Architecture/source and final result | “Lambda runs the workflow, DynamoDB records the booking, and SES closes the communication loop. This is a demo ledger, not a real technician dispatch.” |

## Before submission

- [ ] Record a clean, approximately three-minute walkthrough. Check that playback is audible and legible.
- [ ] Upload the video to the required public video host and test the link in incognito.
- [ ] Include landing URL, `/workspace` judge URL, GitHub, architecture, and video.
- [ ] Use corrected ACE opportunity **O30450854**. Confirm partner/corporate registration details match the entrant.
- [ ] Review the Devpost fields and submit by **October 28, 2026, 1 PM PDT**. Save the submission confirmation.
- [ ] Keep the demo available through judging. Do not publish the operator key.

## Claims to keep precise

Live AI: OpenAI GPT-4.1 mini. AWS runtime: Lambda, API Gateway, DynamoDB, SES. Bedrock is optional and blocked in this account, so do not claim it powers the live demo. Public workspace emails are previews; protected operator emails use SES. Bookings are demonstrative and dispatch no real technician. Customer conversation is on the web page; inbound email replies are not ingested. No measured customer revenue or recovery-rate improvement is claimed.
