# Phase 2 results

## Outcome

Phase 2 is complete. All development and validation records were synthetic. The frozen test split was not accessed by a live model call.

The selected final candidate is **M2 with `account_briefing_v2`, model `openai/gpt-4o`, and abstention threshold `0.65`**. M2 is preferred over H1 because it achieved the same validation quality with lower estimated cost and lower p95 latency, while retaining evidence requirements, abstention guidance, prompt-injection handling, and deterministic evidence validation.

## Development iteration

The first five-account M2 review found three champion contacts incorrectly classified as unknown. The common error was treating an internal champion as if the person needed final purchase authority. Prompt v2 added explicit behavioural definitions for all decision roles and clarified that a champion coordinates, advocates, and drives adoption without needing budget authority.

| Prompt | Accuracy | Macro-F1 | Coverage | Evidence precision | Critical-event recall |
|---|---:|---:|---:|---:|---:|
| v1 | 0.9000 | 0.8901 | 0.7333 | 1.0000 | 1.0000 |
| v2 | 1.0000 | 1.0000 | 0.8333 | 1.0000 | 1.0000 |

## Validation comparison

The validation split contains 10 accounts and 60 role predictions.

| Experiment | Accuracy | Macro-F1 | Coverage | Evidence precision | Critical-event recall | Estimated cost (USD) | p95 latency (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| B0 rules | 0.6667 | 0.6940 | 0.5000 | N/A | N/A | 0.000000 | N/A |
| M1 direct model | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.157527 | 10.1548 |
| M2 evidence-grounded | 1.0000 | 1.0000 | 0.8333 | 1.0000 | 1.0000 | 0.154898 | 7.9942 |
| H1 hybrid | 1.0000 | 1.0000 | 0.8333 | 1.0000 | 1.0000 | 0.169681 | 14.2430 |

All 30 validation model calls succeeded on their first attempt. The cost values are project estimates based on the pinned metadata and are not a substitute for the provider billing record.

## Instructor-aligned supplementary signatory evaluation

A separate set of 10 hand-authored fictional accounts implements the instructor's requested data shape: two email threads with CC lists, one meeting attendee list, two tickets and one explicit `true_signatory_contact_id` per account. The highest-confidence, non-abstained economic-buyer prediction is treated as the system's selected signatory. The label is excluded from model prompts, and the prompt and records were frozen before the one-time run.

| System | Accounts | Selected | Correct | Precision | Recall | Selection rate |
|---|---:|---:|---:|---:|---:|---:|
| B0 rules | 10 | 7 | 7 | 1.0000 | 0.7000 | 0.7000 |
| M2 evidence-grounded | 10 | 10 | 10 | 1.0000 | 1.0000 | 1.0000 |

Precision alone hides the baseline's three omissions. Recall and selection rate are reported beside it. M2 role accuracy, Macro-F1, evidence precision and critical-event recall were all 1.0000. The ten calls cost an estimated USD 0.125933 and had p95 latency of 8.2823 seconds. This is a supplementary fictional-data result, not a production claim.

M1's coverage of 1.0 reflects its intentionally weaker baseline instructions: it returned `unknown` without marking those predictions as abstentions. M2 and H1 used the intended abstention semantics, so coverage of 0.8333 is expected because one of six role labels is `unknown` in each account.

## Threshold selection

The H1 result was rescored offline at thresholds from 0.50 to 0.95, with no additional API calls. Thresholds 0.50 through 0.85 tied at accuracy 1.0, Macro-F1 1.0, and coverage 0.8333. Performance fell at 0.90 and 0.95. The preset 0.65 threshold was retained as the tie-break choice to avoid unnecessary validation-set overfitting.

The complete machine-readable sweep is in `results/h1_threshold_sweep_validation.json`.

## Phase 3 gate

Before the one-time frozen test run:

1. Confirm the selected M2 configuration and model name are final.
2. Do not edit the prompt, role taxonomy, threshold, or evaluation code after viewing test results.
3. Run the test split exactly once and archive the resulting files.
4. Produce charts, error analysis, and the small blinded user study from the frozen outputs.
