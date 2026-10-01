# Statement alignment

## Project identity

The retained title is **Enterprise Account Decision-Chain Mapping & Cross-Team Intelligence Aggregation Assistant**. `AccountLens` is only the short product name used in code and interface labels.

## Primary user and moment of use

The primary user is a Key Account Manager who has less than 15 minutes to prepare for an enterprise customer meeting and cannot manually inspect every CRM note, email, meeting record, calendar item, and support ticket. Sales Directors, Presales Engineers, and Customer Success Managers are secondary consumers of the briefing.

The working change is concrete: instead of reconstructing the account from siloed records, the user reviews one Account Panorama Briefing, verifies the evidence and relationship hypotheses, and enters the meeting with a supported view of the buying workflow, recent activity, risks, and next actions.

## Requirement-to-implementation map

| Statement commitment | Implementation | Status |
|---|---|---|
| Enterprise account as the unit of analysis | One selected account drives contacts, events, roles, risks, actions, and exports | Complete |
| Decision-role inference | Six-class structured prediction with confidence, abstention, evidence validation, and a rules baseline | Complete |
| True commercial signatory | A separate 10-account set records `true_signatory_contact_id`; M2 is scored with a separate account-level metric | Complete on instructor-aligned fictional data |
| Decision-chain mapping | Candidate nodes, missing-role detection, and evidence-linked workflow hypotheses rendered as a graph | Complete, human confirmation required |
| Cross-team intelligence aggregation | Events grouped across Sales, Presales, Customer Success, Product, and Marketing | Complete |
| Past 30 days | Inclusive rolling 30-day filter based on the reproducible dataset reference date | Complete |
| Risk alerts | Deterministic detection of unresolved tickets, unanswered emails, and explicit competitor signals, plus AI-supported risks | Complete |
| One or two action recommendations | Dashboard and exports intentionally display at most two actions | Complete |
| Response under 15 seconds | Frozen test p95 latency was 8.1254 seconds | Complete on synthetic test |
| One-page PDF | Local A4 Account Panorama export, verified as one page | Complete |
| Web dashboard | Streamlit interface with four task-oriented tabs | Complete |
| Slack Bot | Slack-ready Markdown can be downloaded, but the assistant does not post messages | Partial by design |
| CRM, Outlook, Jira/Zendesk and calendar | Synthetic records reproduce the common fields and channels; no live credentials or personal data are used | Simulated, not live |
| Instructor requested data fallback | 10 hand-authored accounts, each with two email threads and CC lists, one attendee list, two tickets, one CRM note and a true signatory | Complete |
| SSO and role-based access | Production authentication is not implemented | Out of scope |
| Class 4 workflow classification | A deterministic orchestrator performs filtering, one structured inference, validation, aggregation, mapping and export. The model does not choose tools or control a variable loop. | Workflow, deliberately not a full agent |
| Pinecone/vector retrieval | Exact account filtering is sufficient for 60 synthetic accounts; adding a vector store would add cost and failure modes without evaluation benefit | Explicitly not selected |
| Observability and evaluation | Metadata-only logs, token/cost/latency measurement, frozen splits, rules baseline, M1/M2/H1 experiments and a one-time test run | Complete |
| Meeting-preparation usability | Five-person blinded B0/M2 pilot on validation accounts; 20 paired comparisons with descriptive reporting | Complete for pilot scope |
| PDPA-conscious handling | Fictional data only, hidden raw content by default, `store=False`, metadata-only logs, and no outbound action | Complete for demo scope |

## Build-versus-buy decision

- **Rent:** the `openai/gpt-4o` model through OpenRouter and the OpenAI-compatible SDK.
- **Build:** synthetic data generator, deterministic baseline, evidence validator, orchestration, decision-chain mapping, risk rules, evaluation, Streamlit dashboard, and export layer.
- **Do not add:** Pinecone, LangChain, autonomous agents, or live system connectors because exact per-account retrieval is adequate at this scale and the extra components would add cost, latency, security exposure, and failure modes without improving the measured objective.

## Class 5 position

- **Archetype:** the core signatory and decision-chain inference is Archetype B because it manufactures a measurement from observable proxies and a calibration set. Briefing summarisation is an Archetype A subtask.
- **Value:** the use case buys scale and may buy scope across KAM, Presales and Customer Success. It does not receive a free correct label, so it does not claim a learning flywheel.
- **Cost:** the observed variable cost is reported separately from human fallback and fixed operating costs. Production affordability remains unproven until those costs and real volume are measured.
- **Absorption:** a KAM reviews the evidence and verifies the likely signatory before a meeting. No autonomous write or outbound action is permitted.
- **Kill condition:** a future real-data pilot stops or re-scopes if signatory precision is below 0.85, selection rate below 0.70, evidence precision below 0.90, p95 latency above 15 seconds, or full cost exceeds the measured value of time saved.

## Classes 1 to 4 position

- **Class 1:** the output requires generated language and structured classification; limited fictional labels support evaluation rather than production training. The cost of a wrong signatory is controlled through evidence, abstention and human verification.
- **Class 2:** the project maps all seven stack layers, owns data/orchestration/evaluation/governance, rents compute and the model, and deliberately avoids a vector store because exact account filtering is sufficient.
- **Class 3:** structured output, schema validation, a frozen evaluation process, L1 checks, a small human L2 pilot and token/cost logging replace subjective prompt judgement.
- **Class 4:** AccountLens is not a full agent. Its code path is predetermined, the model does not choose tools, and there is no variable thought-action-observation loop or autonomous write.

## Responsible-use controls

| Risk | Implemented mitigation |
|---|---|
| Wrong role inference redirects sales effort | Confidence, abstention, evidence IDs, deterministic validation, missing-role flags, and mandatory human confirmation |
| Workflow edge is mistaken for a verified power relationship | Every edge is labelled `workflow_hypothesis`; interface and PDF repeat the limitation |
| Prompt injection in account records | System prompt treats all records as untrusted data; adversarial examples are included in the synthetic set |
| Over-reliance | Advisory-only boundary; no automated outreach or CRM modification |
| Sensitive raw data exposure | Fictional dataset, raw content collapsed by default, metadata-only logs, no stored API output |
| Information overload | Ranked team activity, concise tables, one or two actions, and one-page export |
| Silent API or parsing failure | Structured output validation, retries, visible failure messages, and logged error type |

## Evaluation integrity

The model, prompt, and threshold were frozen before the test split was run once. The decision-chain visualisation, 30-day operational filter, deterministic risk rules, and export layer were added afterward without modifying the saved model result. They therefore improve Statement alignment without retroactively changing the reported role-classification metrics.

The perfect synthetic test result is not presented as real-world performance. The dataset is small, balanced, and generated from repeated patterns. A five-person blinded pilot provides directional meeting-preparation evidence: M2 was preferred in 20/20 comparisons, with median time 21.6% lower and median mean rating 1.67 points higher than B0. Because the accounts are fictional and the participant-provided responses are small and highly uniform, external cases, independent annotation, a larger observed user study, production authentication, and live connector testing remain necessary before any production claim.
