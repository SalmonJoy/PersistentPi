> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8E: Larger-Model Capability Control

Implementation `8d7f5bd9ce7a94e9c7afa9f88893e9e4e54b11e5`; protocol 0.5; complete: True.
Freeze `50b544c4693753ab9da97ead40e5b3ecd6bbbbbcf6cdc209b3368d72a7107533`; exact M0.8D public/development manifest `8d14874e09e2379d08261dde4a55428b27536fd70849d456ef37fa6f32ab9cd7`.
Historical non-concurrent descriptive comparison; no 1.5B baseline rerun.

Model `qwen2.5-coder:3b`; digest `f72c60cabf6237b07f6e632b2c48d533cef25eda2efbd34bed21c5e9c01e6225`; Ollama `0.35.1`.
Parameters 3085938688; quantization Q4_K_M; stored bytes 1929912626.
E0 unchanged; temperature 0, seed 42, context 4096, output 512, timeout 30s, think=false.
15 decisions /15 tools /16000 tokens /120s per window; one-tool/5s automatic verification reserve.
Identical initial task messages, model template/system hashes and tokenizer hash checked before inference.

[Source-bearing example withheld.]
|---|---:|---|---|---:|---|---|
| reference | 7 | 0/7 | 118/125 (94.40%) | 141 | 130446/15731 | 221.721/324.093 |
| control | 8 | 0/8 | 62/106 (58.49%) | 122 | 112423/13897 | 350.738/487.016 |

Net formations: 1; paired descriptive outcomes: `{"both": 3, "control_only": 5, "neither": 4, "reference_only": 4}`.
Interpretation: intermediate; strong descriptive threshold met: False.
Threshold fixed before inference: >=13 formations, >=4 net formations, >=6 formation families. No confirmatory statistical test.

## Funnel

| Stage | Historical 1.5B | Live 3B |
|---|---:|---:|
| tasks | 16 | 16 |
| source_inspected | 16 | 16 |
| act | 16 | 16 |
| edit_generated | 16 | 16 |
| schema_valid_edit | 16 | 16 |
| authorized_edit | 16 | 16 |
| state_changing_edit | 7 | 8 |
| checkpoint | 7 | 8 |
| public_verification | 7 | 8 |
| public_pass | 0 | 0 |
| public_fail | 7 | 8 |

Adjacent conversions: `{"control": {"act -> edit_generated": 1.0, "authorized_edit -> state_changing_edit": 0.5, "checkpoint -> public_verification": 1.0, "edit_generated -> schema_valid_edit": 1.0, "public_verification -> public_fail": 1.0, "public_verification -> public_pass": 0.0, "schema_valid_edit -> authorized_edit": 1.0, "source_inspected -> act": 1.0, "state_changing_edit -> checkpoint": 1.0, "tasks -> source_inspected": 1.0}, "reference": {"act -> edit_generated": 1.0, "authorized_edit -> state_changing_edit": 0.4375, "checkpoint -> public_verification": 1.0, "edit_generated -> schema_valid_edit": 1.0, "public_verification -> public_fail": 1.0, "public_verification -> public_pass": 0.0, "schema_valid_edit -> authorized_edit": 1.0, "source_inspected -> act": 1.0, "state_changing_edit -> checkpoint": 1.0, "tasks -> source_inspected": 1.0}}`.
Counts are tasks reaching a stage; PASS/FAIL branch from verification. Historical ACT is implied by the frozen successful-READ controller transition.

## Family and Template Pairing

| Family | Historical formed | 3B formed |
|---|---:|---:|
| boundary_empty | 0 | 0 |
| coupled_conditions | 2 | 1 |
| duplicates_order | 0 | 2 |
| early_returns | 0 | 2 |
| initialization_accumulation | 1 | 1 |
| parsing | 2 | 0 |
| state_machine | 2 | 2 |
| two_functions | 0 | 0 |

