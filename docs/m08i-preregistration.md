# M0.8I: Compact Replacement Serialization

Protocol 0.5. Clean starting evidence `4098407`, annotated `m0.8h`.
Preserve B/C/D/E/F/G/H evidence and execution files byte-for-byte. No evaluation
content, hidden tests/scoring, fresh tasks, Pi work or subsequent experiment.

## Questions and Conditions

Can minimal single-target framing expose more of the frozen 3B Runner's coding
capability without JSON whole-file escaping or repeated path metadata? Co-primary
engineering outcomes: verified candidate formation and public task success.
No confirmatory p-value, equivalence or generalization claim.

A is exact H E1/512, including JSON schema-constrained decoding. B is E2 version
`E2-single-target-compact-1`, with the same full replacement semantics. Both perform
unchanged JSON-schema inspection, INSPECT->ACT, source observation, task semantics,
control state, context policy, generic rejection projection and automatic public
verification. Only in ACT does B use a different output contract and omit backend
JSON constraints. Prompt instructions/tool argument descriptions change only as
needed to describe that contract. Task/public cases and code capability restrictions
are unchanged. No shortening hints, semantic diagnosis or suggested code.

The intervention bundles framing, raw source (no escaping), trusted single-target
resolution, contract-specific prompt text and removal of JSON-constrained decoding
in ACT. It cannot separately establish which subcomponent caused any effect.
This is human-designed scaffold/interface engineering, not a smarter model or
test-time repair. Whole correct replacement code must still come from the model.

## E2 Contract

Exactly one trusted editable source is required; unsafe/multiple/foreign targets
fail before inference. No target is inferred from generated text. The parser
returns the existing internal replace_file action with the trusted path; the
Supervisor still independently authorizes it. No historical registry modification.

Replacement serialization is the literal concatenation:

```text
"REPLACE\n" + complete_source + "\nEND_REPLACE"
```

One optional final transport LF is accepted. The source body is extracted exactly,
including any final source newline; a source ending in LF consequently has a blank
separator line before END_REPLACE. LF marker lines are required; no trimming,
CRLF normalization, commentary removal, code fences, inferred markers, partial
completion, merging, syntax repair or LLM parser. REPLACE/END_REPLACE as whole
lines inside the body are reserved and rejected. Raw UTF-8 is validated; source
bytes are not transformed. Existing 16384-byte transport bound and 8192-byte
Supervisor replacement limit remain. Empty source is not repaired or special-cased.
GIVE_UP, with at most one final LF, maps to finish without a reason. JSON actions,
prose, prefixes/suffixes and incomplete frames remain malformed, ending the window.

Categories, fixed precedence: invalid_utf8, oversized_transport, invalid_target,
give_up, missing_opening_marker, missing_closing_marker (or trailing_content if a
closing marker exists but is not terminal), reserved_marker_in_content, complete_frame.
JSON completeness is measured structurally separately from strict schema/action
validity. A complete frame/JSON at the cap is not automatically a truncation failure.

## Frozen Model and Budgets

Exact H Qwen2.5-Coder 3B digest, Q4_K_M, Ollama 0.35.1, template/system/tokenizer,
temperature 0, seed 42, context 4096, think=false, timeout30s and keep_alive5m.
Both output ceilings remain512. Model discovery identity and generation options
must match H A; only B serialization metadata/protocol and ACT format/messages differ.
No warmup, downloads, sampling, model switch or larger output limit.

Both retain15 decisions/15 tools/16000 measured input+output tokens/120s windows,
one-tool/5s verification reserve, test timeout5s, file/edit8192 bytes, workspace
10485760 bytes and verifier output4096 bytes. Context max/recent/field bounds and
conservative tokenizer admission remain identical. Different contract text can
change prompt length and admission, which is part of interface cost, not a new cap.
Total campaign32 windows/480 calls/512000 tokens/4800s; no resource relaxation.

## Tasks, Schedule and Stop Rules

Exactly H's exposed16 L2 development tasks, original checkpoints and public cases.
Freeze manifest, task data, schema/contract, initial and canonical post-source-read
prompt hashes, model/tokenizer, configs, schedule, code and analysis before inference.
Sort templates and alternate AB/BA starting AB (eight each), two fresh windows per
task. No outcome-dependent ordering, retries, replacements of failures or resume.
Stop at first verified candidate, GIVE_UP, malformed output, budget, STOP or
infrastructure failure. Public failure is terminal: no test-feedback repair.
Interrupted campaign is incomplete, costs retained, never selectively rerun.

