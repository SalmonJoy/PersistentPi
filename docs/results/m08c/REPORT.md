> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8C acquisition pilot

Implementation commit: `a59adbeae1eb4ea96210b90569dfa02c14f09d75`. Freeze: `eee725692c9971db3cfbae55e2ce36e76e86224462302d0f833059993083fefe`.
Manifest: `ac1c980449c209a4a13ed982b44d473439ad1b12f8b3426352e19686b1c7761a`. Schedule: `a273ab818eb8497cc8147207972c51b6376db4cb3ffebe5abfa46a89761f49b4`.
Complete: True. Progression gate: False.

Runner: `qwen2.5-coder:1.5b`, `Q4_K_M`, Ollama `0.35.1`, digest `d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668`. Temperature 0, seed 42, context 4096, output ceiling 512.

M0.8B remains: no difficulty tier qualified. This is exposed development acquisition evidence.

| Condition | Formations | Public pass/fail | No-ops/repeats | Calls | Input/output tokens | Inference/window wall seconds |
|---|---:|---|---|---:|---|---|
| A | 7/16 | 0/7 | 124/112 | 147 | 136855/16625 | 236.725/348.844 |
| B | 6/16 | 0/6 | 133/121 | 155 | 147164/17873 | 254.129/369.142 |

Paired outcomes: `{"A_win": 1, "both_formed": 6, "neither_formed": 9}`.
Gate: `{"A_formations": 7, "B_families": 4, "B_formations": 6, "B_public_failures": 6, "checks": {"B_families": false, "B_formations": false, "B_public_failures": false, "net_formations": false}, "complete": true, "net_formations": -1, "qualifies": false}`.
Exploratory paired effect/95% interval: `[-0.0625, [-0.125, 0.0]]`.

| Task/template | A formed/public | B formed/public | A/B first changed decision | A/B tokens through change | A/B no-ops before change |
|---|---|---|---|---|---|
| `p5e13b9f98819294d` boundary_empty/0 | False/None | False/None | None/None | None/None | None/None |
| `p34b28cf55210aec1` boundary_empty/2 | False/None | False/None | None/None | None/None | None/None |
| `pa63cfccfadc9b0dc` coupled_conditions/0 | True/fail | True/fail | 2/2 | 1195/1195 | 0/0 |
| `pc0bcb2a4fab9625f` coupled_conditions/5 | True/fail | True/fail | 3/3 | 2053/2054 | 1/1 |
| `p04b147c3e8c0d378` duplicates_order/2 | False/None | False/None | None/None | None/None | None/None |
| `p0954b6525e69e56c` duplicates_order/3 | False/None | False/None | None/None | None/None | None/None |
| `p19748616a72497ae` early_returns/1 | False/None | False/None | None/None | None/None | None/None |
| `p1e61f22b44e3eaee` early_returns/4 | False/None | False/None | None/None | None/None | None/None |
| `p9f571129bbb005d7` initialization_accumulation/2 | True/fail | True/fail | 2/2 | 1249/1249 | 0/0 |
| `p025c66405de3e41f` initialization_accumulation/4 | False/None | False/None | None/None | None/None | None/None |
| `pa866c138ff04432d` parsing/1 | True/fail | True/fail | 2/2 | 1243/1243 | 0/0 |
| `p764fd53ba3e1c1b2` parsing/4 | True/fail | True/fail | 2/2 | 1245/1245 | 0/0 |
| `p42e48770deae3cc5` state_machine/2 | True/fail | False/None | 7/None | 7503/None | 5/None |
| `p97eff6b296a0c4d8` state_machine/4 | True/fail | True/fail | 6/9 | 6118/10316 | 4/7 |
| `pe134b66a3eb4fd3c` two_functions/2 | False/None | False/None | None/None | None/None | None/None |
| `p15ba5a20ecb77266` two_functions/4 | False/None | False/None | None/None | None/None | None/None |

| Family | A formations | B formations |
|---|---:|---:|
| boundary_empty | 0 | 0 |
| coupled_conditions | 2 | 2 |
| duplicates_order | 0 | 0 |
| early_returns | 0 | 0 |
| initialization_accumulation | 1 | 1 |
| parsing | 2 | 2 |
| state_machine | 2 | 1 |
| two_functions | 0 | 0 |

Full secondary diagnostic, checkpoint, cost and audit data are in `results.json` and `paired.csv`.
Post-rejection change rates: `{"A": {"byte_change_rate": 0.02608695652173913, "byte_changed": 3, "eligible": 115, "normalized_change_rate": 0.02608695652173913, "normalized_changed": 3, "normalized_supported": 115}, "B": {"byte_change_rate": 0.016260162601626018, "byte_changed": 2, "eligible": 123, "normalized_change_rate": 0.016260162601626018, "normalized_changed": 2, "normalized_supported": 123}}`.
Cost per formation: `{"A": {"candidates": 1.0, "inference_seconds": 33.81785128542857, "input_tokens": 19550.714285714286, "model_decisions": 21.0, "output_tokens": 2375.0, "tokens": 21925.714285714286, "tool_calls": 22.0, "verification_seconds": 0.31671428570656907, "wall_seconds": 49.83485714285884}, "B": {"candidates": 1.0, "inference_seconds": 42.354865999666664, "input_tokens": 24527.333333333332, "model_decisions": 25.833333333333332, "output_tokens": 2978.8333333333335, "tokens": 27506.166666666668, "tool_calls": 26.833333333333332, "verification_seconds": 0.28899999998975545, "wall_seconds": 61.523666666660574}}`.
Physical cost including recorded preparation overhead: `{"candidates": 13, "inference_seconds": 490.85415499600015, "input_tokens": 284019, "model_decisions": 302, "output_tokens": 34498, "tokens": 318517, "tool_calls": 315, "verification_seconds": 3.950999999884516, "wall_seconds": 722.8750000000582}`.
Execution elapsed including overhead: 735.922 seconds.

Byte request difference and AST normalization are observable proposal changes; neither proves different execution behavior.
A failed progression gate does not establish equivalence. A positive development gate would warrant separately preregistered confirmation.
This pilot does not measure iterative repair, test-time scaling, final benchmark improvement or hidden generalization.

Read-only verification:

[Source-bearing example or private reproduction procedure withheld.]


Fresh reproduction requires a clean checkout of the implementation commit and the archived freeze:

[Source-bearing example or private reproduction procedure withheld.]


The reproduction command deliberately creates new inference expenditure. No follow-up is launched by reporting.

## Accounting Correction

The original live aggregate cost summary consumed a generator while summing fields. It preserved the candidate count but reported zero for the remaining totals. `raw-results.json` preserves the original artifact unchanged. `results.json` reconciles physical costs from immutable model/tool/window receipts and overhead records. Per-task outcomes, diagnostics, condition totals, bootstrap and progression gate are unchanged.

This defect also affected live campaign token/call accounting. Independent per-window limits and the 32-window limit bound the study to 480 calls and 512,000 tokens. Verified expenditure stayed below both; the live wall-clock ceiling operated independently. The counter was fixed after inference and covered by an added regression test. No window was rerun.

Precise feedback formed 6/16 candidates versus baseline 7/16: -6.25 percentage points, zero B wins and one A win. All four progression criteria failed. This pilot provides no support for advancing precise no-op feedback to confirmation. It does not establish equivalence or a universal model/interface limitation.