| Task / template | 1.5B formed/public | 3B formed/public | 1.5B/3B first-change decisions | 1.5B/3B tokens through change |
|---|---|---|---|---|
| `pbf4279c598a17a1b` boundary_empty/0 | False/None | False/None | None/None | None/None |
| `p46df6b0f3b751b32` boundary_empty/2 | False/None | False/None | None/None | None/None |
| `pbed8c8041893bb09` coupled_conditions/0 | True/fail | False/None | 2/None | 1207/None |
| `pf6839215df063f4b` coupled_conditions/5 | True/fail | True/fail | 2/2 | 1221/1221 |
| `pa3711dba178bbc24` duplicates_order/2 | False/None | True/fail | None/2 | None/1231 |
| `p1c406acaf3c565be` duplicates_order/3 | False/None | True/fail | None/2 | None/1229 |
| `p1a42b789ec32c6bf` early_returns/1 | False/None | True/fail | None/2 | None/1195 |
| `pb82cf852b613b4cc` early_returns/4 | False/None | True/fail | None/2 | None/1188 |
| `pf3d15c2036373df1` initialization_accumulation/2 | True/fail | False/None | 2/None | 1249/None |
| `pdebfa2a239d1a5e8` initialization_accumulation/4 | False/None | True/fail | None/2 | None/1242 |
| `pf1c6ba1a368d939c` parsing/1 | True/fail | False/None | 2/None | 1243/None |
| `p952bd0ab55e4f241` parsing/4 | True/fail | False/None | 2/None | 1245/None |
| `pf3646acffdd8caf8` state_machine/2 | True/fail | True/fail | 2/2 | 1290/1290 |
| `pc7e86cd2c076d412` state_machine/4 | True/fail | True/fail | 6/2 | 6118/1314 |
| `pe55313431f5d2011` two_functions/2 | False/None | False/None | None/None | None/None |
| `p3c0490af86efeb5f` two_functions/4 | False/None | False/None | None/None | None/None |

Null first-change values are right-censored acquisition failures, not zero effort. Templates/families are not independent statistical evidence.

## Behavior and Costs

control: repeated proposals 90; raw rejections `{"Edit is empty, unchanged or too large": 62, "Edit requires exactly one matching occurrence": 24, "Invalid Python syntax": 12}`.
Termination classes: `{"public_fail": 8, "token_budget_exhausted": 8}`.
Cost/formation including failed acquisition windows: `{"candidates": 1.0, "inference_seconds": 43.84221949987499, "input_tokens": 14052.875, "model_decisions": 15.25, "output_tokens": 1737.125, "tokens": 15790.0, "tool_calls": 16.25, "verification_seconds": 0.3573749999923166, "wall_seconds": 60.87699999999313}`.
reference: repeated proposals 108; raw rejections `{"Automatic verification reservation exhausted": 2, "Edit is empty, unchanged or too large": 116}`.
Termination classes: `{"decision_budget_exhausted": 2, "public_fail": 7, "token_budget_exhausted": 7}`.
Cost/formation including failed acquisition windows: `{"candidates": 1.0, "inference_seconds": 31.674361570999995, "input_tokens": 18635.14285714286, "model_decisions": 20.142857142857142, "output_tokens": 2247.285714285714, "tokens": 20882.428571428572, "tool_calls": 21.142857142857142, "verification_seconds": 0.2947142857135207, "wall_seconds": 46.299000000003225}`.

New physical study expenditure only: `{"candidates": 8, "inference_seconds": 350.7377559990001, "input_tokens": 112423, "model_decisions": 122, "output_tokens": 13897, "tokens": 126320, "tool_calls": 130, "verification_seconds": 2.8589999999385327, "wall_seconds": 498.31199999997625}`.
Execution elapsed including export/audit tail: 500.062s.
Inference/verification are components of wall, not additional wall cost. Historical costs are separate; no new baseline cost is charged.
Interruption: None; error: None.

## Conclusions and Limits

Partial formation improvement, below the strong threshold; no model promotion or follow-up is triggered.
Different weights/training, non-concurrent hardware load/cache and latency remain confounds despite identical scaffold and serialization.
No evidence about repair scaling, hidden generalization, final evaluation, Planner effectiveness or Pi inference follows.
All B/C/D evidence preserved; 96 evaluation tasks untouched; no hidden access/scoring, baseline rerun, sampling, 7B, Planner or Pi work.
7B locally installed: False; pre-run available RAM 3386527744 bytes; disk free 42782101504 bytes.
7B operational feasibility is not established: no weights/load/latency or resource-pressure test was authorized. Separate authorization is required.


[Private task-level/operational evidence retained in the research repository.]
