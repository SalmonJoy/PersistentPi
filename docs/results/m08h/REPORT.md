> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8H: E1 Output Ceiling Ablation

Executed `e1aaea27899a6d60e2e14bf603b9dbe00b57b753`; protocol 0.5; complete True.
Manifest `8d14874e09e2379d08261dde4a55428b27536fd70849d456ef37fa6f32ab9cd7`; freeze `1d2af9d8713ff8ecd998f18518a5dc8409f7bf2c1219c55f0e3e5ea0427aba56`; schedule `903aca605086a89244af10e97fc621ac9a5cd3608622ed736a563e6dfed6330a`.
Exact model identity: `{"architecture": "qwen2", "backend_defaults": null, "backend_type": "local_http", "capabilities": ["completion", "tools", "insert"], "declared_context_length": 32768, "digest": "f72c60cabf6237b07f6e632b2c48d533cef25eda2efbd34bed21c5e9c01e6225", "endpoint": "http://127.0.0.1:11434", "format": "gguf", "model": "qwen2.5-coder:3b", "parameter_count": 3085938688, "parameter_size": "3.1B", "provider": "ollama", "quantization": "Q4_K_M", "runtime_version": "0.35.1", "seed_support": "documented_backend_option_not_determinism_guarantee", "seed_value": 42, "settings": {"keep_alive": "5m", "num_ctx": 4096, "num_predict": 512, "temperature": 0, "timeout_seconds": 30}, "stored_bytes": 1929912626, "system_hash": "8559162d10010189cec8cb8adc38358b361db0ad44c4ab34fbfaee002f64eb39", "template_hash": "47fca52d970e517f889420240f615fa9f8f4c6e2cb062340b9dec6fe266385b5", "think": false, "thinking_metadata": null, "thinking_policy": "explicit-false-1"}`.
Only num_predict differs (512/1024); E1, prompts/schema/controller and 16000-token/15-decision/15-tool/120s windows unchanged.
Historical subset: `{"selection": "G_E1_ACT_length_512_JSON_fail", "source_commit": "00b51ff4e1b22cbddd84b14f0fab0e152b00c265", "source_sha256": "f5c9837324284c687689dbe5ff51ad57d910737110cf60fdcf69d7a32b6ba570", "task_ids": ["p1c406acaf3c565be", "p3c0490af86efeb5f", "p46df6b0f3b751b32", "p952bd0ab55e4f241", "pa3711dba178bbc24", "pbf4279c598a17a1b", "pe55313431f5d2011", "pf1c6ba1a368d939c"]}`. Eight prespecified opaque IDs, not selected using H outcomes.

| Arm | Candidates /16 | Public pass/fail | Pass given candidate | Truncation failures | Calls | Input/output tokens | Inference/window wall s |
|---|---:|---|---:|---:|---:|---|---|
| E1/512 | 6 | 5/1 | 83.33% | 10 | 32 | 17826/5786 | 136.996/152.342 |
| E1/1024 | 6 | 5/1 | 83.33% | 10 | 32 | 17826/10906 | 248.013/260.283 |


[Private task-level/operational evidence retained in the research repository.]

## Historical Truncation Subset

| Task | Arm | Complete output | JSON parsed | Changed replacement | Accepted | Verification | Public |
|---|---|---|---|---|---|---|---|
| `pbf4279c598a17a1b` | A | False | False | False | False | False | None |
| `pbf4279c598a17a1b` | B | False | False | False | False | False | None |
| `p46df6b0f3b751b32` | A | False | False | False | False | False | None |
| `p46df6b0f3b751b32` | B | False | False | False | False | False | None |
| `pa3711dba178bbc24` | A | False | False | False | False | False | None |
| `pa3711dba178bbc24` | B | False | False | False | False | False | None |
| `p1c406acaf3c565be` | A | False | False | False | False | False | None |
| `p1c406acaf3c565be` | B | False | False | False | False | False | None |
| `pf1c6ba1a368d939c` | A | False | False | False | False | False | None |
| `pf1c6ba1a368d939c` | B | False | False | False | False | False | None |
| `p952bd0ab55e4f241` | A | False | False | False | False | False | None |
| `p952bd0ab55e4f241` | B | False | False | False | False | False | None |
| `pe55313431f5d2011` | A | False | False | False | False | False | None |
| `pe55313431f5d2011` | B | False | False | False | False | False | None |
| `p3c0490af86efeb5f` | A | False | False | False | False | False | None |
| `p3c0490af86efeb5f` | B | False | False | False | False | False | None |

## Funnel

