# Demonstration and final-video script

The complete spoken narration is in `docs/final_video_narration.md`. This file remains the operational recording checklist and demonstration procedure.

## Recording setup

- Use the local Streamlit app and synthetic data only.
- Hide `.env`, terminals containing secrets, browser bookmarks, and notifications.
- Keep the original title visible at the start.
- Record at 1080p if possible and use a readable browser zoom.
- State that the final metrics come from the already frozen, one-time test run; do not rerun it for the video.

## Demo 1: successful workflow (about 90 seconds)

1. Open AccountLens and select `ACC-001` from the development split.
2. Point out the fixed 30-day window and the fictional-data notice.
3. In **Decision chain**, show the likely commercial signatory, supported candidates, missing roles, confidence, and evidence IDs. State that the signatory is a hypothesis requiring human verification.
4. In **Cross-team intelligence**, show ranked activity from CRM, email, meeting/calendar, and support sources. Mention deterministic risk alerts when present.
5. Exclude one low-relevance event and explain that the excluded item is removed from the generation context.
6. Read the responsible-use statement, tick human confirmation, and generate the briefing.
7. Show one or two next actions, claim-level evidence, and limitations.
8. Download the one-page PDF and Slack-ready Markdown. Explain that the app never sends a message autonomously.

Expected result: an evidence-grounded briefing is produced in under the 15-second project target under normal API conditions, with export controls enabled only after human confirmation.

## Demo 2: calibrated abstention (about 45 seconds)

1. Use `ACC-001` or another development account with an intentionally ambiguous contact.
2. Show the `unknown` or missing-role entry rather than forcing a role assignment.
3. Open its supporting evidence and explain that the confidence threshold is frozen at `0.65`.
4. State that abstention lowers coverage deliberately and is safer than presenting an unsupported stakeholder claim.

Expected result: the interface clearly separates supported candidates from unknown or missing roles and does not draw unsupported relationship edges.

## Demo 3: handled failure (about 45 seconds)

Run this as a separate temporary session so the saved `.env` file is not edited. In a new PowerShell window, set an invalid key only for that window and start Streamlit on port 8502:

```powershell
$env:OPENAI_API_KEY = "invalid-demo-key"
python -m streamlit run app.py --server.port 8502
```

Then:

1. Open `http://localhost:8502`.
2. Confirm the responsible-use boundary and request a briefing.
3. Show the visible error message and that the evidence register and deterministic analysis remain usable.
4. Close that PowerShell window. The temporary environment variable disappears and the saved key remains unchanged.

Expected result: the app reports the generation failure without inventing a briefing, leaking the key, sending a Slack message, or corrupting the frozen artifacts.

## Suggested 4-minute final-video narration

1. **Problem and user (0:00-0:30):** A Key Account Manager has less than 15 minutes to reconstruct a complex buying process from fragmented systems.
2. **Scope and safety (0:30-0:55):** The MVP uses fictional records, an explicit 30-day window, evidence IDs, abstention, and mandatory human confirmation.
3. **Core walkthrough (0:55-2:25):** Run Demo 1 and briefly show the decision chain, cross-team activity, risks, actions, and exports.
4. **Uncertainty and failure (2:25-3:05):** Show the abstention and handled-failure behaviours.
5. **Evaluation and economics (3:05-3:40):** Present the frozen role metrics, the separate 10-account signatory result, and the observed variable cost of USD 0.016065 per briefing. State that full production cost must include human fallback and fixed operating costs.
6. **Limitations and next step (3:40-4:00):** State that relationships are hypotheses, data is synthetic, connectors are out of scope, and the small self-reported pilot should be repeated with a larger externally observed sample.

## Recording checklist

- [ ] Success recording captured.
- [ ] Abstention recording captured.
- [ ] Failure recording captured.
- [ ] No secret, personal data, or unrelated notification is visible.
- [ ] Original project title is visible.
- [ ] Frozen metrics are described accurately.
- [ ] Signatory precision is paired with recall and selection rate.
- [ ] Variable model cost is not presented as full production cost.
- [ ] Limitations and human responsibility are stated.
