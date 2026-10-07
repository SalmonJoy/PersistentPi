> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.5 Raw Coding vs Action Selection

## Outcome

**Tiny-model coding capability was demonstrated, narrowly, under A2.** Llama 1B
and Qwen Coder 1.5B each generated a literal patch fixing `sign`; both candidates
passed public and hidden evaluation. Preloading alone did not end read loops.
Direct replacement A3 elicited only GIVE_UP, not incorrect replacement code.

The complete primary matrix ran: 4 models x A1/A2/A3 x 4 unchanged evaluation
tasks, attempt budget 1. All 48 trials terminated normally. There were 272 measured
model calls, no repairs, no length stops, no parser/schema failures, no infrastructure
interruptions, and no extra attempts or model selection. Stop after M0.5; no Pi
benchmark, cleanup, M0.6, Planner, memory, reflection or model download was started.

## Provenance

- Baseline: clean `75c2b33df1dbf281bd139b859f68ac1637802992`.
  [Baseline validation](baseline-validation.json): 133 tests passed,
  zero failures/errors/skips, original six-trial matrix/export checks passed.
- Annotated `m0.4` points to that baseline. M0.4 artifacts and frozen tasks remain
  unchanged. A0 uses the archived M0.4 values, not new reruns.
- Preregistration: `2e929c6`; [rules](../../../configs/m05-preregistered.json)
  record conditions, ceilings, definitions, interpretations and stopping policy
  before comparative inference.
- Implementation/experiment commit: `fa5e74bb98679585f34acf5dab265633a94fb649`.
  [Implementation validation](implementation-validation.json): **153 passed,
  zero failures/errors/skips**, including the original matrix/export acceptance.
- Results/audit commit: `d5c03a836a2941cb7c611802833edbf6dbe59a91`.
  [Final clean-checkout validation](final-validation.json): again **153 passed**,
  zero failures/errors/skips, original matrix/export checks all passed.
  The later archival commit only records this receipt; experiment source is unchanged.
- [Adapter smoke](adapter-smoke-receipt.json): 12 successful first-decision calls
  on calibration-only `smoke_area`, no applied edits or benchmark scores.
- [Freeze](freeze.json) stores exact code, harness, pipeline, preparation and plan
  hashes. [Completion audit](completion-audit.json) verifies them against current
  source and reconstructs requests, choices, candidates, metrics and interpretation.
- Runtime: **Ollama 0.35.1**, loopback local HTTP; Python **3.11.4**, Windows laptop.

## Models and Template Audit

No tags or weights were substituted. All exact M0.4 digests remained installed.
Live `/api/show` audit precedes the experiments; full templates, system prompts,
GGUF metadata, parameter counts and quantization are in [preparation.json](preparation.json).

| Model Tag | Parameter Count | Quantization | Template Hash | Instruction / Chat Evidence |
| --- | ---: | --- | --- | --- |
| llama3.2:1b | 1,235,814,432 | Q8_0 | `002858ff9991640c703e2dc700d5f09f82ff20eb42d8eb039af605b962b55fa1` | metadata declares Instruct; chat template |
| qwen2.5-coder:0.5b | 494,032,768 | Q4_K_M | `47fca52d970e517f889420240f615fa9f8f4c6e2cb062340b9dec6fe266385b5` | metadata declares Instruct; chat template + system prompt |
| qwen3:0.6b | 751,632,384 | Q4_K_M | `7d324826d81029e9cc04696166b97b66637ec0178f32f85c8c56ab61dc4141a1` | chat/thinking configured; finetune label absent, not established from this field |
| qwen2.5-coder:1.5b | 1,543,714,304 | Q4_K_M | `47fca52d970e517f889420240f615fa9f8f4c6e2cb062340b9dec6fe266385b5` | metadata declares Instruct; chat template + system prompt |

Both Coder models have `general.finetune: Instruct`, chat-role templates and the
same helpful-assistant system metadata, whose hash is
`8559162d10010189cec8cb8adc38358b361db0ad44c4ab34fbfaee002f64eb39`.
The base-model repository fields describe their base ancestry, not proof these
installed weights are base-only. This is metadata-declared instruction tuning
and observed runtime chat configuration, not independently verified training
provenance. Missing Qwen3 finetune metadata does not establish it is a base model.


