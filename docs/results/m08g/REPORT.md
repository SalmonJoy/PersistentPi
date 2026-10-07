> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8G: 3B E0 vs E1 Mechanism Test

Executed commit `80526098c899f242dd60c54051f03f59a4424d6a`; protocol 0.5; complete `True`.
Freeze `cde0edc90ebf4f24cb539e0ff1559366e8ba21deffbc16a1f1d200c7925fbe7b`; manifest `8d14874e09e2379d08261dde4a55428b27536fd70849d456ef37fa6f32ab9cd7`; schedule `903aca605086a89244af10e97fc621ac9a5cd3608622ed736a563e6dfed6330a`.
Runner `qwen2.5-coder:3b`; digest `f72c60cabf6237b07f6e632b2c48d533cef25eda2efbd34bed21c5e9c01e6225`; Q4_K_M; Ollama 0.35.1.
Template `47fca52d970e517f889420240f615fa9f8f4c6e2cb062340b9dec6fe266385b5`; system `8559162d10010189cec8cb8adc38358b361db0ad44c4ab34fbfaee002f64eb39`; 1929912626 stored bytes.
Temperature 0; seed 42; context 4096; output 512; think=false; timeout 30s; keep_alive=5m.
Same 16 exposed L2 development tasks. Fresh paired AB/BA windows, not independent benchmark performance evidence.
Historical controller/model/Supervisor/verifier code unchanged. The edit contract, not isolated old-field removal, is the treatment.
15 decisions /15 tools /16000 tokens /120s per window; 32 windows /480 calls /512000 tokens /4800s campaign ceilings.
One-tool/5s automatic verification reserve; first verified candidate terminates; no repair or hidden feedback.

| Arm | Formed /16 | Public pass/fail | Changed/all proposals | Unchanged | Calls | Input/output tokens | Inference/window wall s |
|---|---:|---|---|---:|---:|---|---|
| E0 | 8 | 0/8 | 44/106 | 62 | 122 | 112423/13897 | 348.428/417.639 |
| E1 | 8 | 7/1 | 8/8 | 0 | 32 | 17826/4911 | 118.082/135.013 |


[Private task-level/operational evidence retained in the research repository.]

## Funnels

### task_funnel

| Stage | E0 | E1 |
|---|---:|---:|
| accepted_state_change | 8 | 8 |
| changed | 11 | 8 |
| checkpoint | 8 | 8 |
| edit_generated | 16 | 8 |
| inspected | 16 | 16 |
| mechanically_applicable | 8 | 8 |
| public_fail | 8 | 1 |
| public_pass | 0 | 7 |
| public_verification | 8 | 8 |
| tasks | 16 | 16 |
| valid_authorized | 16 | 8 |

Adjacent conversions: `{"E0": {"accepted_state_change -> checkpoint": 1.0, "changed -> mechanically_applicable": 0.7272727272727273, "checkpoint -> public_verification": 1.0, "edit_generated -> valid_authorized": 1.0, "inspected -> edit_generated": 1.0, "mechanically_applicable -> accepted_state_change": 1.0, "public_verification -> public_fail": 1.0, "public_verification -> public_pass": 0.0, "tasks -> inspected": 1.0, "valid_authorized -> changed": 0.6875}, "E1": {"accepted_state_change -> checkpoint": 1.0, "changed -> mechanically_applicable": 1.0, "checkpoint -> public_verification": 1.0, "edit_generated -> valid_authorized": 1.0, "inspected -> edit_generated": 0.5, "mechanically_applicable -> accepted_state_change": 1.0, "public_verification -> public_fail": 0.125, "public_verification -> public_pass": 0.875, "tasks -> inspected": 1.0, "valid_authorized -> changed": 1.0}}`.

### proposal_funnel

| Stage | E0 | E1 |
|---|---:|---:|
| accepted_state_change | 8 | 8 |
| changed | 44 | 8 |
| checkpoint | 8 | 8 |
| edit_generated | 106 | 8 |
| inspected | 106 | 8 |
| mechanically_applicable | 8 | 8 |
| proposals | 106 | 8 |
| public_fail | 8 | 1 |
| public_pass | 0 | 7 |
| public_verification | 8 | 8 |
| valid_authorized | 106 | 8 |

Adjacent conversions: `{"E0": {"accepted_state_change -> checkpoint": 1.0, "changed -> mechanically_applicable": 0.18181818181818182, "checkpoint -> public_verification": 1.0, "edit_generated -> valid_authorized": 1.0, "inspected -> edit_generated": 1.0, "mechanically_applicable -> accepted_state_change": 1.0, "proposals -> inspected": 1.0, "public_verification -> public_fail": 1.0, "public_verification -> public_pass": 0.0, "valid_authorized -> changed": 0.41509433962264153}, "E1": {"accepted_state_change -> checkpoint": 1.0, "changed -> mechanically_applicable": 1.0, "checkpoint -> public_verification": 1.0, "edit_generated -> valid_authorized": 1.0, "inspected -> edit_generated": 1.0, "mechanically_applicable -> accepted_state_change": 1.0, "proposals -> inspected": 1.0, "public_verification -> public_fail": 0.125, "public_verification -> public_pass": 0.875, "valid_authorized -> changed": 1.0}}`.

