# Data and Evaluation Guide

This guide explains which data AccountLens uses, how labels are protected from model input, how each evaluation was run, and how the checked-in artifacts support the reported results. All account, contact and event records are fictional. Human-study records use anonymous participant codes only.

## 1 Data inventory

| Dataset | Size and split | Purpose | Repository location |
|---|---|---|---|
| Frozen synthetic accounts | 60 accounts: 30 development, 10 validation, 20 test | Prompt development, candidate selection and one final frozen test | `data/generated/` |
| Instructor-aligned accounts | 10 hand-authored accounts | Separate signatory-selection evaluation using the evidence shape requested by the instructor | `data/teacher_aligned_10/` |
| Blinded user-study inputs | 4 fictional validation accounts shown to 5 participants | Compare meeting-readiness of B0 and M2 briefings | Masked packets in `docs/user_study_materials/` |
| Normalized user-study outputs | 40 briefing observations and 20 paired choices | Descriptive usability evidence | `results/real_user_study*` |

The frozen 60-account snapshot was generated with seed `6201` and reference date `2026-09-01`. Its manifest records 60 accounts, 360 contacts, 1,106 interactions, 360 role labels and 128 critical-event labels. SHA-256 hashes in `data/generated/manifest.json` allow an assessor to verify that regeneration produces the same files.

The public repository excludes the five completed questionnaire documents and the facilitator decoding key. They are preserved in the private instructor package. The normalized results remain checked in so the reported calculations can be audited without publishing the original forms.

## 2 Record and label structure

| File family | Model-visible information | Evaluation-only information |
|---|---|---|
| Accounts | Account ID, fictional name, industry, stage and opportunity value | `true_signatory_contact_id` |
| Contacts | Contact ID, fictional name, title, department and seniority | Correct decision role is stored separately |
| Interactions | Event ID, date, channel, internal team, participant IDs, subject, content and status | Critical-event labels are stored separately |
| Role ground truth | None | One of `champion`, `economic_buyer`, `technical_evaluator`, `procurement_legal`, `end_user` or `unknown` for every contact |
| Critical-event ground truth | None | Event IDs and categories that a good briefing should surface |

`true_signatory_contact_id`, role ground truth and critical-event ground truth are loaded only by evaluation code. They are removed before model payload construction. Automated tests cover signatory leakage prevention and reject invalid contact or evidence IDs.

For the synthetic 60-account dataset, the economic buyer is also the commercial signatory. The instructor-aligned dataset stores the signatory independently and defines the role as the person with final commercial approval authority. A procurement or legal contact who only executes paperwork is not counted as the signatory.

## 3 Freeze and contamination controls

1. Development accounts were used to inspect early failures and revise role definitions.
2. Validation accounts were used to compare B0, M1, M2 and H1 and to select the confidence threshold.
3. The model name, prompt, threshold and evaluation code were frozen before the test split was used.
4. The 20-account test split was run once with the final M2 configuration.
5. The threshold sweep rescored saved H1 predictions offline and made no additional model calls.
6. The 10-account signatory run was a post-freeze supplementary evaluation and did not alter the original frozen test metrics.
7. Presentation features added after the frozen test are covered by unit tests but are not represented as improvements to the frozen role-classification score.

The final configuration is M2 with `openai/gpt-4o`, prompt `account_briefing_v2.txt` and confidence threshold `0.65`.

## 4 Systems compared

| ID | System | What it tests |
|---|---|---|
| B0 | Deterministic title and interaction rules | Whether simple non-AI rules are sufficient |
| M1 | Direct model prompt | Model-only performance with weaker evidence and abstention instructions |
| M2 | Evidence-grounded structured model | The value of role definitions, required evidence IDs, abstention and validation |
| H1 | M2 plus deterministic rule features and fallback | Whether added hybrid complexity improves quality enough to justify cost and latency |

M2 was selected because it matched H1's validation quality while using lower estimated cost and lower p95 latency. Prompt v1 had classified three champions as unknown by confusing advocacy with final approval authority. Prompt v2 separated those behaviours, raising development Macro-F1 from `0.8901` to `1.0000`.

## 5 Metric definitions

| Metric | Definition | Why it matters |
|---|---|---|
| Accuracy | Correct contact-role predictions divided by all contact-role labels | Overall classification performance |
| Macro-F1 | Unweighted mean of F1 across all six role classes | Prevents large classes from dominating the score |
| Coverage | Fraction of predictions that are not marked as abstentions | Shows whether high accuracy is achieved by avoiding difficult cases |
| Evidence precision | Valid cited event IDs divided by all cited event IDs | Detects fabricated or invalid evidence references |
| Critical-event recall | Labelled critical events surfaced divided by all labelled critical events | Checks whether the briefing misses important account developments |
| Signatory precision | Correct signatory selections divided by all selections | Measures trustworthiness when the system names a signatory |
| Signatory recall | Correct signatory selections divided by all accounts | Penalizes accounts where the system fails to find the signatory |
| Selection rate | Accounts with a signatory selection divided by all accounts | Makes omission visible beside precision |
| p95 latency | 95th percentile of successful generation latency | Tests fit with the short meeting-preparation window |
| Estimated cost | Token-based project estimate for successful model calls | Supports affordability analysis; it is not a billing record |

