# Instructor-aligned ten-account dataset

## Purpose

This supplementary dataset directly implements the instructor's recommendation to replace unavailable Salesforce, Outlook, Jira and calendar access with ten fictional enterprise accounts. It is isolated from the original 60-account generated dataset and does not alter the frozen test split or its reported results.

## Required record shape

Every account contains:

- two fictional email threads, each with explicit sender, recipient and CC contact IDs;
- one meeting with an explicit attendee list and internal attendees;
- two support tickets, including status and priority;
- one CRM note;
- six fictional contacts with role ground truth;
- one `true_signatory_contact_id`, defined as the person with final commercial approval authority.

Across the dataset this yields 10 accounts, 60 contacts, 20 emails, 10 meetings, 20 tickets and 10 CRM notes. Procurement or legal contacts who only execute documents are deliberately separated from the true commercial signatory.

## Evaluation rule

For each account, the evaluator takes the highest-confidence, non-abstained `economic_buyer` prediction as the system's selected signatory and compares its contact ID with `true_signatory_contact_id`.

The primary metric is signatory precision. Recall and selection rate are reported beside it so that a system cannot appear successful merely by omitting difficult accounts. Role accuracy, evidence precision, critical-event recall, latency and variable API cost are supporting measures.

The ground-truth signatory field is removed before model input. `manifest.json` records file hashes, counts and the required shape. The ten accounts are treated as a frozen supplementary evaluation set: after a live M2 run is inspected, neither the prompt nor these records should be tuned against the result.

## Reproduction

```powershell
# Rebuild the deterministic hand-authored files and the zero-cost rules baseline
python tools\build_teacher_aligned_dataset.py

# Inspect the planned M2 run without making a model call
python tools\run_teacher_aligned_evaluation.py

# Run M2 once on all ten accounts (ten paid API calls)
python tools\run_teacher_aligned_evaluation.py --confirm-paid-run
```

The build command writes the dataset to `data/teacher_aligned_10/` and the rules result to `results/teacher_aligned_baseline.json`. The confirmed live command writes `results/teacher_aligned_m2.json`.

## Recorded result

The frozen supplementary evaluation was run once on 24 September 2026.

| System | Selected | Correct | Precision | Recall | Selection rate |
|---|---:|---:|---:|---:|---:|
| B0 rules | 7 | 7 | 1.0000 | 0.7000 | 0.7000 |
| M2 evidence grounded | 10 | 10 | 1.0000 | 1.0000 | 1.0000 |

M2 also achieved 1.0000 role accuracy, Macro-F1, evidence precision and critical-event recall. The ten calls used 25,737 input tokens and 6,159 output tokens, with an estimated variable cost of USD 0.125933 and p95 latency of 8.2823 seconds. All evidence validations passed. These are results on hand-authored fictional accounts, not estimates of production accuracy.