Applicability in the funnel is observed successful application, not hypothetical validity. Proposal inspection means a prior complete source read.
Raw actions/results and separate static/reached E0 guard fields are retained in JSON; schema validity is not Python syntax or correctness.

## Failure and Behavioral Metrics

E0 proposal partition: `{"changed": 44, "changed_correct_old": 20, "changed_incorrect_old": 24, "context_mismatch": 24, "syntax_rejection": 12, "terminal_causes": {"accepted": 8, "context_mismatch": 24, "syntax_rejection": 12, "unchanged": 62}, "total": 106, "unchanged": 62}`.
Rates (denominator all EDITs except syntax_changed): `{"changed": 0.41509433962264153, "context_mismatch": 0.22641509433962265, "syntax_all": 0.11320754716981132, "syntax_changed": 0.2727272727272727, "unchanged": 0.5849056603773585}`.
Repeated proposals 90; unique normalized accepted candidate ASTs 8.
Termination classes: `{"public_fail": 8, "token_budget_exhausted": 8}`.
Window cost per formation including failed windows: `{"candidates": 1.0, "inference_seconds": 43.5534377495, "input_tokens": 14052.875, "model_decisions": 15.25, "output_tokens": 1737.125, "tokens": 15790.0, "tool_calls": 16.25, "verification_seconds": 0.2833750000136206, "wall_seconds": 52.204875000003085}`.
Physical receipt cost including shared overhead: `{"candidates": 8, "inference_seconds": 348.4275019959998, "input_tokens": 112423, "model_decisions": 122, "output_tokens": 13897, "tokens": 126320, "tool_calls": 130, "verification_seconds": 2.2670000001089647, "wall_seconds": 423.5304999999644}`.
E1 proposal partition: `{"changed": 8, "changed_correct_old": null, "changed_incorrect_old": null, "context_mismatch": 0, "syntax_rejection": 0, "terminal_causes": {"accepted": 8}, "total": 8, "unchanged": 0}`.
Rates (denominator all EDITs except syntax_changed): `{"changed": 1.0, "context_mismatch": 0.0, "syntax_all": 0.0, "syntax_changed": 0.0, "unchanged": 0.0}`.
Repeated proposals 0; unique normalized accepted candidate ASTs 8.
Termination classes: `{"malformed_model_output": 8, "public_fail": 1, "public_pass": 7}`.
Window cost per formation including failed windows: `{"candidates": 1.0, "inference_seconds": 14.760216499999999, "input_tokens": 2228.25, "model_decisions": 4.0, "output_tokens": 613.875, "tokens": 2842.125, "tool_calls": 4.0, "verification_seconds": 0.2753750000119908, "wall_seconds": 16.876624999989872}`.
Physical receipt cost including shared overhead: `{"candidates": 8, "inference_seconds": 118.08173200000002, "input_tokens": 17826, "model_decisions": 32, "output_tokens": 4911, "tokens": 22737, "tool_calls": 32, "verification_seconds": 2.2030000000959262, "wall_seconds": 140.9375000000291}`.

## Interpretation

Preregistered result: `{"broader_benefit": false, "changed_mechanical_failure_tasks": {"A": 3, "B": 0}, "classification": "no_observed_benefit", "context_failure_tasks": {"A": 2, "B": 0}, "mechanism_confirmed": false, "net_formations": 0, "offsetting_failure": true, "subset_paired_rescues": []}`.
Mechanistic subset is only two exposed tasks; rescue there is a limited diagnostic, not population evidence.
No 13/16 gate, confirmatory p-value, equivalence claim or final Runner promotion. Newly generated E1 code is not the saved E0 new string.
Shared contract change also changes output burden/distribution, wording and prewrite checkpoint; not a pure post-hoc acceptance test.

Recommended single next step: 7B same-scaffold development capability control, separately authorized/preregistered, targeting remaining acquisition/public failures. Observed development public passes qualify the rationale; no global model or E1 promotion.
No sampling recommendation follows from diversity alone; no Planner intervention was tested.
Supported: observed development formations/rejections, paired transitions, public correctness and measured costs under this frozen contract.
Unsupported: general model capacity causality, hidden success, repair/test-time scaling, final model/scaffold selection, Planner/memory/tools or Pi feasibility.
B remains a valid calibration stop; B/C/D/E/F evidence unchanged; 96 evaluation tasks sealed and hidden scoring absent.


[Private task-level/operational evidence retained in the research repository.]
