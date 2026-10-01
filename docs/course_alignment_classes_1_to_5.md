# PE6201 Classes 1 to 5 alignment

## Conclusion

AccountLens is a bounded AI-assisted workflow, not a full agent. This is a deliberate architecture decision rather than a missing feature. The task has a known sequence, exact per-account filtering is sufficient, one structured model call performs the inference, deterministic code validates the result, and a human retains every consequential decision. This gives the project a clearer evaluation boundary and avoids the compounding reliability, cost and governance risks of an unnecessary multi-step agent.

## Class 1 selecting the AI type

Class 1 says that capability is jagged and must be tested rather than inferred from how easy a task looks to a person. Its four selection questions are output type, available labelled data, cost of being wrong and whether the answer can be checked.

| Class 1 question | AccountLens answer | Design consequence |
|---|---|---|
| What output is needed | A new evidence-grounded briefing plus structured role labels | Use a foundation model with a strict structured-output schema |
| How much labelled data exists | No real enterprise labels; limited fictional ground truth is available for evaluation | Rent model understanding rather than train a production classifier |
| What does being wrong cost | A wrong signatory could redirect account effort, but the prototype cannot act on a system or contact a customer | Show confidence and evidence; require human verification |
| Can the answer be checked | Contact IDs, evidence IDs, schema validity and fictional signatory truth are mechanically checkable | Use automated validation, abstention and frozen evaluation sets |

The project therefore compares a deterministic classifier-like rules baseline with a foundation-model workflow instead of assuming that the model must be better. This follows the Class 1 instruction to build, test and measure.

Sources: `PE6201_C1_Your_intuition_is_wrong.pdf`, pages 10-14; `PE6201_C2_Sorting_vs_making.pdf`, pages 3-10; `PE6201_C5_Choosing_and_close.pdf`, pages 3-11.

## Class 2 the product stack

Class 2 defines seven layers and says that the model is only one layer of the product. AccountLens makes an explicit decision at every layer.

| Layer | AccountLens implementation | Build or rent | Main failure controlled |
|---|---|---|---|
| Compute | Provider infrastructure reached through the API | Rent | Provider availability and latency are surfaced as visible failures |
| Data and embeddings | Fictional account records, schemas and ground-truth labels; embeddings are unnecessary for exact account filtering | Build and own | Dataset checks, fixed IDs and leakage tests |
| Vector store | Not used because one account is selected directly from a small structured dataset | Do not add | Avoid irrelevant retrieval, extra cost and another failure surface |
| Model | Pinned GPT-4o-compatible endpoint | Rent | Frozen prompt/model metadata, abstention and evidence validation |
| Orchestration | Filtering, aggregation, risk rules, schema validation, retries and export | Build and own | Deterministic code paths and explicit failure handling |
| Serving | Local Streamlit demonstration | Build | Narrow single-user scope; production service levels are not claimed |
| Observability and evaluation | Metadata-only logs, frozen splits, B0/M1/M2/H1 comparisons, teacher-aligned set and human pilot | Build and own | Silent failures become measurable results |

The build-versus-buy decision follows the course rule: own the data, orchestration, evaluation and governance; rent commodity compute and the frontier model. Retrieval-augmented generation is not selected because the records are already structured and filtered by exact account ID. Adding embeddings or Pinecone would not improve the measured task.

Sources: `PE6201_Class2_C1_The_modern_AI_stack.pdf`, pages 5-16; `PE6201_Class2_C2_Build_vs_buy.pdf`, pages 2-13; `PE6201_Class2_C3_RAG.pdf`, pages 2-13; `PE6201_Class2_C4_Evals_and_A1.pdf`, pages 2-9.

## Class 3 steering proving and pricing

Class 3 treats prompting as programming in words. It recommends clear instructions, structured output, schema enforcement, validation and an evaluation set written before tuning.

AccountLens applies those requirements as follows:

- the Responses API is constrained by a Pydantic schema;
- every contact must receive exactly one role prediction;
- evidence IDs are validated against the selected account records;
- missing or unsupported claims cause retry or visible failure;
- confidence and abstention are recorded rather than forcing every role;
- development and validation data are separated from the one-time frozen test run;
- L1 checks cover schemas, IDs, evidence precision, exact role labels and automated tests;
- L2 judgement is supplied by a small blinded human pilot and is reported descriptively;
- token use, latency, retries and estimated variable cost are saved with each run.

