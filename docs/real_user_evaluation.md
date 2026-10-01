# Real blinded user evaluation

## Status and scope

Five anonymous, participant-provided completed questionnaires were imported on 2026-09-22. They contain 20 participant-account comparisons and 40 briefing observations across ACC-014, ACC-020, ACC-040 and ACC-058. This evidence is separate from the synthetic pilot and does not alter or rerun the frozen test set.

The files establish that all four consent items were checked in every questionnaire. Participation itself and the stated background are self-reported; no independent identity or session verification was performed during import.

## Participant profile

| Participant | Self-reported background | Relevant experience |
|---|---|---|
| P01 | Account management | 4-7 years |
| P02 | Presales | 4-7 years |
| P03 | Customer success | 4-7 years |
| P04 | Business analysis | 1-3 years |
| P05 | Other: B2B procurement practitioner | 1-3 years |

## Method

Each participant reviewed B0 and M2 briefings in counterbalanced A/B order for four fictional accounts. Participants recorded meeting-readiness time, scored six dimensions from 1 to 5, and selected a preferred briefing after each pair. The frozen facilitator key was used only after the completed answers were retrieved to decode A/B labels. Results below are descriptive because this is a small pilot.

## Quantitative results

Each system has 20 observations.

| Measure (median) | B0 | M2 |
|---|---:|---:|
| Role usefulness | 2.0 | 5.0 |
| Evidence trust | 4.0 | 5.0 |
| Risk relevance | 2.0 | 4.0 |
| Action usefulness | 2.0 | 5.0 |
| Clarity | 3.0 | 4.0 |
| Uncertainty | 4.0 | 4.0 |
| Mean of six ratings | 2.83 | 4.50 |
| Preparation time (seconds) | 185 | 145 |

- M2's median mean rating was **1.67 points higher** than B0.
- M2's median preparation time was **21.6% lower** (145 vs 185 seconds).
- Participants preferred M2 in **20/20 comparisons (100%)**.
- All M2 observations were marked Ready; all B0 observations were marked Partly ready.

### Paired results by participant

| Participant | Median rating difference (M2-B0) | Median time difference in seconds (M2-B0) | M2 preferences |
|---|---:|---:|---:|
| P01 | +1.67 | -40 | 4/4 |
| P02 | +1.67 | -40 | 4/4 |
| P03 | +1.67 | -40 | 4/4 |
| P04 | +1.67 | -40 | 4/4 |
| P05 | +1.67 | -40 | 4/4 |

## Pre-registered pilot targets

| Target | Observed result | Outcome |
|---|---:|---|
| Median mean rating: M2 at least +0.5 vs B0 | +1.67 | Met |
| Median preparation time: M2 at least 15% lower | 21.6% lower | Met |
| At least 60% of pairwise preferences favour M2 | 100% | Met |

## Qualitative findings

The recurring explanation was that M2 is more meeting-ready because it names likely decision roles, connects claims to evidence IDs and makes the next action easier to identify. Participants said this reduced the effort required to reconstruct the buying group. The recurring caution was equally important: role authority remains a hypothesis and should be verified before a customer conversation. The weaker B0 briefings were described as activity summaries rather than explicit buyer-role maps. Participants generally regarded the uncertainty wording as appropriate.

## Limitations

- The sample contains five self-reported participants and fictional accounts, so the findings are directional rather than population-level evidence.
- The completed responses are highly uniform and structured. The importer verified document completeness and arithmetic, but did not independently observe the sessions or verify participant identity.
- Timing is self-recorded in the provided forms and the study measures short-term meeting preparation, not downstream commercial outcomes.
- Descriptive comparisons are reported; no inferential significance claim is made.
- A larger external study with more varied roles, live facilitation and real enterprise data remains recommended.

## Conclusion

Within this five-person blinded pilot, M2 met all three pre-registered targets and was consistently judged more useful for meeting preparation than B0. The result supports the project's decision-chain mapping and cross-team intelligence aggregation direction, while preserving the requirement for human confirmation of inferred roles and authority.

## Reproducibility

- Normalized observations: `results/real_user_study_observations.csv`
- Pairwise preferences: `results/real_user_study_preferences.csv`
- Machine-readable record and validation summary: `results/real_user_study.json`
- Archived questionnaires: retained in the local assessment archive and intentionally excluded from the public repository
- Importer: `tools/import_real_user_study.py`
