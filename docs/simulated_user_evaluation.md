# Simulated blinded-evaluation pilot

> **SIMULATED RESULTS - NOT HUMAN PARTICIPANT DATA.** This pilot validates the study procedure only and must not be presented as completed user research.

## Purpose

Five fictional evaluator personas reviewed four validation accounts under a reproducible A/B order. B0 is the deterministic role-only baseline; M2 uses the already-saved frozen validation briefings. No API call or test-set run was made.

## Virtual evaluator panel

| ID | Fictional role | Fictional experience |
|---|---|---|
| VP01 | Key Account Manager | 8 years managing enterprise software accounts |
| VP02 | Sales Director | 12 years reviewing strategic opportunities |
| VP03 | Presales Engineer | 6 years in solution design and technical validation |
| VP04 | Customer Success Manager | 7 years managing adoption and service risks |
| VP05 | Revenue Operations Analyst | 5 years in CRM governance and pipeline analysis |

## Aggregate simulated results

| Measure | B0 | M2 |
|---|---:|---:|
| Median preparation time (seconds) | 158.0 | 139.0 |
| Median mean rating (1-5) | 3.34 | 4.58 |
| Role usefulness (1-5) | 3.6 | 4.9 |
| Evidence trust (1-5) | 4.9 | 5.0 |
| Risk relevance (1-5) | 1.5 | 3.8 |
| Action usefulness (1-5) | 1.1 | 5.0 |
| Clarity (1-5) | 4.4 | 4.3 |
| Confidence calibration (1-5) | 4.7 | 4.7 |

Across 20 simulated participant-account pairs, preference counts were: M2=20, B0=0, tie=0.

## Interpretation

The synthetic panel is expected to favour M2 because M2 includes risk summaries and recommended actions while B0 is intentionally a role-only baseline. This is useful for checking whether the questionnaire detects the intended product difference, but it is not evidence that real users will agree, work faster, or make better decisions.

## Method

- Accounts: `ACC-014`, `ACC-020`, `ACC-040`, and `ACC-058`, all from the validation split.
- Five fictional personas; four account pairs per persona; 40 masked briefing observations.
- A/B order is deterministic but randomised from seed `6201`.
- Role accuracy, coverage, evidence validity, and critical-event recall come from saved validation artifacts.
- Likert scores and preparation times are transparent heuristic transformations with small seeded persona variation.
- The test split, final metrics, frozen prompt, model, and threshold were not touched.

## Limitations

- No real person viewed or scored a briefing.
- Likert ratings and preparation times are generated from disclosed heuristics.
- The simulator is not independent of the project design and cannot validate business value.
- Results are suitable only for piloting the study procedure and checking analysis code.

## Permitted claim

The project completed a reproducible synthetic pilot of the blinded study procedure. The pilot identified no structural problem in the scoring or aggregation workflow. A real blinded participant study remains outstanding.

## Prohibited claim

Do not write that five users participated, that users preferred M2, or that preparation time improved. Those statements would misrepresent simulated observations as human research.
