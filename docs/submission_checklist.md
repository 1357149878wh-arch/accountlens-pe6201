# Final submission checklist

> Requirement audit: `docs/submission_requirements_audit.md`. The separate Final Project Rubric and final submission brief are not present in the workspace, so exact delivery formats remain unconfirmed.

## Already complete

- [x] Original project title retained throughout the project.
- [x] Synthetic multi-source dataset and deterministic generator.
- [x] Frozen development, validation, and test splits.
- [x] Non-AI baseline and evidence-grounded model variants.
- [x] Frozen prompt, model, and abstention threshold.
- [x] One-time final test execution and documented comparison.
- [x] `true_signatory_contact_id` added to every account and excluded from model prompts.
- [x] Separate teacher-aligned 10-account dataset contains two email threads with CC lists, one attendee list, two tickets, one CRM note and a true signatory per account.
- [x] One-time M2 evaluation completed on the teacher-aligned set; signatory precision, recall and selection rate are all reported.
- [x] Class 5 intake screen, archetype, data-readiness, cost-to-serve, break-even, sensitivity, ownership, and kill conditions documented.
- [x] Classes 1-5 course concepts mapped to implementation evidence and limitations.
- [x] Class 4 classification corrected: bounded workflow, not a full agent.
- [x] Automated tests and dashboard QA.
- [x] README installation and app startup verified in a clean environment.
- [x] Decision-chain, 30-day activity, risks, actions, evidence, and exports.
- [x] Responsible-use notice and mandatory human confirmation.
- [x] Blinded user-study protocol prepared.
- [x] Matched-layout A/B participant packets and private facilitator key prepared.
- [x] Five printable, participant-specific Word questionnaires prepared and visually verified.
- [x] Synthetic evaluator pilot completed and clearly labelled as non-human evidence.
- [x] Five participant-provided completed questionnaires imported and checked for completeness.
- [x] Blinded A/B results decoded, aggregated, and reported with limitations.
- [x] Submission-ready final project report generated in Word format.
- [x] Full four-minute demonstration narration prepared as a provisional script.
- [x] Success, abstention, and failure demo script prepared.
- [x] Self-appraisal draft prepared.

## Actions that still require the student

- [ ] Obtain the official Final Project Rubric and final submission instructions, then confirm deadline, platform, formats and video duration.
- [ ] Record the three demonstrations in `docs/demo_script.md`.
- [ ] Record and edit the final video to the official duration; use four minutes only if no different limit is specified.
- [ ] If required by the final brief, review and personalise `docs/self_appraisal.md` so it accurately reflects individual contribution.
- [ ] Inspect every submission file and ensure `.env` and API keys are absent.
- [ ] Commit the final repository state; create a release tag as a reproducibility aid or if the final brief requires it.

## Final integrity checks

- Do not rerun the frozen test split.
- Do not modify the frozen prompt, model, threshold, or reported test artifacts.
- Keep `true_signatory_contact_id` out of every model prompt and describe the teacher-aligned result as a supplementary fictional-data metric.
- Report the USD 0.016065 figure as observed variable model cost, not full production cost.
- Report the five-person study as a small, participant-provided descriptive pilot; do not claim independent identity/session verification or population-level significance.
- Do not show the API key in the video, screenshots, repository, or report.
- Do not claim that decision-chain edges are verified reporting relationships.
