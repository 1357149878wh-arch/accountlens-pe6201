# Final demonstration narration

> This is a four-minute working script based on the available project evidence. The exact duration and submission format must be updated if the official Final Project Rubric specifies different requirements.

## 0:00 to 0:30 Problem and user

Enterprise Account Decision-Chain Mapping and Cross-Team Intelligence Aggregation Assistant, presented as AccountLens, is designed for a Key Account Manager who has less than 15 minutes to prepare for a complex customer meeting. Important evidence may be scattered across CRM notes, email, meetings, calendar records and support tickets. The problem is not simply summarisation. The user needs to understand who influences the decision, what changed recently, which risks matter and what action should happen next.

## 0:30 to 0:55 Scope and responsible use

This prototype uses only fictional data. It examines one account and an explicit 30-day window. Decision roles and workflow links are hypotheses, not verified reporting relationships. The system shows evidence IDs, can abstain when evidence is insufficient and requires human confirmation before AI generation or export. It never sends a message or changes a source system autonomously.

Using the Class 4 definition, this is an AI-assisted workflow rather than a full agent. Application code fixes the sequence, the model performs one structured inference, and there is no model-directed tool loop or autonomous write. This is deliberate: the course recommends the lowest rung that can complete the task because extra steps compound errors, latency and cost.

## 0:55 to 1:35 Account and decision chain

I will select one fictional enterprise account. The Decision Chain view shows the likely commercial signatory and candidates for the champion, technical evaluator, procurement or legal role and end user. The signatory is the person inferred to hold final commercial approval authority, not necessarily the contact who executes the paperwork. Confidence and evidence IDs are visible, while unsupported contacts remain unknown and missing roles are highlighted.

## 1:35 to 2:10 Cross-team intelligence and risks

The Cross-Team Intelligence view ranks recent activity from Sales, Presales, Customer Success, Product and Marketing. Deterministic checks identify unresolved support tickets, unanswered email and explicit competitor signals. A user can exclude an irrelevant record before generation. The briefing then presents only one or two recommended next actions so the output remains useful in a time-constrained meeting-preparation workflow.

## 2:10 to 2:35 Generation and exports

After I confirm the responsible-use boundary, AccountLens generates an evidence-grounded briefing. Each important claim must reference valid source events. Invalid evidence causes validation and retry handling rather than silent acceptance. The result can be downloaded as a one-page PDF or Slack-ready Markdown, but the user remains responsible for checking the content and deciding whether to share it.

## 2:35 to 2:55 Abstention and failure

For an ambiguous contact, the system returns unknown or a missing-role warning rather than forcing a confident label. In a separate failure demonstration, an invalid temporary API key produces a visible error while the evidence register and deterministic analysis remain available. The system does not invent a successful briefing or expose the saved credential.

## 2:55 to 3:35 Evaluation and economics

The final M2 configuration was frozen before the test split was run once. On 20 synthetic test accounts and 120 role labels, M2 achieved 1.000 accuracy and Macro-F1, 0.833 coverage, 1.000 evidence precision and 1.000 critical-event recall. I then evaluated the frozen prompt on a separate instructor-aligned set of 10 hand-authored fictional accounts. Each contains two email threads with CC lists, one meeting attendee list, two tickets and a labelled true signatory. M2 selected all 10 signatories correctly, so precision, recall and selection rate were 1.000. The rules baseline selected seven correctly but omitted three, so its precision was 1.000 while recall and selection rate were 0.700. The ten model calls cost an estimated 0.126 US dollars.

Observed variable model cost was USD 0.016065 per test briefing, so a USD 10 balance represents about 622 briefings at that rate. This is not a production price. Human fallback, integration, monitoring, maintenance and governance must be added before a budget decision.

## 3:35 to 3:52 Blinded pilot

Five anonymous participants completed a blinded comparison using four fictional validation accounts. Across 20 paired comparisons, M2 was preferred 20 times. Median preparation time fell from 185 to 145 seconds, a 21.6 percent reduction, and the median six-item mean rating increased from 2.83 to 4.50. Participants valued named decision roles, evidence links and clearer next actions, while still saying that role authority must be verified.

## 3:52 to 4:00 Limitations and conclusion

These results are directional, not production proof. The data is synthetic and the user sample is small, self-reported and highly uniform. A production version would require external data, a larger observed study, authentication, connector permissions, privacy review and monitoring. Within the course-project scope, AccountLens demonstrates a working, measurable and human-controlled approach to enterprise meeting preparation.

## Recording completion checklist

- [ ] Capture the successful workflow.
- [ ] Capture calibrated abstention.
- [ ] Capture handled API failure in a temporary session.
- [ ] Show the frozen test metrics and blinded-pilot results.
- [ ] Show signatory precision with recall and selection rate.
- [ ] Distinguish variable API cost from full cost to serve.
- [ ] Keep the API key, personal data and unrelated notifications out of frame.
- [ ] Confirm the official video duration and submission format before final export.
