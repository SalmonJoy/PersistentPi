# M0.8E: Larger-Model Capability Control

Protocol 0.5. This is a development diagnostic, not Runner selection or a
confirmatory model trial. M0.8B/C/D outcomes remain immutable. E1 is not advanced.
The historical reference is M0.8D E0 at 7c9c803: 7/16 verified candidates,
[Source-bearing example withheld.]

## Question and Scope

Does qwen2.5-coder:3b form more state-changing candidates than the historical
1.5B E0 Runner on the exact same 16 exposed L2 development tasks? Copy only the
archived development/public snapshots, task hashes and initial checkpoints.
Never open evaluation-task or hidden-test content. No benchmark modification,
repair, Planner, memory, generated tools, sampling, Pi work or 7B inference.

## Frozen Treatment

Obtain only the intended Ollama chat/instruct 3B Q4_K_M tag. Pin its full digest
before inference. Record parameter metadata, stored bytes, raw template/system
metadata and hashes, runtime, tokenizer manifest/blob/hash and laptop resources.
If unavailable, unloadable or incompatible, stop without substitution.
Downloaded before inference: digest
`f72c60cabf6237b07f6e632b2c48d533cef25eda2efbd34bed21c5e9c01e6225`;
local tag metadata: 3.1B, Q4_K_M, 1,929,912,626 stored bytes.

Reuse the historical E0 PrimitiveCampaign.acquire method and original Window,
PrimitiveModel, C3 INSPECT -> ACT, historical generic rejection feedback,
public verifier, Supervisor, task prompt/context packer and strict JSON schema.
One source inspection precedes ACT. Initial messages must hash-identically
match archived E0 messages for every task. Freeze all code/config/input hashes.
The only model-config changes allowed are model tag and expected digest;
Q4_K_M remains fixed. Require identical template/system hashes and tokenizer
hash to retain the historical context/framing policy. Otherwise stop/report.

Ollama 0.35.1; temperature 0, seed 42, context 4096, output 512, think=false,
keep_alive=5m, request timeout 30s. Each fresh window retains 15 decisions,
15 tool calls, 16,000 measured tokens, 120s wall, one tool + 5s verification
reservation, output 4096 bytes, edit 8192 bytes, workspace 10485760 bytes.
No warmup inference. Cold-load time is included in the first live request.

Run once per task in ascending template order. Stop each window at the first
automatically verified candidate (PASS or FAIL), GIVE_UP, malformed response,
or original budget stop. Stop the campaign on STOP/infrastructure/identity
failure; no resume or selective rerun. Total ceilings: 16 windows, 240 calls,
256,000 tokens, 2400s including control/export overhead. Do not increase a
window limit if larger-model latency makes this control impractical. A request
timeout or infrastructure interruption is an operationally incomplete result,
not evidence that the model lacks semantic capability.

## Analysis Fixed Before Inference

Primary: formations/16 minus historical 7/16. Strong descriptive signal requires
at least 13 formations, improvement of at least 4 tasks, and at least 6 families
with formations. Improving but missing this conjunction is intermediate. No
improvement plus persistent unchanged proposals does not justify attributing
the bottleneck primarily to model size. Incomplete data cannot meet the gate.
No p-values, inferential confidence claims, model promotion or automatic next run.

Report task-level pairing and 8-family/16-template coverage; related instances
are not independent evidence. Public correctness is secondary. Funnel stages
are tasks with READ, ACT transition, EDIT, valid/authorized EDIT, state change,
checkpoint, public verification, PASS/FAIL. Rates use the preceding stage as
denominator; PASS/FAIL branch from verification. Report all no-op/repeated
proposals, raw rejection classes, GIVE_UP, malformed stops, calls, input/output
tokens, inference/window/total wall, first changed edit decision and cumulative
[Source-bearing example withheld.]
Account for all failed/rejected actions and preparation/control costs. Compare
archived 1.5B receipts separately, never charge them to new physical expenditure.

## Integrity and Interpretation

Before inference run all existing and added fake-model tests. Validate identity,
unchanged E0 semantics, initial prompt equality, public-only manifest, budgets,
single automatic verification and receipts. Back up SQLite via backup API and
export actions/prompts/telemetry; replay every request and reconcile DB/export,
diagnostics, ordering, costs and history after the campaign. Archive tests,
freeze, manifest, metadata, raw and derived results, checksums and reproduction.

A non-concurrent comparison cannot isolate parameter count from different
weights/training, runtime load/cache/hardware conditions or model-specific
inference behavior. Identical templates/tokenizer reduce but do not eliminate
those confounds. Improvement is evidence of model-dependent acquisition behavior,
not proof that scaling parameters alone caused it. Failure is not equivalence.
No hidden generalization, feedback-driven repair or Pi feasibility claim follows.
Report local 7B availability and measured host headroom only; loading/performance
feasibility remains untested and needs separate authorization. Evaluation stays
sealed. Stop after this milestone.
