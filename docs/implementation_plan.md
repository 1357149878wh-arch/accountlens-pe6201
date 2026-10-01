# Implementation checklist

## Phase 1 - Data and baseline

- [x] Lock the MVP and out-of-scope features.
- [x] Define strict data and briefing schemas.
- [x] Generate 60 fictional accounts with a fixed seed.
- [x] Create 30/10/20 account-level data splits.
- [x] Add adversarial prompt-injection examples.
- [x] Implement a deterministic rules baseline.
- [x] Implement Macro-F1, per-class metrics, coverage, and a confusion matrix.
- [x] Add automated tests.
- [x] Add a demonstration interface.

## Phase 2 - AI briefing

- [x] Obtain an API key and complete one smoke test on a development account.
- [x] Review the structured output on five development accounts.
- [x] Add claim-level evidence validation and retry/failure handling.
- [x] Measure tokens, cost, and latency for every call.
- [x] Create M1, M2, and H1 experiment runners.
- [x] Tune the abstention threshold using only the validation split.

## Phase 3 - Final evaluation

- [x] Freeze the model name, prompt version, and threshold.
- [x] Run the test split exactly once.
- [x] Produce final charts and an error analysis.
- [x] Conduct and import the small blinded user study; report descriptive results and limitations.
- [x] Complete README setup verification on a clean environment.
- [ ] Record success, abstention, and failure demonstrations.
- [ ] Create the final communication artifacts required by the official brief; the current video, self-appraisal, and release-tag plan is provisional.

Prepared but still requiring student execution:

- [x] Create the blinded study protocol and recording sheet.
- [x] Generate matched-layout A/B participant packets and a private randomisation key from validation artifacts.
- [x] Run a reproducible synthetic evaluator pilot on validation artifacts (not human-subject evidence).
- [x] Create success, abstention, and failure demo scripts.
- [x] Draft the self-appraisal and final submission checklist.
- [x] Import five completed anonymous questionnaires and archive normalized real-user-study artifacts.

## Statement-alignment enhancement

- [x] Retain the original full project title in the application and documentation.
- [x] Add an evidence-linked decision-chain workflow map and missing-role detection.
- [x] Restrict operational briefing context to an explicit 30-day window.
- [x] Rank cross-team intelligence by importance and recency.
- [x] Add deterministic unresolved-ticket, unanswered-email, and competitor-signal alerts.
- [x] Limit displayed recommendations to one or two next actions.
- [x] Add one-page PDF export and Slack-ready Markdown export.
- [x] Add relevance feedback and a mandatory human-confirmation boundary.
- [x] Preserve the frozen v2 model, prompt, threshold, and final test artifacts.
