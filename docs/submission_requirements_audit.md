# Submission requirements audit

Audit date: 2026-09-24

## Status

The workspace contains two course documents:

1. `PE6201_WEN+HAOProject_Problem_Statement_.pdf`
2. `PE6201_Project_Proposal_Watchouts.pdf`

It does **not** contain the separate Final Project Rubric or a final submission brief. The Watch-outs document explicitly tells students to read it alongside the Project Rubric, so the two available PDFs are not sufficient to confirm the final deadline, submission platform, file formats, video duration, or every required artifact.

## Confirmed course requirements and marking signals

| Area | Confirmed information | Source |
|---|---|---|
| Milestone 1 status | The Problem Statement was individual, formative and not graded, but timely submission was mandatory for the End-of-Course Project to count as complete. | Problem Statement page 1; Watch-outs page 1 |
| Criterion 1 | Problem Statement & Significance: 15%. | Watch-outs page 1 |
| Criterion 2 | Business & Technical Trade-offs: 25%. | Watch-outs page 1 |
| Criterion 3 | Implementation - code & repository: 35%. | Watch-outs page 1 |
| Criterion 4 | Demonstration & Communication: 25%. | Watch-outs page 1 |
| Repository | The repository should run on another person's machine. | Watch-outs page 3, pre-submission check 4 |
| Data | Name the data source; for synthetic data, commit the generator, fix ground truth before experiments, vary edge cases and state limitations. | Watch-outs pages 2-3, section 6 |
| Evaluation | Use a value-linked metric with a target and baseline; use a sufficiently large set; avoid grading only self-authored cases. | Watch-outs page 3, section 7 |
| Abstention | Give the system a way to say "I don't know" and measure how often it abstains and whether abstained cases are difficult. | Watch-outs page 3, section 7 |
| Responsible use | Pair each risk with a mitigation; implement guardrails; state intended use, non-use and silent-failure detection. | Watch-outs pages 1 and 3, section 8 |
| Demonstration | Explain limitations and risks during the demonstration; communication is 25% of the mark. | Watch-outs pages 1 and 3 |
| MVP | A smallest end-to-end working version is required even though the Problem Statement template labelled it optional. | Watch-outs page 3, section 9 |
| Proposed project output | The submitted Statement proposed a web dashboard/Slack bot, a one-page briefing, decision-chain confidence, 30-day activity, risk alerts, 1-2 actions, response under 15 seconds and PDF export. | Problem Statement page 3 |
| Proposed evaluation | The submitted Statement proposed a blinded business metric and offline role precision / critical-event recall evaluation. | Problem Statement page 2, section 7 |

## Not confirmed by the available course documents

The following cannot be presented as teacher-mandated requirements until the Final Project Rubric or final submission brief is supplied:

- final project due date and time;
- submission platform and naming convention;
- whether submission is a Git URL, ZIP, PDF report, slide deck, video, live demonstration, or a combination;
- exact video duration, resolution or file format;
- whether a self-appraisal is required and its word limit;
- whether a real participant study is mandatory;
- minimum participant count for a user study;
- whether a release tag is required;
- required report length, citation style or appendix format;
- whether source data and model outputs must be uploaded separately.

The current four-minute video outline, five-person study plan and `v1.0.0` release tag are sensible internal completion targets, not verified course rules.

## Current project coverage against confirmed criteria

| Criterion | Current evidence | Status |
|---|---|---|
| Problem & significance | Scope, primary persona, problem consequences and out-of-scope section | Complete |
| Business & technical trade-offs | Class 5 intake screen, Archetype B classification, build-versus-buy decision, three-layer cost-to-serve, sensitivity analysis, abstention and limitations | Complete; final narration still needs recording |
| Implementation | Reproducible 60-account generator, separate teacher-aligned 10-account set, frozen splits, baseline, model pipeline, signatory ground truth and evaluator, evidence validation, tests and clean-environment verification | Complete |
| Demonstration & communication | Working dashboard, PDF export, demo script and final evaluation chart | Implementation complete; recording not yet produced |

## Required next input

Obtain and add the official Final Project Rubric and final submission instructions to the workspace. After they are supplied, rerun this audit and replace every unconfirmed item with the exact requirement, deadline, format and evidence location.

Until then, do not describe the four-minute duration, five-person sample, self-appraisal or release tag as requirements from the instructor.
