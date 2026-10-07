> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.7 Requirement-To-Evidence Audit

This checklist covers the original numbered objective, not a reduced milestone.
Final completion also requires the clean-checkout `scripts/validate.py` receipt
at `.local/m07/final-validation.json`; that receipt is generated after archival
commit so its exact commit and 208-test outcome are authoritative.

| Objective | Evidence inspected / outcome |
| --- | --- |
| 0: freeze M0.6 | Baseline receipt: clean 6819ea3, 181 tests, six-trial/export checks; annotated m0.6 verified by offline audit. Old protected files have zero diff. |
| 1: semantic/mechanical boundary | `orchestration.py` only advances lifecycle and calls fixed verifier; unchanged C3, prompts, evaluator and bounded execution. No line/patch diagnosis. |
| 2: fresh frozen tasks | Twelve mechanical recipes, 4/8 deterministic split, per-file/provenance/task hashes; suite receipt proves 12 buggy fail both / 12 reference pass both, zero live calls. Freeze commit is an ancestor of live commit. |
| 3: exact Qwen | model.json, per-call observed digest/runtime checks, immutable request settings 0/42/4096/512, unchanged 0.35.1/Q4_K_M. |
| 4: optional Llama | Omission preregistered; only Qwen appears in full trial matrix. |
| 5: C3 base/calibration | Read cap two or all sources observed; calibration receipt has eight complete trials; no post-calibration code/policy changes before primary. Every trial has one successful source read. |
| 6: V0/V1 | Mock V0-vs-legacy payload test; live identical pre-accepted prefixes; V0 zero automatic tests, V1 exactly 21 accepted edits/checkpoints/verifications across budgets. |
| 7: no semantic assistance | PREREGISTRATION.md and RESULTS.md document intervention; fixed verifier and bounded output, no diagnostics or patch generation added. |
| 8: candidate semantics | New 0.4 manifest and events; historical protocol tests and unchanged migrations; candidate chains reconciled with usage/attempt tables. |
| 9: primary one-candidate | Sixteen primary runs, same eight task hashes, max_attempts=1, all required counters/costs in summary and CSV. |
| 10: hypotheses | Frozen m07-preregistered.json H0/H1, material reach increase 4/8; observed 7/8. No post-hoc significance claim. |
| 11: engineering gate | Saved public-only gate: V1 7/8 accepted and 7/8 verified, eligible; SQL-trace reconstruction identical. |
| 12: efficiency/control | Per-task and pooled ratios, zero-denominator null, schema-valid VERIFY/finish fraction; rejected semantic edits not relabeled. Audit reconstructs original summary and CSV. |
| 13: conditional repair | Scaling authorized only after both primary cohorts finished and gate saved; no extra budget-one runs; eight runs each for budgets three/five. Mock failed-then-repair and 1/3/5 cap tests pass. |
| 14: bounded public feedback | Public-only context fields <=1800 bytes, prompt <=7000; fixture verifies raw public failure/AssertionError feedback. Live candidates never failed, so no live repair feedback was exercised. |
| 15: scaling/cost smoke | Solve curves 7/8 at each budget; zero recovered/new solves; incremental costs and undefined marginal-per-new-solve costs explicitly reported. No scaling law. |
| 16: stopping | Unit tests cover pass/GIVE_UP/attempt/decision/tool/STOP/infra handling. Live audit rejects model requests after pass/termination and hidden evaluation before termination. |
| 17: no prompt intelligence | Prior prompts/control unchanged, protected diff empty, no task-specific hint or new test-after-edit instruction. |
| 18: private isolation | Gate reconstruction trace has no private result columns; request audit excludes hidden/reference/provenance; hidden evaluation after each Runner ends; first private aggregation in frozen pipeline after authorized scaling finishes. |
| 19: tests | All 181 prior tests +22 implementation/suite tests +5 offline evidence-audit tests. Mock tests cover listed behaviors and do not require Ollama. Full clean validation records total/results. |
| 20: laptop/Pi separation | Formal execution profile is Windows/Python laptop; M0.7 changes confined to PersistentPi. Separate user-requested SSH probes failed and made no Pi changes. |
| 21: seven research answers | RESULTS.md answers reproduction, candidate conversion, cost reduction, public/hidden correctness, lack of recovery and undefined marginal cost. Repair efficacy is unestablished because no first-failure candidates occurred. |
| Final deliverables | RESULTS.md plus full raw/aggregate report, CSV, task/hash envelopes, exact identity, annotated tag, final commit/test receipt, DB/ZIP paths/checksums and offline/live reproduction commands. |

The offline completion audit reads SQLite in query-only mode, replays control
states, reconciles 32 unique finished trials, checks 21 candidate chains and
207 model requests, reconstructs every exported table/checksum, and compares
public gate, summary, curves, CSV and Markdown without adding live calls.
Audit regression fixtures demonstrate rejection of duplicated/reordered
verification, unverified accepted V1 edits and generation after public success.

No Planner, persistent memory, reflection, tool creation, cloud calls, model
change, Pi execution, hidden-result tuning or M0.8 feature was introduced.
No additional task redesign or inference is required to complete this milestone.
