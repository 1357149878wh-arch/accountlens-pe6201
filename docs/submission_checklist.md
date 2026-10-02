# Final submission checklist

Confirmed deadline: Sunday, 4 October, 23:59 Singapore time.

## Complete

- [x] Original Problem Statement included in the private submission package.
- [x] Final report is well structured and exactly 1,200 displayed words.
- [x] Report critiques impact, metric performance, evaluation quality, tuning, difficulties, rough edges, limitations and next steps.
- [x] Original project title retained throughout the project.
- [x] Synthetic 60-account dataset, fixed generator and frozen 30/10/20 splits checked in.
- [x] Separate instructor-aligned 10-account dataset includes CC lists, attendees, tickets, CRM notes and hidden `true_signatory_contact_id` labels.
- [x] Data and evaluation explainers identify inputs, labels, leakage controls, metrics, targets, results, artifact lineage and limitations.
- [x] Baseline, candidate systems, saved evaluation outputs and transparent cost analysis checked in.
- [x] Model, prompt, threshold and frozen test artifacts preserved.
- [x] Product documentation in `README.md` states persona, input, output, architecture, target metrics and reached metrics.
- [x] README includes installation, test and application startup instructions.
- [x] Python source, tools and tests include file- or module-level documentation.
- [x] Class 4 classification corrected to a bounded AI-assisted workflow rather than a full agent.
- [x] Class 5 worth, feasibility, affordability, absorption, killability and cost-to-serve analysis documented.
- [x] Decision-chain, 30-day activity, risks, bounded actions, evidence and exports implemented.
- [x] Responsible-use notice, abstention, evidence validation and mandatory human confirmation implemented.
- [x] Five completed anonymous questionnaires imported and reported with explicit limitations.
- [x] Complete automated suite rerun: 24/24 passed, with no API call and no change to frozen results.
- [x] Private full submission package excludes API keys, `.env`, virtual environments, Git metadata and caches.
- [x] Video narration and operational recording checklist prepared as a separate item.

## Student actions still required

- [ ] Record the final video with face and screen visible at the same time.
- [ ] Keep the video between 2 and 8 minutes; aim for approximately 4-5 minutes.
- [ ] Present the problem, working demo, evaluation, cost, limitations and next step precisely and succinctly.
- [ ] Confirm that no API key, personal data, browser notification or unrelated window is visible.
- [ ] Upload the Problem Statement, report, repository link/private package and video to the course submission location before the deadline.
- [ ] If the submission page specifies a file format, naming convention or resolution, apply it during the final upload.

## Final integrity rules

- Do not rerun or tune against the frozen model test split.
- Do not modify the frozen prompt, model, threshold or reported model-test artifacts.
- Keep `true_signatory_contact_id` and all evaluation labels out of model prompts.
- Describe the signatory result as a supplementary fictional-data evaluation.
- Present USD 0.016065 as observed variable model cost, not full production cost.
- Present the participant study as a small descriptive pilot, not population-level proof.
- State that decision-chain edges are hypotheses rather than verified reporting relationships.
- Keep the private completed questionnaires and facilitator key out of the public GitHub repository.