## Measures and Analysis

Preserve every generation, including inspection: tokens, cap flag, bytes, raw hash,
backend reason/status, phase, JSON/frame/parser category, valid action/replacement,
authorization, unchanged/changed source, Python syntax versus policy acceptance,
checkpoint, public verification and PASS/FAIL. Unknown telemetry stays unknown.
Ceiling/serialization failure is a terminal malformed ACT at512 tokens with backend
length termination and failed protocol parsing; other failures remain separate.
Frame absence is not proof that an EDIT was attempted. Generation opportunities
are all ACT responses excluding parsed GIVE_UP; full outputs are retained.

Task funnel and proposal/opportunity funnel: tasks/windows -> ACT generation ->
protocol parsed -> authorized replacement -> changed -> syntax/static acceptance
-> checkpoint -> public verification -> PASS/FAIL. Task stages mean at least one
same-response chain; proposal stages count all qualifying responses, including
unparsed ACT opportunities. Recognized replacement counts are separately reported.
Public passes count tasks, not tests, and family coverage counts distinct task families.

Report32 paired windows/16 task rows, by-arm parser categories, saturation and
all token-length distributions. Costs include failures: calls/input/output/total
tokens, inference/window/physical wall, calls/tokens per candidate and tokens/pass.
Zero denominators=null. Repeated generations are identical raw output hashes within
one task/window, not inspection actions shared across different tasks.

For fully parsed replacement outputs only, serialization_overhead_tokens equals
frozen-tokenizer count(raw serialization) minus count(decoded raw source). It is a
deterministic text-token difference, not an additive trace attribution or hidden
reasoning estimate. BPE boundary effects may be negative. Also report serialized/
source token counts and independent framing-token count; no overhead estimate for
malformed/non-ASCII/unknown-counter outputs. State exclusions explicitly.

Progression requires ALL: B>=12 formations, B>=8 public passes, net formations>=4,
at least four fewer ceiling/serialization-failed tasks than fresh A (25 percentage
points defines materially fewer), and B public passes spanning>=6 of8 families.
This gate is descriptive engineering only, not final Runner promotion.

Classification priority: incomplete; strong_E2_result; no_observed_benefit if neither
formation nor public success improves; serialization_improvement_only if material
ceiling improvement and formation gain but public gain<=0 or conditional pass<50%;
correctness_preserved_formation_low if B<12 formations, public count>=A and conditional
public pass>=A; otherwise partial_mixed_development_result. Null conditional rates
cannot meet rate comparisons. All progression checks and raw counts are reported;
classification never erases trade-offs or secondary evidence. Failure of the gate
does not establish equivalence. Non-ceiling frame failures/saturation without failed
parsing are separate and cannot be relabeled after seeing outcomes.

Strong supports separately frozen development confirmation, not final evaluation.
Any non-strong result ends one-factor manual serialization tuning; recommend a
separately preregistered automated scaffold-search, larger-model capability reference
or another evidence-justified factor, without running it. No E3 automatically.
No claim about hidden correctness, final benchmark performance, model-size scaling,
universal primitive superiority or feedback-driven test-time scaling.

## Validation and Delivery

All355 historical tests plus isolated I mocks before inference and again afterward.
Test exact frames/missing markers/no repair/UTF-8/line endings/known target, path
confinement/no-op/syntax/static checks, checkpoint/public verification,512-token
accounting, manifests/schedule/budgets, gate boundaries, STOP/no repeats, hidden/
evaluation/repair exclusion, full mock campaign/export/offline reconstruction.
A initial/post-read prompts and requests must reproduce H; B inspection identical.
Historical acquisition bytecode/controller/Supervisor/evaluator remain unchanged.

Audit all requests/parser results/token counts/receipts/checkpoints/public outcomes,
pairing/order and DB/ZIP/artifact hashes without new inference or verification.
Deliver JSON/CSV/Markdown, model/config/task/prompt/contract freezes, pre/post tests,
consistent SQLite backup-API snapshots, checksums, requirement-by-requirement
completion evidence, final commit/tag and read-only reproduction command.
Keep the evaluation retirement registry absent. Stop after I.
