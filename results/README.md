# Results directory

Evaluation commands write machine-readable experiment outputs here. Generated JSON result files are excluded from Git and can be reproduced from the frozen data split and experiment configuration.

Real blinded-pilot artifacts:

- `real_user_study_observations.csv`: 40 normalized briefing observations;
- `real_user_study_preferences.csv`: 20 decoded pairwise preferences;
- `real_user_study.json`: profiles, answers, completeness metadata, summaries, and pre-registered target outcomes.

Class 5 supplementary artifacts:

- `signatory_validation.json`: account-level true-signatory selection metrics for B0 and M2 using saved validation predictions;
- `class5_economics.json`: observed variable cost, USD 10 capacity, three-layer cost-to-serve scenarios, and break-even rates.
- `teacher_aligned_baseline.json`: zero-cost rules evaluation on the instructor-aligned ten-account dataset;
- `teacher_aligned_m2.json`: created only after the one-time, ten-call M2 evaluation is explicitly confirmed.

Rebuild both Class 5 artifacts without a model call by running `python tools\evaluate_signatory.py`.