| Stage | A | B |
|---|---:|---:|
| action_attempted | 16 | 16 |
| authorized | 6 | 6 |
| changed | 6 | 6 |
| checkpoint | 6 | 6 |
| json_parsed | 6 | 6 |
| output_complete | 6 | 6 |
| public_fail | 1 | 1 |
| public_pass | 5 | 5 |
| public_verification | 6 | 6 |
| syntax_valid | 6 | 6 |
| tasks | 16 | 16 |

ACT candidate-response opportunity is not proof of a fully expressed EDIT; unknown action type remains null. Complete JSON at a ceiling may be structurally complete despite backend length termination.
Conversions: `{"A": {"action_attempted -> output_complete": 0.375, "authorized -> changed": 1.0, "changed -> syntax_valid": 1.0, "checkpoint -> public_verification": 1.0, "json_parsed -> authorized": 1.0, "output_complete -> json_parsed": 1.0, "public_verification -> public_fail": 0.16666666666666666, "public_verification -> public_pass": 0.8333333333333334, "syntax_valid -> checkpoint": 1.0, "tasks -> action_attempted": 1.0}, "B": {"action_attempted -> output_complete": 0.375, "authorized -> changed": 1.0, "changed -> syntax_valid": 1.0, "checkpoint -> public_verification": 1.0, "json_parsed -> authorized": 1.0, "output_complete -> json_parsed": 1.0, "public_verification -> public_fail": 0.16666666666666666, "public_verification -> public_pass": 0.8333333333333334, "syntax_valid -> checkpoint": 1.0, "tasks -> action_attempted": 1.0}}`.

## Output Length and Costs

A: tasks/generations hitting 512 = 10/10; JSON parse failures 10; recognized replacements 6.
Completed >512: 0 tasks/0 generations; lengths `{"max": null, "median": null, "min": null, "n": 0, "p90": null, "sorted": []}`.
All generation lengths: `{"max": 512, "median": 36.0, "min": 16, "n": 32, "p90": 512.0, "sorted": [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 56, 56, 65, 73, 74, 86, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512]}`.
Calls/candidate 5.333333333333333; tokens/candidate 3935.3333333333335; tokens/public pass 4722.4.
Terminal outcomes: `{"malformed_model_output": 10, "public_fail": 1, "public_pass": 5}`.
Physical arm expenditure: `{"candidates": 6, "inference_seconds": 136.995520998, "input_tokens": 17826, "model_decisions": 32, "output_tokens": 5786, "tokens": 23612, "tool_calls": 28, "verification_seconds": 1.2960000000311993, "wall_seconds": 157.4659999999276}`.
B: tasks/generations hitting 1024 = 10/10; JSON parse failures 10; recognized replacements 6.
Completed >512: 0 tasks/0 generations; lengths `{"max": null, "median": null, "min": null, "n": 0, "p90": null, "sorted": []}`.
All generation lengths: `{"max": 1024, "median": 36.0, "min": 16, "n": 32, "p90": 1024.0, "sorted": [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 56, 56, 65, 73, 74, 86, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024]}`.
Calls/candidate 5.333333333333333; tokens/candidate 4788.666666666667; tokens/public pass 5746.4.
Terminal outcomes: `{"malformed_model_output": 10, "public_fail": 1, "public_pass": 5}`.
Physical arm expenditure: `{"candidates": 6, "inference_seconds": 248.01337800000007, "input_tokens": 17826, "model_decisions": 32, "output_tokens": 10906, "tokens": 28732, "tool_calls": 28, "verification_seconds": 1.4209999999729916, "wall_seconds": 265.31500000003143}`.

## Engineering Interpretation

Frozen classification: `{"ceiling_moves": true, "classification": "ceiling_merely_moves", "net_formations": 0, "paired_new_saturation_without_candidate": 8, "partial": false, "public_passes": {"A": 5, "B": 5}, "strong": false, "strong_checks": {"formations": false, "fresh_public_preserved": true, "historical_public_preserved": false, "truncation_reduction": false}, "subset_reduction": 0, "subset_truncation": {"A": 8, "B": 8}}`.
Development diagnostic only: no hidden generalization, final benchmark/model selection, universal E0 superiority, model-size scaling or test-time repair conclusion.
G remains 8/16 each, E1 seven public passes, no known-mismatch rescue. H does not retrospectively revise G.
Recommended next experiment: a separately preregistered development-only acquisition/output-length diagnosis or confirmation. Do not automatically increase beyond1024, switch model or launch repair.
Any lower cost from earlier failure stops is not a demonstrated capability gain; all failed windows are included. Output capacity may change admission while total budget/context stay fixed.
No Planner, memory/tool generation, 7B, sampling, Pi or next experiment. Evaluation cohort remains sealed.


[Private task-level/operational evidence retained in the research repository.]
