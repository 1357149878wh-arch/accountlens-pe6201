# Final evaluation

## Frozen configuration

The final configuration was frozen before the test split was used by a live model:

- experiment: M2 evidence-grounded briefing;
- model: `openai/gpt-4o` through OpenRouter;
- prompt: `account_briefing_v2.txt`;
- abstention threshold: `0.65`;
- prompt SHA-256: `A0BE5A8F89381857F2F12671C447812316D227FCD79EFEEE906C5921DBAAD541`;
- pipeline SHA-256: `4733D34B32FCE317E9EAF860C40C75969A606E0C53B3498927073BCA90ED2A04`.

The final M2 test command was run once on 20 synthetic accounts. No prompt, threshold, model, or evaluation changes were made after the result was viewed, and the model was not called on the test split again.

## Final results

The test split contains 20 accounts and 120 role labels, with 20 examples for each of the six classes.

| Metric | Rules baseline | Final M2 |
|---|---:|---:|
| Accuracy | 0.6667 | 1.0000 |
| Macro-F1 | 0.7024 | 1.0000 |
| Coverage | 0.5000 | 0.8333 |
| Evidence precision | N/A | 1.0000 |
| Critical-event recall | N/A | 1.0000 |
| Estimated API cost | $0.000000 | $0.321290 |
| p95 latency | N/A | 8.1254 s |

All 20 model calls succeeded on their first attempt. The final run used 63,567 input tokens and 16,237 output tokens. Estimated cost is project metadata and may differ from the provider's billing record.

Every role class achieved precision, recall, and F1 of 1.0. Coverage is 0.8333 because each account contains one correctly identified `unknown` contact, and unknown predictions are deliberately marked as abstentions.

## Error analysis

There were no role-classification errors, invalid evidence references, missing critical events, parsing failures, or retries in the frozen test run. The rules baseline made 40 errors, all caused by abstaining on supported non-unknown roles. Its largest recall gaps were procurement/legal (0.45), end user (0.50), technical evaluator (0.60), and champion (0.65).

The absence of M2 errors must not be interpreted as real-world perfection. The dataset is synthetic, balanced, small, and generated from repeated role-specific patterns. The same generation process created the development, validation, and test records, so the test split measures generalisation across fictional accounts rather than across organisations, writing styles, CRM systems, languages, or real data quality problems. A production claim would require external data, independent annotation, calibration analysis, privacy review, and monitoring for distribution shift.

## Reproducibility artifacts

- `results/baseline_test.json`: deterministic test baseline;
- `results/m2_test.json`: frozen final M2 output;
- `results/test_comparison.svg`: presentation-ready metric comparison;
- `logs/api_runs.jsonl`: metadata-only API run log;
- `docs/phase2_results.md`: development, validation, and threshold-selection record.

Artifact SHA-256 checksums:

- `baseline_test.json`: `4D3DBA30435E10F1D4DD588C69507E3CE782446A4E8825EBAD7D02BEFCF3245B`;
- `m2_test.json`: `F75A1E8D7D483BBB8398F4B608E1D7BCF1E14265DECD717A5AD33583F133377E`.

## Blinded user evaluation

Five anonymous, participant-provided completed questionnaires were imported after scoring and decoded with the frozen facilitator key. Across 20 paired comparisons, M2 was preferred 20 times (100%). Its median preparation time was 145 seconds versus 185 seconds for B0, a 21.6% reduction. The median of the six-item mean rating was 4.50 for M2 and 2.83 for B0, a gain of 1.67 points. All three pre-registered pilot targets were met.

These findings are descriptive, not inferential. The accounts are fictional, the sample contains five self-reported participants, and the completed answers are highly uniform. The import process verified document completeness and arithmetic but did not independently observe the sessions or verify participant identity. Full results and limitations are in `docs/real_user_evaluation.md`; normalized records are in `results/real_user_study.json` and the two real-user-study CSV files.

## Remaining project work

The model evaluation, clean-environment setup verification, and five-person blinded pilot are complete. Remaining non-model work is to obtain the official final submission brief, record the demonstration/final communication artifact in the required format, and package the repository. The current four-minute video, self-appraisal, and release-tag plan is provisional until the separate Final Project Rubric is available.

## Post-evaluation Statement alignment

After the frozen test result was recorded, a deterministic presentation and orchestration layer was added without changing the tested model, v2 prompt, abstention threshold, or saved test outputs. It adds a 30-day operational window, decision-workflow hypotheses, missing-role detection, cross-team ranking, deterministic risk signals, relevance feedback, human-confirmation controls, one-page PDF export, and a Slack-ready local download. These features are covered by unit tests but are not included in the frozen role-classification score.

## Post-freeze Class 5 supplement

A separate instructor-aligned dataset contains 10 hand-authored fictional accounts, each with two email threads and explicit CC lists, one meeting attendee list, two tickets, one CRM note and one `true_signatory_contact_id`. The label is removed from model input. In a one-time supplementary run, M2 selected all 10 signatories correctly, giving precision, recall and selection rate of 1.0000. B0 selected 7 signatories and all 7 were correct, giving precision 1.0000 but recall and selection rate of 0.7000. The ten M2 calls cost an estimated USD 0.125933 and had p95 latency of 8.2823 seconds. This result does not alter the original frozen test configuration or its metrics.

The Class 5 cost analysis reports USD 0.016065 as the observed variable cost per test briefing and approximately 622 briefings from a USD 10 balance at that variable-only rate. It also separates human fallback and fixed monthly costs through explicit sensitivity scenarios. These scenarios are planning assumptions, not measured production costs.
