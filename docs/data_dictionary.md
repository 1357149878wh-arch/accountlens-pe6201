# Data dictionary

All records are synthetic and use fictional identifiers.

## accounts.jsonl

| Field | Type | Description |
|---|---|---|
| account_id | string | Stable fictional account identifier |
| name | string | Fictional company name |
| industry | string | Industry category |
| stage | string | Current procurement stage |
| annual_value_usd | integer | Synthetic opportunity value |
| true_signatory_contact_id | string | Contact with final commercial approval authority; used only for offline evaluation and removed from model input |

## contacts.jsonl

| Field | Type | Description |
|---|---|---|
| contact_id | string | Stable contact identifier |
| account_id | string | Parent account |
| name | string | Fictional display name |
| title | string | Job title, sometimes intentionally ambiguous |
| department | string | Business function |
| seniority | string | Individual, manager, director, or executive |

## interactions.jsonl

| Field | Type | Description |
|---|---|---|
| event_id | string | Evidence identifier shown in briefings |
| account_id | string | Parent account |
| date | string | ISO date |
| channel | string | Email, meeting, CRM note, or ticket |
| internal_team | string | Internal team responsible for the event |
| participant_ids | list[string] | External contact IDs involved |
| subject | string | Short event title |
| content | string | Synthetic unstructured record |
| status | string | Open, closed, sent, or completed |

## role_ground_truth.jsonl

The correct role for every contact. Supported values are `champion`, `economic_buyer`, `technical_evaluator`, `procurement_legal`, `end_user`, and `unknown`.

For this synthetic dataset, the `economic_buyer` contact is also the account's true commercial signatory. A procurement or legal contact who only executes paperwork is not treated as the true signatory.

## critical_event_ground_truth.jsonl

The event IDs that a good briefing should surface, with category and importance labels.

## splits.json

Account-level development, validation, and test partitions. The test split must remain frozen until the final evaluation.