[Source-bearing example or private reproduction procedure withheld.]


All models use runtime-correct templates, temperature 0, seed 42, context 4096,
explicit native `think=false`, 30s request timeout, original resource/context/test
budgets and a common **512-token output ceiling** for A1/A2/A3. No thinking output
occurred. Source files are 53-158 bytes; original-sized replacement JSON is 90-199
bytes (~45-100 tokens at 2 bytes/token) and whole-file patch JSON 172-390 bytes.
512 gives margin even at conservative one byte/token for original-sized patches;
it is not a guarantee for arbitrary expanded code. Actual length stops were zero.
Archived A0 keeps 256, a declared comparability limitation.

## Condition Matrix

A1 supplies all permitted initial files, including public tests, but retains normal
P1/E0 actions. A2 supplies exactly the same files and permits one EDIT or GIVE_UP.
A3 supplies those same files and permits complete replacement of the fixed target
or GIVE_UP, without tool selection. Accepted A2/A3 changes get trusted automatic
public verification, not another model call. No hidden information is preloaded.

Counts and rates per four tasks. EDIT means literal patch selection; A3 replacement
selections were zero. All GIVE_UP decisions were valid model decisions.

| Model | Condition | READ | EDIT | GIVE_UP | Valid Change / Rate | Verify / Rate | Public / Rate | Hidden / Rate |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |
| llama3.2:1b | A1 | 60 | 0 | 0 | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% |
| llama3.2:1b | A2 | 0 | 4 | 0 | 1/4 / 25% | 1/4 / 25% | 1/4 / 25% | 1/4 / 25% |
| llama3.2:1b | A3 | 0 | 0 | 4 | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% |
| qwen2.5-coder:0.5b | A1 | 60 | 0 | 0 | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% |
| qwen2.5-coder:0.5b | A2 | 0 | 4 | 0 | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% |
| qwen2.5-coder:0.5b | A3 | 0 | 0 | 4 | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% |
| qwen3:0.6b | A1 | 60 | 0 | 0 | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% |
| qwen3:0.6b | A2 | 0 | 4 | 0 | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% |
| qwen3:0.6b | A3 | 0 | 0 | 4 | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% |
| qwen2.5-coder:1.5b | A1 | 60 | 0 | 0 | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% |
| qwen2.5-coder:1.5b | A2 | 0 | 4 | 0 | 1/4 / 25% | 1/4 / 25% | 1/4 / 25% | 1/4 / 25% |
| qwen2.5-coder:1.5b | A3 | 0 | 0 | 4 | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% | 0/4 / 0% |

Valid change/rate is the preregistered edit-generation metric: nonempty changed
candidate accepted by Supervisor, not merely requesting EDIT or emitting syntax.
The two valid changes produced two distinct candidate checkpoints, changed the
target file, and were executable by the public verifier. A1 created no candidate
checkpoint; A3 generated no replacement code or checkpoint. Initial bookkeeping
checkpoints are not model candidates.

Every A1 task still performed 15 reads of unchanged `src/solution.py`: one read
and 14 identical parsed-action repeats. Each model had 56/60 repeated decisions
(93.33%), with initial code already supplied. This is not a determinism claim.
All 16 A1 trials exhausted decisions; A2 stopped after one decision and either
rejection or automatic verification; A3 stopped normally at GIVE_UP.

A0 archived values for every model: 60 valid executed reads, zero edits/checkpoints/
verification/passes, 6.67% productive actions and 93.33% rereads, original cap 256.
No A0 prompt/action behavior was retuned. Automated regression tests compare
default adapter payloads exactly to all four archived M0.4 initial smoke requests.

## Candidate Quality and Task Results

