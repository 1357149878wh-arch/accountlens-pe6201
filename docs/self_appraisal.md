# Self-appraisal draft

## Project contribution

I designed and implemented **Enterprise Account Decision-Chain Mapping & Cross-Team Intelligence Aggregation Assistant**, presented in the interface as AccountLens. The project turns fragmented fictional CRM, email, calendar/meeting, and support-ticket records into an evidence-grounded account briefing for a Key Account Manager. My work covers problem framing, schema design, synthetic data generation, a deterministic baseline, model integration, evidence validation, evaluation, a human-reviewable dashboard, and PDF/Slack-ready exports.

## What worked well

The strongest part of the project is the alignment between the problem statement and the operational controls. The system uses a fixed 30-day context window, attaches evidence IDs to claims, abstains when confidence is insufficient, limits recommendations to one or two actions, and requires human confirmation before AI generation or export. A non-AI baseline makes the model contribution measurable. The dataset and account-level splits are reproducible, and the frozen test evaluation was run once after prompt and threshold selection.

The final M2 configuration achieved 1.000 accuracy and 1.000 Macro-F1 on 120 role labels across 20 fictional test accounts, with 0.833 coverage, 1.000 evidence precision, and 1.000 critical-event recall. All 20 calls succeeded on the first attempt. These results should be interpreted in the context of a controlled synthetic dataset rather than as evidence of production performance.

A five-person blinded pilot added a separate usability check. Across 20 B0-versus-M2 comparisons, participants preferred M2 in all 20. Median preparation time fell from 185 to 145 seconds, and the median six-item mean rating increased from 2.83 to 4.50. The recurring benefit was faster reconstruction of named decision roles, evidence, and next actions; the recurring caution was that inferred authority still requires human verification.

## Challenges and decisions

The main challenge was avoiding confident but unsupported stakeholder claims. I addressed this with a strict structured-output schema, claim-level evidence validation, retry/failure handling, and an explicit abstention threshold. I also kept deterministic risk checks for unresolved tickets, unanswered emails, and competitor signals separate from model-generated summaries so important alerts remain inspectable.

Another challenge was reconciling the broad proposal with a feasible course-project scope. I retained the requested business workflow but treated live enterprise connectors, automatic Slack delivery, SSO, production deployment, and verified organisational reporting lines as out of scope. The decision-chain edges are therefore labelled as workflow hypotheses requiring human confirmation.

## Limitations

The evaluation data is synthetic and follows patterns encoded by the generator, so the perfect test classification result is likely easier than performance on messy enterprise data. The blinded pilot used fictional accounts, only five self-reported participants, and highly uniform completed responses; the import verified completeness but not participant identity or the live sessions. It therefore provides directional usability evidence rather than a population-level result. Latency and cost depend on the external API provider. The interface does not validate identities or permissions against a real organisation, and exported content must still be handled according to the user's data-governance rules.

## Next iteration

The next iteration should repeat the blinded study with a larger and more varied externally observed sample, test with privacy-approved de-identified enterprise examples, calibrate confidence on more diverse language, add role-based access controls, and integrate read-only connectors behind explicit consent. Production use would also require security review, retention rules, audit logging, monitoring, and a formal process for correcting source data.

## Reflection

The project demonstrates that useful AI assistance is not only a generation problem. Its value depends on scope discipline, traceable evidence, uncertainty communication, failure behaviour, and a clear boundary between advice and human action. The most important learning was to design evaluation and responsible-use constraints alongside the product rather than add them at the end.
