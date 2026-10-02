# Submission requirements audit

Audit updated: 1 October 2026

## Confirmed final submission requirements

The instructor's latest clarification confirms the following requirements.

| Deliverable | Confirmed requirement | Current evidence | Status |
|---|---|---|---|
| Deadline | Sunday, 4 October, 23:59 Singapore time | Final package prepared before the deadline | Ready |
| Problem Statement | Submit the original Problem Statement | `Submission_Documents/Wen_Hao_PE6201_Problem_Statement.pdf` in the private package | Complete |
| Final report | Well-reasoned and well-structured analysis of approximately 1,200 words; +/-10-15% is acceptable | `output/Wen_Hao_AccountLens_Final_Analysis.docx` and matching PDF | Complete at exactly 1,200 displayed words |
| Reasoning depth | Critique impact, metric performance, evaluation quality, difficulties overcome, tuning and rough edges; future path is welcome but optional | Sections 1, 5, 6, 7 and 8 of the final report | Complete |
| Runnable code | Check in runnable code with enough instructions for the instructor or TA | Root `README.md`, dependency files and tested setup commands | Complete |
| Data transparency | Check in the data used and provide an explainer | `data/`, `data/README.md`, `docs/data_dictionary.md`, `docs/data_and_evaluation_guide.md` | Complete |
| Evaluation transparency | Check in the evals used during development and provide an explainer | `results/`, `results/README.md`, `docs/data_and_evaluation_guide.md`, evaluation code and tests | Complete |
| Code documentation | Document code at file and module level; code should be legible to humans and AI agents | Module docstrings across Python source, tools and tests | Complete |
| Product documentation | State persona, input, output, high-level architecture, target metrics and reached metrics in the repository | Product documentation section and Mermaid box diagram in `README.md` | Complete |
| Demo video | Presenter face and computer/mobile screen must both be visible; presentation should be precise, articulate and succinct | Recording materials supplied separately from the private code package | Recording still required |
| Video duration | Target 5 minutes, with a permitted range of 2-8 minutes; only the first 8 minutes will be reviewed if longer | Concise approximately four-minute narration, within the confirmed range | Script complete; recording still required |

## Evidence quality and limitations

The project uses 60 reproducible fictional accounts for development, validation and frozen testing, plus a separate 10-account instructor-aligned signatory set. It checks in the generator, frozen files, hidden ground truth, prompts, saved outputs, metric definitions and artifact lineage. The final configuration was frozen before the 20-account test execution.

The report explicitly critiques the strongest results. Perfect model scores come from controlled fictional data generated from repeated patterns and do not establish production accuracy. The five-person blinded pilot is descriptive because the sample is small, timing is self-reported, responses are highly uniform, and identity or live sessions were not independently verified. Variable API cost excludes integration, monitoring, maintenance, governance and human review.

## Current completion status

The Problem Statement, 1,200-word report, runnable repository, data, evaluation outputs, explainer documentation, product documentation, module documentation and 24-test verification are complete. The remaining student-executed deliverable is the face-and-screen recording and its final upload to the instructor's submission location.

The supplied clarification does not specify a repository naming convention, video resolution, video file format or exact submission platform. Those details should follow the course submission page if it provides additional fields.