| A2 Model | Syntax Valid Proposals | Syntax Invalid | Syntax Unknown | Bounded Policy Failures | Accepted Changes | Executable Candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| llama3.2:1b | 1 | 1 | 2 | 0 | 1 | 1 |
| qwen2.5-coder:0.5b | 2 | 0 | 2 | 1 | 0 | 0 |
| qwen3:0.6b | 2 | 0 | 2 | 0 | 0 | 0 |
| qwen2.5-coder:1.5b | 4 | 0 | 0 | 1 | 1 | 1 |

Syntax-valid counts include unchanged proposals; they do not imply nine useful
modifications. Syntax unknown means the patch did not establish a post-edit
candidate (e.g. unmatched or empty old text), not syntax failure. Policy failures
here count syntax-valid but unsupported candidates separately from invalid syntax.
A1/A3 supply no modification syntax evidence, not 32 syntax-failed candidates.

Exact public-stage disposition by task (all in A2):

| Model | parse | sign | total | unique |
| --- | --- | --- | --- | --- |
| llama3.2:1b | unmatched old text | public + hidden pass | unmatched old text | invalid Python syntax |
| qwen2.5-coder:0.5b | unchanged | unmatched old text | duplicate functions rejected by policy | unmatched old text |
| qwen3:0.6b | unmatched old text | unchanged | unchanged | empty edit |
| qwen2.5-coder:1.5b | unchanged | public + hidden pass | unchanged | unsupported `set` call |

Fourteen rejections: five unmatched patches, six empty/unchanged requests, one
syntax error, two bounded-policy rejections. No protected-path violation occurred
live; mocked tests enforce path protections independently. Raw outputs/actions,
quality records and exact rejection errors are preserved in completion-audit.json.

The two accepted sign patches corrected both positive and negative branches;
Llama used two `if` branches and Coder 1.5B used `if/elif/else`. The audit proves
checkpoint contents equal the literal model patch and only the permitted source
changed; no repair supplied the solution. Checkpoints:


[Source-bearing example or private reproduction procedure withheld.]


**Public test failures by task: none among tested candidates.** Only two public
verifications ran; both passed with zero unittest assertion failures/errors.
The other 46 trials never reached public verification. They are not failed public
test executions. Hidden evaluation ran after normal termination for all 48:
two changed-candidate passes and 46 failures of unchanged initial checkpoints.
The latter do not establish 46 incorrect generated implementations.

## Costs

| Model | Condition | Input Tokens | Output Tokens | Inference Seconds | Trial Wall Seconds |
| --- | --- | ---: | ---: | ---: | ---: |
| llama3.2:1b | A1 | 48,210 | 963 | 30.237 | 40.874 |
| llama3.2:1b | A2 | 1,872 | 257 | 4.691 | 6.953 |
| llama3.2:1b | A3 | 1,832 | 32 | 0.709 | 2.251 |
| qwen2.5-coder:0.5b | A1 | 47,788 | 1,020 | 22.165 | 38.641 |
| qwen2.5-coder:0.5b | A2 | 1,847 | 289 | 3.052 | 4.859 |
| qwen2.5-coder:0.5b | A3 | 1,807 | 32 | 0.558 | 2.359 |
| qwen3:0.6b | A1 | 48,268 | 1,004 | 19.106 | 32.813 |
| qwen3:0.6b | A2 | 1,879 | 297 | 3.314 | 5.344 |
| qwen3:0.6b | A3 | 1,839 | 32 | 0.470 | 2.062 |
| qwen2.5-coder:1.5b | A1 | 47,788 | 960 | 31.336 | 50.390 |
| qwen2.5-coder:1.5b | A2 | 1,847 | 319 | 5.323 | 8.031 |
| qwen2.5-coder:1.5b | A3 | 1,807 | 32 | 0.860 | 2.734 |

Total primary cost: **206,784 input + 5,237 output = 212,021 tokens**;
**121.821 inference seconds**, **197.311 summed trial wall seconds**;
272 measured generations, 258 tool calls, two verification attempts. Inference
means prompt evaluation + generation reported by runtime; wall includes control,
preloading, loads and evaluation. Twelve smoke calls and full test/report time are
excluded. Auto verification has real tool/wall cost but no synthetic LLM call.
Conditions intentionally differ in control/decision opportunities; these numbers
are not a matched-compute performance benchmark or Pi timing forecast.

