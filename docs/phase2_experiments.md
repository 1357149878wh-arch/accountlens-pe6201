# Phase 2 experiments

## Experiment definitions

| ID | System | Purpose |
|---|---|---|
| B0 | Deterministic title and interaction rules | Non-AI baseline |
| M1 | GPT-4o with a short direct prompt | Model-only baseline |
| M2 | GPT-4o with evidence, abstention, and responsible-use instructions | Evidence-grounded model |
| H1 | M2 plus deterministic rule features and fallback | Final hybrid candidate |

All AI experiments use the same strict `AccountBriefing` Pydantic output schema. M1 does not require every claim to cite evidence, because missing evidence is one of the differences being measured. M2 and H1 require valid event IDs for every non-abstained claim.

## Safe dry-run

This checks payload construction without an API key or billable call:

```powershell
python -m accountlens.evaluation.experiments --experiment all --split validation --dry-run
```

## First live smoke test

After `.env` contains a valid local API key, run one development account:

```powershell
python -m accountlens.evaluation.experiments --experiment M2 --split development --limit 1
```

Inspect the resulting file and `logs/api_runs.jsonl` before increasing the limit to five accounts.

## Validation experiment

Run each candidate on the validation split. This is the only split used to select the hybrid threshold:

```powershell
python -m accountlens.evaluation.experiments --experiment all --split validation
```

Compare Macro-F1, per-class F1, coverage, critical-event recall, evidence precision, cost, and p95 latency.

## Frozen test protection

The runner rejects live AI calls on `test` unless `--confirm-test` is supplied. Do not use that flag until the model, prompt, and threshold are frozen.

## Logs and privacy

The JSONL log stores request ID, experiment, model, prompt version, attempts, latency, token counts, estimated cost, validation status, and error type. It never stores account records, API keys, prompts, or model outputs.

