> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8D: E0 versus E1 acquisition ablation

Executed implementation: `bd72bff5f8278cde60d7742022122049121affa0`; protocol 0.5.
Freeze: `e89af5defbb6dc0bf1a09e6c7f91d3f4f47be51e70997890c5ef163952f0e7b0`.
Fresh manifest: `8d14874e09e2379d08261dde4a55428b27536fd70849d456ef37fa6f32ab9cd7`.
Schedule: `903aca605086a89244af10e97fc621ac9a5cd3608622ed736a563e6dfed6330a`.
Complete: True; gate: False.

Runner: `qwen2.5-coder:1.5b`, `Q4_K_M`, Ollama `0.35.1`, digest `d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668`.
Temperature 0, seed 42, context 4096, output 512, think=false. Post-generation identity rechecked.
A: E0-old-new-1; B: E1-replace-file-1. Strict runner-json-schema-1; fixed C3 and automatic public verification.
Both arms project equivalent no-op/oversize errors to the historical generic message. No precise M0.8C feedback.
Fresh means the OTHER L2 instance per development template, not exposed in M0.8C; all were previously calibrated in M0.8B.
Prior B/C outcomes and evaluation cohort remain unchanged. No hidden scoring or repair cycle.

| Arm | Formed /16 | Public pass/fail | Changed rate | No-op proposals/all | Calls | Input/output tokens | Inference/window wall s |
|---|---:|---|---:|---|---:|---|---|
| A | 7 | 0/7 | 43.75% | 118/125 (94.40%) | 141 | 130446/15731 | 221.721/324.093 |
| B | 6 | 1/5 | 37.50% | 141/147 (95.92%) | 163 | 131927/10689 | 158.915/272.374 |

Paired outcomes: `{"A_win": 1, "B_win": 0, "both_formed": 6, "neither_formed": 9}`.
Gate: `{"A_formations": 7, "B_families": 4, "B_formations": 6, "B_public_failures": 5, "checks": {"B_families": false, "B_formations": false, "B_public_failures": false, "net_formations": false}, "complete": true, "net_formations": -1, "qualifies": false}`.
Exploratory formation effect / paired cluster-bootstrap 95% interval: `[-0.0625, [-0.125, 0.0]]`.
No confirmatory p-value; missing the engineering gate is not equivalence.


[Private task-level/operational evidence retained in the research repository.]

## Funnel

| Stage | A | B |
|---|---:|---:|
| authorized_edit | 16 | 16 |
| checkpoint | 7 | 6 |
| edit_generated | 16 | 16 |
| public_fail | 7 | 5 |
| public_pass | 0 | 1 |
| public_verification | 7 | 6 |
| schema_valid_edit | 16 | 16 |
| source_inspected | 16 | 16 |
| state_changing_edit | 7 | 6 |
| tasks | 16 | 16 |

Adjacent conversion rates: `{"A": {"authorized_edit -> state_changing_edit": 0.4375, "checkpoint -> public_verification": 1.0, "edit_generated -> schema_valid_edit": 1.0, "public_verification -> public_fail": 1.0, "public_verification -> public_pass": 0.0, "schema_valid_edit -> authorized_edit": 1.0, "source_inspected -> edit_generated": 1.0, "state_changing_edit -> checkpoint": 1.0, "tasks -> source_inspected": 1.0}, "B": {"authorized_edit -> state_changing_edit": 0.375, "checkpoint -> public_verification": 1.0, "edit_generated -> schema_valid_edit": 1.0, "public_verification -> public_fail": 0.8333333333333334, "public_verification -> public_pass": 0.16666666666666666, "schema_valid_edit -> authorized_edit": 1.0, "source_inspected -> edit_generated": 1.0, "state_changing_edit -> checkpoint": 1.0, "tasks -> source_inspected": 1.0}}`.
Counts mean tasks with at least one qualifying action. PASS/FAIL branch from verification; schema validity is not correctness.

## Families