## Diagnosis and Limits

Preregistered public-only flags, saved before private aggregation:

- Case 1: supported for Llama 1B and Coder 1.5B: A1 read-only, A2 publicly solves.
  Action-selection/contract/control is a major current bottleneck; some latent
  coding ability exists and the A0 result did not establish intrinsic incapacity.
- Case 2: not supported; A3 solved nothing.
- Case 3: not supported; no condition reliably generated accepted changes on
  >=50% tasks while failing all public tests.
- Case 4 operational predicate: true, because A3 supplied no accepted change.
  **Do not elevate this to universal model coding incapacity:** all A3 outputs
  were abstentions, while A2 yielded two successful candidates. It is evidence
  against this current direct-replacement protocol eliciting the required behavior,
  not proof the models cannot synthesize replacement code under another contract.
- Case 5: supported in this small diagnostic: two identities publicly solve under
  restriction and two do not. This is not a causal specialization/size conclusion.

These flags are not mutually exclusive. Broad Case 4 wording cannot override the
positive A2 evidence. No larger model, selected Runner or next experiment follows.

Answers to the milestone questions: (1) yes, source-preloaded models still read
repeatedly; (2) yes, all selected EDIT when READ was unavailable in A2;
(3) yes, two nonempty policy-valid modifications were synthesized, plus other
syntax-valid but unchanged/unsupported proposals; (4) two reached verification;
(5) two tiny models solved sign under the restricted contract; direct replacement
elicited no code; (6) missing initial information alone is insufficient to explain
the read loop, action-selection/contract is implicated, patch applicability/policy
remain obstacles, and test correctness was not the failing stage for the two
accepted candidates. A3 abstention prevents an isolated raw-replacement-correctness
measurement; the cause of abstention is not established.

Competing explanations not ruled out: effects of action labels/schema/serialization,
instruction framing and abstention preference; removal of several action choices
rather than READ alone; automatic verification vs model-selected verification;
patch matching vs whole-file replacement; output ceiling difference vs A0; bounded
Python exclusions; model family/template/quantization/backend-default covariation;
cache/loading/run order; task difficulty and this tiny, previously exposed cohort.
No repeated-run reliability, general coding ability, optimality, test-time scaling,
Planner improvement or Pi feasibility claim is supported.


[Private task-level/operational evidence retained in the research repository.]

## Completion Coverage

| Requirement | Authoritative Evidence |
| --- | --- |
| Freeze clean M0.4, annotated tag, old tests | baseline receipt, tag, unchanged prior-record diff |
| Archived unchanged A0 | M0.4 records, payload-equality regression tests |
| A1 complete source with normal choices | preload artifacts, payloads, 240 real READ decisions |
| A2 EDIT/GIVE_UP with no READ | native schema, strict parser, independent Supervisor restriction tests |
| A3 literal replacement/GIVE_UP, supervised writes | versioned schema/parser, positive mocked checkpoint/write test, 16 live GIVE_UP decisions |
| Prechosen common ceiling | preparation sizing, preregistration, all raw request options |
| Frozen tasks/models and Coder instruction audit | task hashes, exact digest/template/system metadata audit |
| Full 48-trial budget-1 matrix | SQLite run identities, reconstructed cohort, no extra attempts |
| Behavior/quality/rates/costs/task failures | per-run raw evidence, summaries and tables above |
| Preregistered diagnostic cases, no hidden influence | public-only query/reconstruction audit and immutable public diagnosis |
| Distinct valid GIVE_UP; no repairs | raw decisions, normal termination, zero malformed/infra outcomes |
| All prior and new mocked tests pass | implementation and final clean-checkout validations: 153 passed |
| No Pi/M0.6; optional A2b handled | laptop-only pipeline; preregistered deferral and stopping policy |

M0.5 ends with narrowly demonstrated coding capability and unresolved direct-
replacement abstention. It does not redefine those abstentions as infrastructure
errors or fill missing capability evidence with a broader claim.