The project uses a concise schema instead of chain-of-thought or self-consistency. This follows the course cost ladder: structured output is cheap and testable, whereas repeated samples and verbose reasoning multiply the bill. The original frozen 20-account M2 run cost USD 0.321290, or USD 0.016065 per briefing. The separate ten-account teacher-aligned run cost USD 0.125933.

Sources: `PE6201_Class3_C2_Steer_it_and_prove_it.pdf`, pages 3-22; `PE6201_Class3_C3_Token_economics_and_case (1).pdf`, pages 2-7 and 21-24.

## Class 4 workflow versus agent

Class 4 gives two necessary tests for an agent:

1. the model chooses the next step at runtime, so the number and sequence of steps vary with the input;
2. the outside world returns an observation after each step, allowing reality to correct the model.

AccountLens does not meet either test. Its sequence is predefined in code and the model does not choose or invoke tools. The model receives one prepared account context and returns one structured briefing. Validation retries are ordinary recovery logic, not a model-directed thought-action-observation loop. The system also has no write, send, book, pay or CRM-update tool.

| Class 4 test | AccountLens | Result |
|---|---|---|
| Who chooses the sequence | Deterministic application code | Workflow |
| Does the step count vary by model choice | No; the normal path has one inference call | Workflow |
| Does every step receive a tool observation | No model-directed tool loop | Not an agent |
| Can it change the outside world | No; exports are local and require a human | Advisory only |
| Appropriate rung | A single structured call inside a fixed workflow, with deterministic checks | Rung 1, with surrounding software controls |

This choice is consistent with the course instruction to move down the seven-rung ladder only when the rung above cannot do the job. A full agent would add unpredictable paths, quadratic context growth, compounding step errors and a governance cliff at the first write without improving the one-account briefing objective.

The project still adopts the Class 4 hardening principles that apply to workflows: minimum capability surface, code-level constraints, a retry cap, evidence checks, negative cases, loud failure, human gates and no irreversible action.

Sources: `PE6201_Class4_C1_What_is_an_agent_STUDENT (1).pdf`, pages 2-19; `PE6201_Class4_C2_Build_it_and_harden_it_STUDENT (1).pdf`, pages 2-14; `PE6201_Class4_C3_Agent_economics_and_the_case_STUDENT (1).pdf`, pages 2-8.

## Class 5 business case

The likely signatory is an Archetype B output because it manufactures a measurement that source systems do not directly record. The briefing summary is an Archetype A subtask because it replaces a repeated manual reconstruction.

The project now includes the five Class 5 gates:

- worth doing: repeated meeting preparation with a measured directional time saving;
- possible: demonstrated on fictional data, with real data readiness explicitly unproven;
- affordable: variable cost, human fallback and fixed costs are kept separate;
- absorbable: a Key Account Manager verifies evidence and remains accountable;
- killable: signatory, evidence, latency and full-cost stop conditions are written in advance.

The primary supplementary metric is signatory precision on ten instructor-aligned fictional accounts. Recall and selection rate are reported beside precision so omissions remain visible. Cost is presented per successful briefing rather than only per token.

Sources: `PE6201_Class5_C1_Where_is_AI_worth_building_STUDENT (2).pdf`, pages 8-31; `PE6201_Class5_C2_What_does_it_actually_cost_STUDENT (2).pdf`, pages 2-26; `PE6201_Class5_C3_Two_archetypes_and_the_Ant_Group_case_STUDENT (1).pdf`, pages 2-12.

## Resulting project position

The course-aligned description is:

> AccountLens is a bounded, evidence-grounded AI-assisted workflow. It uses one structured foundation-model inference inside deterministic orchestration to infer a likely commercial signatory and decision roles, aggregate cross-team evidence and prepare one briefing for human review. It is intentionally not a full agent because the task does not require model-directed tool selection, a variable action loop or autonomous writes.

No architectural expansion is required for course alignment. The important correction is terminological and evidential: describe the system as a workflow, show its seven-layer product design, connect evaluation to business value and make the human decision boundary explicit.
