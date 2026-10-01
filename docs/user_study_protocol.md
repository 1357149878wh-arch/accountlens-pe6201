# Blinded user-study protocol

> The synthetic pilot in `docs/simulated_user_evaluation.md` is a procedure check only. Five participant-provided completed questionnaires have now been imported separately; see `docs/real_user_evaluation.md`. The import verified completeness but did not independently observe the sessions or verify participant identity.

## Purpose

Measure whether the evidence-grounded AccountLens briefing helps a Key Account Manager prepare more accurately and efficiently than the deterministic non-AI baseline. This protocol evaluates decision support, not autonomous decision making.

## Study design

- Recruit 5 to 8 adults familiar with B2B sales, account management, customer success, or business analysis.
- Use four fictional accounts from the validation split only: `ACC-014`, `ACC-020`, `ACC-040`, and `ACC-058`.
- Prepare two briefings for each account: the frozen B0 rules baseline and the frozen M2 evidence-grounded configuration.
- Remove system names, model names, costs, and generation metadata. Label outputs only as **Briefing A** and **Briefing B**.
- Randomise A/B order independently for each account and participant.
- Use a within-participant design: every participant reviews both systems, but alternate which one is shown first.
- Do not use test accounts, change the prompt, or tune the threshold from study feedback.

Ready-to-use masked packets and the private randomisation key are in `docs/user_study_materials/`. Give each participant only their matching `Pxx_participant_packet.md` file and keep `facilitator_key.md` private until all scores have been recorded.

## Participant notice

All organisations, people, messages, meetings, and tickets in this study are synthetic. The tool can make mistakes and its relationship map is a hypothesis, not a verified reporting structure. Participants should not enter personal, confidential, or employer data. Participation is voluntary; record only anonymous participant codes.

## Session procedure

1. Assign an anonymous code such as `P01`; do not record the participant's name.
2. Read the participant notice and obtain verbal agreement.
3. Explain the six decision roles without describing how either system works.
4. For each fictional account, start a timer and show one masked briefing.
5. Ask the participant to identify the likely buying roles, the two most important current risks, and the next action they would take.
6. Stop the timer when the participant says they are ready for the meeting.
7. Ask the participant to score the briefing using the rubric below.
8. Repeat with the paired briefing, then ask which one they prefer and why.
9. Rotate the order for the next account according to the randomisation sheet.

Target session duration: 20 to 30 minutes per participant.

## Scoring rubric

Use a 1-to-5 scale for each item, where 1 is very poor and 5 is excellent.

| Measure | Participant question | Direction |
|---|---|---|
| Role usefulness | How useful is the role map for preparing the meeting? | Higher is better |
| Evidence trust | How easy is it to verify important claims from cited event IDs? | Higher is better |
| Risk relevance | How relevant are the surfaced risks to the next meeting? | Higher is better |
| Action usefulness | How actionable are the one or two recommended next steps? | Higher is better |
| Clarity | How clear and concise is the briefing? | Higher is better |
| Confidence calibration | Does the briefing clearly show what is uncertain or unknown? | Higher is better |
| Preparation time | Seconds until the participant says they are ready | Lower is better |

## Facilitator recording sheet

| Participant | Account | First shown | B0 time (s) | M2 time (s) | B0 mean rating | M2 mean rating | Preferred | Notes |
|---|---|---:|---:|---:|---:|---:|---|---|
| P01 | ACC-014 | A / B |  |  |  |  | A / B / tie |  |

Keep the private A/B mapping in a separate note until all scoring is finished. Do not reveal it during the session.

## Analysis plan

- Report participant count and relevant experience in aggregate only.
- For each system, report the median preparation time and the median score for each rubric item.
- For paired comparisons, report each participant's M2 minus B0 score and the number preferring each system.
- With a small sample, emphasise descriptive results and individual paired differences; do not claim population-level statistical significance.
- Summarise recurring comments as themes and include at least one negative or mixed theme.
- Record any observed hallucination, unsupported claim, confusing abstention, or inappropriate action recommendation.

## Completion criteria

The checklist item is complete only after at least five real participants have completed the protocol, the blind has been preserved through scoring, and aggregate findings plus limitations have been added to the final report. A prepared protocol alone does not count as a completed user study.

Status: five anonymous completed questionnaires were supplied, decoded after scoring, and reported on 2026-09-22. All forms passed completeness checks. Because participation and timing are self-reported, the result is labelled as a small descriptive pilot rather than independently verified human-subject research.
