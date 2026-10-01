# Class 5 use case economics and decision gate

## Decision summary

AccountLens remains a suitable course project because it addresses a repeated account-preparation task with a bounded, evidence-grounded workflow. The prototype demonstrates technical feasibility on synthetic data. A production budget decision would still require lawful source access, an accountable data owner, real signatory labels, measured human fallback cost, and observed operating volume.

The primary Class 5 metric is signatory selection precision on a separate instructor-aligned set of 10 hand-authored fictional accounts. The true signatory is defined as the contact with final commercial approval authority. A procurement or legal contact who only executes paperwork is not the signatory.

## AI opportunity archetype

The core use case is Archetype B because AccountLens manufactures a measurement that is not recorded directly in the source systems: the likely commercial signatory and the surrounding decision chain. Email participation, meeting attendance, budget discussions, procurement activity, tickets, and CRM notes act as observable proxies. The ten-account set provides two email threads with explicit CC lists, one attendee list, two tickets, one CRM note and a known true signatory for every account.

The briefing and activity summarisation functions are an Archetype A subtask because they replace a manual computation that the account manager already performs. The central risk for the Archetype B component is that an estimate may be read as a verified fact. The application therefore labels the output as a likely commercial signatory, shows evidence and confidence, supports abstention, and requires human confirmation.

## Use case intake screen

| Gate | Evidence in the prototype | Decision |
|---|---|---|
| Worth doing | The task occurs before account meetings. The pilot recorded a 40-second median preparation-time difference. The use case buys scale; the same evidence pipeline may support KAM, Presales and Customer Success. It does not have a free learning label. | Pass for a bounded pilot |
| Possible | Synthetic records are accessible, standardised, consistent and quality-controlled. Real Salesforce, email, calendar and ticket data have not passed the five readiness tests. | Prototype pass; production not proven |
| Affordable | Observed variable model cost was USD 0.016065 per briefing. Full production cost depends on failure handling, human review, integration, monitoring and maintenance. | Pass for the prototype; production decision pending |
| Absorbable | A KAM reviews the briefing before a meeting, checks evidence, verifies the signatory and chooses the next action. The system performs no write or outbound action. | Pass for the advisory workflow |
| Killable | Existing technical thresholds and the Class 5 signatory gate define when to stop or re-scope. | Pass for the pilot |

## Data readiness

| Test | Synthetic prototype | Production requirement |
|---|---|---|
| Long | Sixty accounts cover the generator's designed variations. | Historical data must cover different organisations, stages, writing styles and outcomes. |
| Standardised | One schema and one role definition are used. | Source fields and signatory meaning must be reconciled across teams. |
| Quality controlled | Fixed ground truth and deterministic checks are available. | Sales Operations or a named data steward must own corrections and label quality. |
| Consistent | Definitions do not change across the generated dataset. | Data contracts and drift monitoring must detect changes in source meaning. |
| Accessible | Local fictional records are available without personal data. | CRM, email, calendar and ticket access requires lawful permission, provenance and retention controls. |

The weakest production links are lawful access, cross-team consistency, daily data ownership, and independently verified signatory labels. A one-off export does not demonstrate a production data pipeline.

## Build and rent decision

The project rents the model and API infrastructure. It owns the role and signatory definitions, synthetic and future approved data contracts, ground-truth labels, evaluation set, deterministic evidence validation, workflow integration, human-review boundary, and monitoring requirements. A vector database and multi-agent framework remain unnecessary for the one-account exact-filtering task.

AccountLens is a bounded AI-assisted decision workflow rather than a fully autonomous agent. Deterministic code performs filtering, validation, risk checks, aggregation and export. The model performs one structured inference step. This reduces compounded errors and avoids the governance risk created by autonomous writes.

## Signatory evaluation

The evaluator selects the highest-confidence, non-abstained `economic_buyer` prediction for each account and compares its contact ID with `true_signatory_contact_id`.

| System | Accounts | Signatories selected | Correct | Precision | Recall | Selection rate |
|---|---:|---:|---:|---:|---:|---:|
| B0 rules | 10 | 7 | 7 | 1.00 | 0.70 | 0.70 |
| M2 evidence grounded | 10 | 10 | 10 | 1.00 | 1.00 | 1.00 |

Precision alone would make both systems appear equal. Recall and selection rate show that B0 omitted three of the ten true signatories. M2 selected the correct signatory in all ten instructor-aligned fictional accounts. M2 used 25,737 input tokens and 6,159 output tokens, with an estimated variable cost of USD 0.125933 and p95 latency of 8.2823 seconds. This is a supplementary synthetic result, not a claim about real enterprise performance.

## Cost per successful briefing

The project uses the following Class 5 formula:

`variable cost + expected human fallback cost + fixed monthly cost divided by monthly volume`

The frozen 20-account test cost USD 0.321290, or USD 0.016065 per briefing. At that variable-only estimate, a USD 10 balance supports approximately 622 briefings. This number excludes production integration, review, monitoring, maintenance and governance.

| Scenario | Success rate | Human fallback | Fixed cost and volume | Cost per successful briefing | Break-even hourly rate using 40 seconds saved |
|---|---:|---|---|---:|---:|
| Observed prototype variable only | 100% | None | USD 0 at 500 per month | USD 0.0161 | USD 1.45 |
| Low overhead illustration | 95% | 5 min at USD 30 per hour | USD 100 at 500 per month | USD 0.3411 | USD 30.70 |
| Expected illustration | 90% | 10 min at USD 45 per hour | USD 500 at 500 per month | USD 1.7661 | USD 158.95 |
| Conservative illustration | 80% | 20 min at USD 60 per hour | USD 1,500 at 250 per month | USD 10.0161 | USD 901.45 |

The last three rows are sensitivity assumptions, not measured production costs. They show why the model invoice alone cannot support a production budget decision. The production break-even must be recalculated after observing real success rate, review time, loaded labour cost, operating volume and fixed support cost.

## Measurement and stop conditions

The counterfactual is the B0 deterministic rules baseline. The primary Class 5 measure is signatory precision; recall and selection rate prevent omission from being hidden. Role Macro-F1, evidence precision, latency, cost and user-study results remain supporting measures.

The original frozen-test thresholds remain unchanged. The following Class 5 conditions govern a future real-data pilot:

- stop or re-scope if signatory precision is below 0.85 or selection rate is below 0.70 on an independently labelled calibration set;
- stop if evidence precision is below 0.90 or unsupported-claim rate exceeds 0.05;
- stop if p95 generation latency exceeds 15 seconds for the meeting-preparation workflow;
- stop if cost per successful briefing exceeds the measured value of preparation time saved;
- do not start a production pilot if lawful access, source provenance, daily data ownership or a correction workflow is missing.

## Ownership and workflow

The KAM is accountable for using and verifying the briefing. Sales Operations or a named data steward owns role definitions, signatory corrections and data quality. Source-system owners approve access and freshness requirements. Security and Legal approve permissions, retention and audit controls. The AI system remains advisory and cannot send messages, change CRM records or approve a commercial decision.

## Evaluation integrity

`true_signatory_contact_id` is removed explicitly from every model prompt. The ten hand-authored accounts are isolated from the original 60-account dataset and have their own manifest and file hashes. The prompt and ten records were frozen before the one-time M2 evaluation; the original frozen test artifacts remain unchanged.