The signatory-selection rule chooses the highest-confidence, non-abstained `economic_buyer` prediction for each account. Reporting precision, recall and selection rate together prevents a system from appearing perfect by selecting only easy accounts.

## 6 Targets and reached results

| Measure | Target | Reached | Interpretation |
|---|---:|---:|---|
| Frozen-test Macro-F1 | At least 0.75 | 1.0000 | Met on controlled fictional data |
| Improvement over B0 Macro-F1 | At least +0.15 | +0.2976 | M2 1.0000 versus B0 0.7024 |
| Evidence precision | At least 0.90 | 1.0000 | All cited event IDs were valid |
| Selective accuracy | At least 0.85 | 1.0000 | Met at 0.8333 coverage |
| Coverage | At least 0.70 | 0.8333 | Unknown contacts were deliberately abstained |
| Critical-event recall | Reported supporting metric | 1.0000 | All labelled critical events were surfaced |
| p95 latency | Below 15 seconds | 8.1254 seconds | Met in the frozen provider run |
| Variable model cost | Below USD 0.05 per briefing | USD 0.016065 | Excludes integration, monitoring and human review |
| Instructor-aligned signatory precision | At least 0.85 | 1.0000 | 10 correct selections from 10 |
| Instructor-aligned selection rate | At least 0.70 | 1.0000 | A signatory was selected for every account |
| Blinded-pilot time reduction | At least 15% | 21.62% | Median 185 seconds for B0 versus 145 for M2 |
| Blinded-pilot preference | At least 60% for M2 | 100% | M2 preferred in 20 of 20 pairs |

Unsupported-claim rate had a project target of at most `0.05`, but it was not estimated as a separate semantic-claim metric. The implemented evidence validator instead measured whether cited event IDs were valid and obtained evidence precision of `1.0000`. This is narrower than proving that every natural-language claim is fully supported.

This gap is intentionally reported rather than replaced with an automated proxy. A future semantic-support evaluation should split every briefing into atomic claims, hide the generating system, and ask two independent reviewers to label each claim as entailed, partially supported, or unsupported by its cited records. Disagreements should be adjudicated before calculating `unsupported claims / all claims`, with results reported by claim type and alongside reviewer agreement. Because that review was not performed before the frozen submission, no unsupported-claim result is claimed here.

## 7 Artifact lineage

| Question | Evaluation code | Input | Checked-in output |
|---|---|---|---|
| How strong is the deterministic baseline? | `src/accountlens/evaluation/run.py` | `data/generated/` | `results/baseline_validation.json`, `results/baseline_test.json` |
| Which model configuration should be selected? | `src/accountlens/evaluation/experiments.py` | Development and validation splits | `results/m1_validation.json`, `results/m2_validation.json`, `results/h1_validation.json` |
| Which threshold should be used? | `src/accountlens/evaluation/thresholds.py` | Saved H1 validation predictions | `results/h1_threshold_sweep_validation.json` |
| Does the final model generalize to the frozen test accounts? | `src/accountlens/evaluation/experiments.py` | 20 frozen test accounts | `results/m2_test.json` |
| Does the system identify the commercial signatory? | `tools/evaluate_signatory.py` and `tools/run_teacher_aligned_evaluation.py` | Saved predictions plus hidden signatory labels | `results/signatory_validation.json`, `results/teacher_aligned_*.json` |
| Is the briefing useful for meeting preparation? | `tools/import_real_user_study.py` | Five completed anonymous questionnaires | `results/real_user_study.json` and two CSV files |
| What does it cost? | `src/accountlens/evaluation/economics.py` | Saved token usage and explicit scenarios | `results/class5_economics.json` |

## 8 Reproduction commands

Generate and verify the fictional data:

```powershell
python -m accountlens.data.generate --seed 6201 --accounts 60
python tools\build_teacher_aligned_dataset.py
```

Run non-billable checks:

```powershell
python -m accountlens.evaluation.run --split validation
python tools\evaluate_signatory.py
python -m unittest discover -s tests -v
```

Inspect model payloads without an API call:

```powershell
python -m accountlens.evaluation.experiments --experiment all --split validation --dry-run
```

Live development or validation experiments require a locally supplied API key. Do not rerun or tune against the frozen test split. The checked-in final results are the authoritative frozen record.

## 9 Evaluation limits

- The synthetic accounts are balanced and generated from repeated role-specific patterns, so perfect model scores do not establish real-world accuracy.
- Development, validation and test records come from the same generator and do not measure transfer across organisations, systems, languages or data-quality regimes.
- Evidence precision verifies reference validity, not complete semantic entailment of every sentence.
- The 10 instructor-aligned accounts were hand-authored for the project and are supplementary rather than an independent external benchmark.
- The blinded pilot contains five self-reported participants, fictional accounts and highly uniform responses. Identity, session conduct and timing were not independently observed.
- Cost excludes integration, security, monitoring, maintenance, governance and human fallback.
- Production use would require lawful access, independent annotation, role-based controls, retention policy, drift monitoring and a larger externally observed user study.
