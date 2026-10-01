# Data directory

This repository checks in the exact fictional data used for development, validation and the frozen test evaluation. No real customer or employee data is included.

For the complete data lineage, label-separation policy and connection to evaluation artifacts, see `docs/data_and_evaluation_guide.md`.

## Frozen 60-account dataset

`generated/` is the fixed evaluation snapshot produced with seed `6201` and reference date `2026-09-01`. It contains 60 accounts, 360 contacts, 1,106 interaction records, 360 role labels and 128 critical-event labels. Account-level splits are fixed at 30 development, 10 validation and 20 test accounts.

| File | Purpose |
|---|---|
| `accounts.jsonl` | Account records and account-level true signatory labels |
| `contacts.jsonl` | Six fictional contacts per account |
| `interactions.jsonl` | Fictional CRM, email, meeting, calendar and support-ticket evidence |
| `role_ground_truth.jsonl` | Contact-level decision-role labels used only for evaluation |
| `critical_event_ground_truth.jsonl` | Event-level labels used for critical-event recall |
| `splits.json` | Frozen development, validation and test account IDs |
| `manifest.json` | Seed, reference date, record counts and SHA-256 hashes |

Reproduce the snapshot with:

```powershell
python -m accountlens.data.generate --seed 6201 --accounts 60
```

The hashes in `manifest.json` allow the checked-in snapshot to be compared with a regenerated copy.

## Label separation

Each account contains `true_signatory_contact_id`, defined as the contact with final commercial approval authority. This field is used only for offline evaluation and is removed from every model prompt to prevent label leakage.

Role and critical-event ground truth are also loaded by the evaluation layer, not inserted into model prompts. Automated tests verify this separation.

## Instructor-aligned dataset

`teacher_aligned_10/` is a separate, deterministic, hand-authored supplementary dataset built to match the instructor's requested evidence shape. Each of its ten accounts contains two email threads with CC lists, one attendee list, two tickets, one CRM note and an explicit true commercial signatory. See `docs/teacher_aligned_dataset.md`.

## Participant data

Only normalized anonymous pilot results are included in the public repository. Completed questionnaires and the facilitator decoding key are retained in the private instructor package.
