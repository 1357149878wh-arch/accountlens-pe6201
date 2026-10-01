# Scope decision

## Primary user

A Key Account Manager who has less than 15 minutes to prepare for a customer meeting and cannot manually inspect every CRM note, email, meeting record, and support ticket.

## Core problem

Account information is fragmented across teams and systems. The manager needs a concise, evidence-grounded view of who influences the purchase and what important events occurred recently.

## MVP

One account ID produces one Account Panorama Briefing with:

1. inferred decision roles;
2. a likely commercial signatory selected from the supported economic-buyer predictions;
3. an evidence-linked decision-workflow map and missing-role check;
4. ranked cross-team activity from an explicit 30-day window;
5. deterministic alerts for unresolved tickets, unanswered emails, and competitor signals;
6. one or two suggested next actions;
7. confidence, evidence IDs, explicit limitations, and human-review status;
8. one-page PDF and Slack-ready Markdown exports.

## Non-AI baseline

The baseline maps job-title and interaction keywords to decision roles. It is measured before the LLM workflow and retained as an explicit comparison.

## Out of scope

- live enterprise-system connectors;
- real personal or customer data;
- autonomous actions or outbound communication;
- multi-agent orchestration;
- vector databases and semantic retrieval;
- production authentication and deployment;
- live Slack posting and SSO.

The demo exports a Slack-ready summary but does not transmit it. PDF export is local and contains fictional data only.

## Success criteria

- role Macro-F1 of at least 0.75 on the frozen test set;
- at least 0.15 Macro-F1 improvement over the rules baseline;
- evidence precision of at least 0.90;
- unsupported-claim rate of at most 0.05;
- selective accuracy of at least 0.85 with coverage of at least 0.70;
- p95 latency below 15 seconds;
- estimated model cost below USD 0.05 per briefing.

## Class 5 supplementary gate

The post-freeze validation analysis evaluates the selected commercial signatory separately from the six-class role task. On a future independently labelled pilot, signatory precision must be at least 0.85 and selection rate at least 0.70. This supplementary gate does not alter the pre-registered frozen-test criteria or results.