| Family | A formed | B formed |
|---|---:|---:|
| boundary_empty | 0 | 0 |
| coupled_conditions | 2 | 2 |
| duplicates_order | 0 | 0 |
| early_returns | 0 | 0 |
| initialization_accumulation | 1 | 1 |
| parsing | 2 | 2 |
| state_machine | 2 | 1 |
| two_functions | 0 | 0 |

## Diagnostics and Costs

[Source-bearing example withheld.]
Raw rejections: `{"Automatic verification reservation exhausted": 2, "Edit is empty, unchanged or too large": 116}`.
Window cost per formation, including failed acquisitions: `{"candidates": 1.0, "inference_seconds": 31.674361570999995, "input_tokens": 18635.14285714286, "model_decisions": 20.142857142857142, "output_tokens": 2247.285714285714, "tokens": 20882.428571428572, "tool_calls": 21.142857142857142, "verification_seconds": 0.2947142857135207, "wall_seconds": 46.299000000003225}`.
Physical cost per formation including allocated preparation/control overhead: `{"candidates": 1.0, "inference_seconds": 31.67436157100001, "input_tokens": 18635.14285714286, "model_decisions": 20.142857142857142, "output_tokens": 2247.285714285714, "tokens": 20882.428571428572, "tool_calls": 21.142857142857142, "verification_seconds": 0.2947142857135207, "wall_seconds": 47.44171428572112}`.
Post-rejection proposal changes: `{"byte_change_rate": 0.009174311926605505, "byte_changed": 1, "eligible": 109, "normalized_change_rate": 0.009174311926605505, "normalized_changed": 1, "normalized_supported": 109}`.
B: 141 replacement==current proposals; 130 repeated proposals, 17 within-window unique proposals.
Raw rejections: `{"Automatic verification reservation exhausted": 10, "Replacement is unchanged": 131}`.
Window cost per formation, including failed acquisitions: `{"candidates": 1.0, "inference_seconds": 26.485819832999997, "input_tokens": 21987.833333333332, "model_decisions": 27.166666666666668, "output_tokens": 1781.5, "tokens": 23769.333333333332, "tool_calls": 28.166666666666668, "verification_seconds": 0.2763333333374855, "wall_seconds": 45.3956666666539}`.
Physical cost per formation including allocated preparation/control overhead: `{"candidates": 1.0, "inference_seconds": 26.485819833000008, "input_tokens": 21987.833333333332, "model_decisions": 27.166666666666668, "output_tokens": 1781.5, "tokens": 23769.333333333332, "tool_calls": 28.166666666666668, "verification_seconds": 0.2763333333374855, "wall_seconds": 46.760833333326445}`.
Post-rejection proposal changes: `{"byte_change_rate": 0.007633587786259542, "byte_changed": 1, "eligible": 131, "normalized_change_rate": 0.007633587786259542, "normalized_changed": 1, "normalized_supported": 131}`.

Physical expenditure: `{"candidates": 13, "inference_seconds": 380.6354499950001, "input_tokens": 262373, "model_decisions": 304, "output_tokens": 26420, "tokens": 288793, "tool_calls": 317, "verification_seconds": 3.7210000000195578, "wall_seconds": 612.6570000000065}`.
Execution elapsed including final export/audit/report tail: 616.891s.
window/preparation/shared control receipts; elapsed also includes final export/report tail. Inference and verification are components, not additions to wall.
Costs are not artificially matched: representation changes input/output length and E1 adds a prewrite checkpoint.
Proposal byte/AST diversity does not establish hidden reasoning or semantic equivalence.

## Interpretation

E1 worsens formation; retain E0. Do not keep simplifying primitives without evidence.
E1 predominantly reproduces the existing source as replacement content, without more changed candidates than E0. Removing the redundant old-content field did not resolve the dominant acquisition behavior; this points toward model/action-policy limitations rather than patch matching, without isolating their causal contribution.

No claim about iterative public-test repair, test-time scaling, final benchmark performance, hidden generalization, Planner effectiveness or Pi feasibility follows.
The complete tool contract is the treatment; formatting, token burden and state checks are not separately identified.
The 96 intended evaluation tasks remain sealed. No confirmation, final evaluation, hidden scoring, repair or next experiment is launched.


[Private task-level/operational evidence retained in the research repository.]
