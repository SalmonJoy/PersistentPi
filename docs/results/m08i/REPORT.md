> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8I: Compact Replacement Serialization

Executed `e875cfdd6d40762314002ab6922c78f776694c09`; complete True; protocol 0.5.
Freeze `2401898c9172a4ed3c7062229e5f6d15d40945da189ac45340df94b38b01aaaf`; manifest `8d14874e09e2379d08261dde4a55428b27536fd70849d456ef37fa6f32ab9cd7`; schedule `903aca605086a89244af10e97fc621ac9a5cd3608622ed736a563e6dfed6330a`.
Exact model identity: `{"architecture": "qwen2", "backend_defaults": null, "backend_type": "local_http", "capabilities": ["completion", "tools", "insert"], "declared_context_length": 32768, "digest": "f72c60cabf6237b07f6e632b2c48d533cef25eda2efbd34bed21c5e9c01e6225", "endpoint": "http://127.0.0.1:11434", "format": "gguf", "model": "qwen2.5-coder:3b", "parameter_count": 3085938688, "parameter_size": "3.1B", "provider": "ollama", "quantization": "Q4_K_M", "runtime_version": "0.35.1", "seed_support": "documented_backend_option_not_determinism_guarantee", "seed_value": 42, "settings": {"keep_alive": "5m", "num_ctx": 4096, "num_predict": 512, "temperature": 0, "timeout_seconds": 30}, "stored_bytes": 1929912626, "system_hash": "8559162d10010189cec8cb8adc38358b361db0ad44c4ab34fbfaee002f64eb39", "template_hash": "47fca52d970e517f889420240f615fa9f8f4c6e2cb062340b9dec6fe266385b5", "think": false, "thinking_metadata": null, "thinking_policy": "explicit-false-1"}`.
Both caps512; only ACT serialization changes. INSPECT and E1 internal Supervisor/controller/verifier are unchanged.
B includes raw framing, no path/JSON escaping and removal of JSON-constrained ACT decoding; effects of these subcomponents cannot be separated.

| Arm | Candidates /16 | Public PASS/FAIL | Pass/candidate | Ceiling/serialization failures | Calls | Input/output tokens | Inference/window wall s |
|---|---:|---|---:|---:|---:|---|---|
| E1 JSON | 6 | 5/1 | 0.8333333333333334 | 10 | 32 | 17826/5786 | 138.089/179.344 |
| E2 compact | 0 | 0/0 | None | 0 | 125 | 98164/6740 | 175.375/316.782 |


[Private task-level/operational evidence retained in the research repository.]

## Acquisition and Serialization

### A

Task funnel: `{"conversions": {"authorized -> changed": 1.0, "changed -> syntax_accepted": 1.0, "checkpoint -> public_verification": 1.0, "generation -> protocol_parsed": 0.375, "protocol_parsed -> authorized": 1.0, "public_verification -> public_fail": 0.16666666666666666, "public_verification -> public_pass": 0.8333333333333334, "syntax_accepted -> checkpoint": 1.0, "tasks -> generation": 1.0}, "counts": {"authorized": 6, "changed": 6, "checkpoint": 6, "generation": 16, "protocol_parsed": 6, "public_fail": 1, "public_pass": 5, "public_verification": 6, "syntax_accepted": 6, "tasks": 16}}`.
Proposal/opportunity funnel: `{"conversions": {"authorized -> changed": 1.0, "changed -> syntax_accepted": 1.0, "checkpoint -> public_verification": 1.0, "generation -> protocol_parsed": 0.375, "protocol_parsed -> authorized": 1.0, "public_verification -> public_fail": 0.16666666666666666, "public_verification -> public_pass": 0.8333333333333334, "syntax_accepted -> checkpoint": 1.0}, "counts": {"authorized": 6, "changed": 6, "checkpoint": 6, "generation": 16, "protocol_parsed": 6, "public_fail": 1, "public_pass": 5, "public_verification": 6, "syntax_accepted": 6}}`.
ACT parser categories: `{"JSON_parse_failure": 10, "complete_JSON_action": 6}`.
Complete JSON 6; complete frames 0; parse failures 10; valid/unchanged/changed replacements 6/0/6.
Tasks/generations at512: 10/10; unknown counts 0; within-window repeated generations 0.
Output token distribution: `{"max": 512, "median": 36.0, "min": 16, "n": 32, "p90": 512.0, "sorted": [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 56, 56, 65, 73, 74, 86, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512]}`.
Passing families: `["early_returns", "initialization_accumulation", "state_machine"]`; coverage 3/8.
Terminal reasons: `{"malformed_model_output": 10, "public_fail": 1, "public_pass": 5}`.

