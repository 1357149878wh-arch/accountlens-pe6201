# Results directory

This directory checks in the machine-readable outputs used to select, freeze and critique the final system. The files contain only fictional account data or anonymous participant codes.

For metric definitions, target-versus-result tables, artifact lineage and evaluation limitations, see `docs/data_and_evaluation_guide.md`.

## Experiment sequence

| Stage | Files | Purpose |
|---|---|---|
| Dry-run validation | `b0_dry_run.json`, `m1_dry_run.json`, `m2_dry_run.json`, `h1_dry_run.json` | Verify payload construction without billable model calls |
| Development | `baseline_development.json`, `m2_development.json` | Inspect early errors and revise the role definitions before validation |
| Validation comparison | `b0_validation.json`, `baseline_validation.json`, `m1_validation.json`, `m2_validation.json`, `h1_validation.json` | Compare the deterministic baseline, direct model, evidence-grounded model and hybrid candidate |
| Threshold selection | `h1_threshold_sweep_validation.json` | Offline sweep from 0.50 to 0.95; retain 0.65 without additional model calls |
| Frozen test | `baseline_test.json`, `m2_test.json` | One final 20-account comparison after model, prompt and threshold were frozen |
| Signatory evaluation | `signatory_validation.json`, `teacher_aligned_baseline.json`, `teacher_aligned_m2.json` | Report precision, recall and selection rate on the validation and separate 10-account datasets |
| Economics | `class5_economics.json` | Variable cost, USD 10 capacity, cost-to-serve scenarios and break-even assumptions |
| Presentation | `test_comparison.svg` | Human-readable frozen-test metric comparison |

The final selection was M2 with `account_briefing_v2`, model `openai/gpt-4o` and threshold `0.65`. M2 matched H1's validation quality with lower estimated cost and lower p95 latency. Full interpretation and limitations are in `docs/phase2_results.md` and `docs/final_evaluation.md`.

## User-evaluation artifacts

Real blinded-pilot artifacts:

- `real_user_study_observations.csv`: 40 normalized briefing observations;
- `real_user_study_preferences.csv`: 20 decoded pairwise preferences;
- `real_user_study.json`: profiles, answers, completeness metadata, summaries, and pre-registered target outcomes.

Synthetic pilot artifact:

- `simulated_user_evaluation.json`: deterministic rehearsal of the study procedure; it is not human-participant evidence.

## Reproduction

Run the non-billable baseline and tests with:

```powershell
python -m accountlens.evaluation.run --split validation
python -m unittest discover -s tests -v
```

Rebuild the Class 5 signatory and economics summaries from saved predictions without a model call:

```powershell
python tools\evaluate_signatory.py
```

Live model experiments require a locally supplied API key. The frozen test output must not be regenerated or tuned after inspection.

## Interpretation boundary

Perfect M2 scores are controlled fictional-data results, not production accuracy claims. The five-person pilot is descriptive because the sample is small, timing is self-reported and participant identity or live sessions were not independently verified. Provider cost figures are estimates recorded by the project and may differ from billing records.