Calls/candidate 5.333333333333333; tokens/candidate 3935.3333333333335; tokens/public pass 4722.4.
Serialization overhead-token distribution: `{"max": 23, "median": 21.5, "min": 20, "n": 6, "p90": 23.0, "sorted": [20, 21, 21, 22, 23, 23]}`.
Overhead exclusions: `{"No fully parsed authorized replacement": 10}`.
Physical arm expenditure: `{"candidates": 6, "inference_seconds": 138.08906100000002, "input_tokens": 17826, "model_decisions": 32, "output_tokens": 5786, "tokens": 23612, "tool_calls": 28, "verification_seconds": 2.6550000000279397, "wall_seconds": 193.600999999966}`.

### B

Task funnel: `{"conversions": {"authorized -> changed": 1.0, "changed -> syntax_accepted": 0.0, "checkpoint -> public_verification": null, "generation -> protocol_parsed": 1.0, "protocol_parsed -> authorized": 1.0, "public_verification -> public_fail": null, "public_verification -> public_pass": null, "syntax_accepted -> checkpoint": null, "tasks -> generation": 1.0}, "counts": {"authorized": 16, "changed": 16, "checkpoint": 0, "generation": 16, "protocol_parsed": 16, "public_fail": 0, "public_pass": 0, "public_verification": 0, "syntax_accepted": 0, "tasks": 16}}`.
Proposal/opportunity funnel: `{"conversions": {"authorized -> changed": 1.0, "changed -> syntax_accepted": 0.0, "checkpoint -> public_verification": null, "generation -> protocol_parsed": 0.8807339449541285, "protocol_parsed -> authorized": 1.0, "public_verification -> public_fail": null, "public_verification -> public_pass": null, "syntax_accepted -> checkpoint": null}, "counts": {"authorized": 96, "changed": 96, "checkpoint": 0, "generation": 109, "protocol_parsed": 96, "public_fail": 0, "public_pass": 0, "public_verification": 0, "syntax_accepted": 0}}`.
ACT parser categories: `{"complete_frame": 96, "missing_closing_marker": 13}`.
Complete JSON 0; complete frames 96; parse failures 13; valid/unchanged/changed replacements 96/0/96.
Tasks/generations at512: 0/0; unknown counts 0; within-window repeated generations 78.
Output token distribution: `{"max": 73, "median": 58.0, "min": 16, "n": 125, "p90": 68.0, "sorted": [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 42, 42, 45, 45, 45, 45, 45, 45, 45, 45, 47, 49, 50, 50, 50, 50, 50, 52, 52, 52, 52, 52, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 55, 55, 55, 55, 55, 55, 57, 57, 58, 58, 58, 58, 58, 59, 59, 60, 60, 60, 60, 60, 60, 60, 60, 61, 61, 61, 61, 62, 62, 62, 62, 62, 62, 62, 62, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 70, 71, 71, 71, 73, 73, 73, 73, 73]}`.
Passing families: `[]`; coverage 0/8.
Terminal reasons: `{"decision_budget_exhausted": 3, "malformed_model_output": 13}`.

Calls/candidate None; tokens/candidate None; tokens/public pass None.
Serialization overhead-token distribution: `{"max": 6, "median": 6.0, "min": 5, "n": 96, "p90": 6.0, "sorted": [5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]}`.
Overhead exclusions: `{"No fully parsed authorized replacement": 13}`.
Physical arm expenditure: `{"candidates": 0, "inference_seconds": 175.375450994, "input_tokens": 98164, "model_decisions": 125, "output_tokens": 6740, "tokens": 104904, "tool_calls": 112, "verification_seconds": 0, "wall_seconds": 332.04000000003725}`.

## Interpretation

Frozen progression: `{"checks": {"ceiling_serialization_improvement": true, "formations": false, "net_formations": false, "passing_families": false, "public_passes": false}, "classification": "no_observed_benefit", "conditional_public_pass": {"A": 0.8333333333333334, "B": null}, "family_coverage": 0, "formations": {"A": 6, "B": 0}, "net_formations": -6, "passing_families": [], "public_passes": {"A": 5, "B": 0}, "strong": false, "truncation_failures": {"A": 10, "B": 0}, "truncation_reduction": 10}`.
The strong progression gate was not met. End one-factor manual interface tuning; recommend a separately preregistered automated scaffold-search, larger-model capability reference or another evidence-justified factor. None was launched.
No hidden generalization, final benchmark result, iterative-repair/test-time scaling, model-size effect or final Runner selection is established. Failure is not equivalence.
No E3, extra output limits, sampling, 7B, Planner, Pi, repair or hidden/evaluation experiment. B/C/D/E/F/G/H remain unchanged.
Unknown/unparsed ACT opportunities are not fully expressed EDITs. Syntax acceptance requires successful historical Supervisor application; static policy validity is separately logged.
Overhead is frozen ASCII text-token count(serialization) minus count(decoded source), not hidden reasoning or additive token-trace attribution. BPE boundary effects and exclusions are retained.
Inference/verification are components of wall. Physical totals include control overhead; zero efficiency denominators are null.


[Private task-level/operational evidence retained in the research repository.]
