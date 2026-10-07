> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.4 Tiny Model Capability Ladder: Negative Result

## Outcome

All four mandatory models completed the frozen four-task, attempt-budget-1
comparison. Every model executed 60 valid `read_file` actions, never requested an
edit, never reached public verification, and failed both predefined viability
gates. No model was eligible for attempt scaling or leading-model repetition.
**No provisional Pi Runner is selected.** This is a completed negative development
experiment, not evidence that these models cannot code under other scaffolds.

The optional `qwen3:1.7b` condition was excluded before comparison after its
predeclared 300-second download deadline. There was no substitution or retry.
No Pi runtime benchmark, cleanup, optimization, prompt tuning, E1 intervention,
reflection, memory or Planner experiment was performed.

## Provenance and Validation

- M0.3 baseline: clean `d5956d2ef610ef90007c4349d8542979d004c23c`;
  [baseline validation](baseline-validation.json): 117 passed, 0 failed/errors/skipped.
- Annotated `m0.3` points to that commit. Prior experiment artifacts are unchanged.
- Preregistration commit: `3b71169`. [Rules](../../../configs/m04-preregistered.json)
  preceded comparative inference and specified metrics, gates and selection order.
- Implementation and experiment commit: `88e723287cf27ed1e85cf725f84b312c58658950`.
  [Implementation validation](implementation-validation.json): 133 passed,
  0 failures, 0 errors, 0 skips; original six-trial matrix and export checks passed.
- Results/audit commit: `978892c955b1800a4b61985ca52bef77fa47c484`.
  [Final clean-checkout validation](final-validation.json): again 133 passed,
  0 failures/errors/skips, and all original matrix/export acceptance checks passed.
  The subsequent archival change only records this receipt; experiment code is unchanged.
- Runtime: Ollama **0.35.1**, local loopback HTTP; Python **3.11.4**, Windows laptop.
  No current Pi specification or feasibility is inferred.
- [Adapter smoke receipt](adapter-smoke-receipt.json): one first-decision call per
  mandatory model on the prior calibration task `smoke_area`; all successful,
  no actions executed, no benchmark scores assigned.
- [Freeze](freeze.json): harness hash
  `0333a5f36c5d0b5507f5629943f991dfc487c75bf8682e958ec559ae614aad2d`;
  scaffold hash `f2a60de3eca13086bfb6fcb7337e2260d2b1a0d419262b1fa526f07953b0f66c`;
  native schema hash `334949bce843624050d2f267646a9247a0220a233e06fc7180ec3f2858feb4e0`.
- Protected M0.3 prompt, schema, tools, context policy, Runner, Supervisor,
  evaluators, bounded interpreter, fixture versions and migrations were unchanged.
  The adapter adds pinned identity and explicit non-thinking control; legacy
  requests without the new policy remain unchanged.

## Models and Inference

| Condition / Exact Tag | Actual Parameters | Quantization | Stored Bytes | Runtime-Reported Resident Bytes |
| --- | ---: | --- | ---: | ---: |
| M0 / llama3.2:1b | 1,235,814,432 | Q8_0 | 1,321,098,329 | 1,514,584,145 |
| M1 / qwen2.5-coder:0.5b | 494,032,768 | Q4_K_M | 397,821,516 | 481,810,185 |
| M2 / qwen3:0.6b | 751,632,384 | Q4_K_M | 522,653,767 | 930,401,484 |
| M3 / qwen2.5-coder:1.5b | 1,543,714,304 | Q4_K_M | 986,062,089 | 1,166,236,712 |
| M4 / qwen3:1.7b | not measured | not measured | not measured | not measured |

M4 was not installed/evaluated; metadata is not fabricated. Resident values are
Ollama `/api/ps` immediately after each model's primary trials, not measured
process RSS or Pi RAM requirements; each reported the same value for `size_vram`.
Exact identities, full backend templates/defaults and before/after inventories
are preserved in [models.json](models.json). Digests:


[Source-bearing example or private reproduction procedure withheld.]


All models used P1 `runner-json-schema-1` / E0, temperature 0, seed 42,
context 4096, output cap 256, native `think=false`, 30-second request timeout,
5-minute keep-alive, and the same original decision/tool/token/wall/verifier and
context-construction budgets. There were no repairs or hidden thinking outputs.
Qwen3's recorded default is thinking enabled; it explicitly supports false/true.
Llama reports false-only/default-false. Coder thinking metadata was omitted;
it remains unknown rather than inferred. Requests explicitly disabled thinking
for all four models, and every response recorded zero thinking bytes.

Runtime-correct chat templates were used, not forced to match across families.
Template hashes and actual prompt tokens exist for every call. Initial HTTP
messages were byte-identical for matching task/budget states across models;
later messages can differ through measured remaining token budgets and public
observation history. The same experimental information policy was preserved,
not a requirement for identical runtime tokenization/rendered template bytes.

## Action Funnel

Counts per model, four tasks each, attempt budget 1:

| Model | Response | Parse | Schema | Authorized | Applicable | Executed | Edit Requested | Candidate Checkpoint | Public Reached | Public Passed | Hidden Passed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| llama3.2:1b | 60 | 60 | 60 | 60 | 60 | 60 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:0.5b | 60 | 60 | 60 | 60 | 60 | 60 | 0 | 0 | 0 | 0 | 0 |
| qwen3:0.6b | 60 | 60 | 60 | 60 | 60 | 60 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:1.5b | 60 | 60 | 60 | 60 | 60 | 60 | 0 | 0 | 0 | 0 | 0 |

Every task stopped normally at `decision_budget_exhausted` after 15 decisions,
with 15 tool calls and **zero verification attempts consumed**. Attempt budget
is the number of permitted public verification attempts, not an instruction to
generate exactly one model response. All 16 final hidden evaluations failed on
the unchanged initial checkpoints; these are not edited candidate evaluations.
Initial bookkeeping checkpoints do not count as Runner-created candidates.

## Progress, Loops and Gates

Productivity and write attempts use the committed deterministic definitions,
not post-hoc judgments. A first successful source read is productive evidence;
it is not a successful edit or proof of semantic usefulness.

| Model | Schema Rate | Productive Decisions / Rate | Authorized Write Tasks / Rate | Verification Tasks / Rate | Rereads / Rate | Identical Repeats | V1 | V2 | Viable |
| --- | ---: | --- | --- | --- | --- | ---: | --- | --- | --- |
| llama3.2:1b | 100% | 4/60 / 6.67% | 0/4 / 0% | 0/4 / 0% | 56/60 / 93.33% | 56 | fail | fail | no |
| qwen2.5-coder:0.5b | 100% | 4/60 / 6.67% | 0/4 / 0% | 0/4 / 0% | 56/60 / 93.33% | 56 | fail | fail | no |
| qwen3:0.6b | 100% | 4/60 / 6.67% | 0/4 / 0% | 0/4 / 0% | 56/60 / 93.33% | 56 | fail | fail | no |
| qwen2.5-coder:1.5b | 100% | 4/60 / 6.67% | 0/4 / 0% | 0/4 / 0% | 56/60 / 93.33% | 56 | fail | fail | no |

For each model: one unique file inspected per task (four task-local file identities
in aggregate), 60 successful reads, zero source-changing actions, maximum
non-state-changing streak 15. Each task's trace consists of one read of
`src/solution.py` followed by 14 identical rereads without source change. Reread
rates per decision and per successful read are both 93.33%. No intervention
prevented loops. Post-run observer events link each decision to its original call.

V1 requires authorized edits in at least 2/4 tasks; V2 requires public verification
in at least 2/4. No model qualified. Consequently fresh 1/3/5 scaling cohorts and
three leading-model replicates were **not eligible**, not unsuccessfully executed
or missing data. Task recovery and repetition trace/result/token/timing variance
are not measured. No determinism claim is made from temperature 0 or similar traces.
There are no E0 applicability failures because no patches were requested; these
results provide no applicability evidence for a later E0/E1 comparison.

## Costs and Useful Throughput

| Model | Input Tokens | Output Tokens | Total Tokens | Inference Seconds | Load Seconds | Trial Wall Seconds | Public / Hidden Tasks Passed | Solved Tasks/Hour |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| llama3.2:1b | 41,205 | 960 | 42,165 | 27.527 | 0.626 | 37.530 | 0/4 / 0/4 | 0 |
| qwen2.5-coder:0.5b | 40,742 | 1,020 | 41,762 | 22.265 | 7.279 | 38.219 | 0/4 / 0/4 | 0 |
| qwen3:0.6b | 41,222 | 1,192 | 42,414 | 17.312 | 0.625 | 30.078 | 0/4 / 0/4 | 0 |
| qwen2.5-coder:1.5b | 40,742 | 960 | 41,702 | 29.586 | 3.055 | 41.969 | 0/4 / 0/4 | 0 |

Total primary cost: 240 model calls/tool calls, 168,043 tokens, 96.690 inference
seconds, 147.796 summed trial wall seconds. Inference time is runtime-reported
prompt evaluation plus generation; wall time includes each trial's orchestration,
loads and final evaluation, not downloads, tests or report generation. Four smoke
calls are recorded separately and excluded from comparative costs.

**Tokens per solved task and inference seconds per solved task are undefined
(`null`) for every model**, under both public and hidden success definitions.
Solves/hour is zero with the measured positive wall times. Faster read-looping is
not higher useful capability; fixed run order/cache/loading and model/backend
differences constrain timing interpretation.

## Selection and Storage

The exact public-only order was registered before results: higher public-pass
count, higher verification-reach task rate, higher productive-action rate, lower
reported resident bytes, lower stored bytes, lower inference seconds, lower total
tokens. Missing resident data would uniformly fall back to stored size for all
eligible models; exact ties would use ascending model tag. Selection uses primary
budget-1 data only, never hidden outcomes or Pi timing. [Saved selection](model-selection.json)
has `selected: null`; no eligible model exists, so no tie or fallback was invoked.
Hidden measurements were aggregated only after this selection was durably saved.

Before pulls: three installed tags (Llama, Coder 0.5B, unrelated
`nomic-embed-text:latest`), 52,138,110,976 bytes free on C:, Ollama 0.35.1.
Qwen3 0.6B and Coder 1.5B added 1,508,715,856 logical model bytes;
pull durations were 146.719s and 254.015s. Optional Qwen3 1.7B hit 300.063s;
its CLI was stopped, backend cancellation was not guaranteed, and no installed
tag existed in the final post-run inventory. It remains excluded, with no retry.

Preparation-recovery free space was 48,839,168,000 bytes (net decrease
3,298,942,976). [Post-run inventory](post-run-runtime.json) reports
48,827,453,440 bytes free. These net disk changes include possible optional
partial downloads and other activity; they are not attributed entirely to usable
model storage. No model blobs or user files were removed.

A Windows sharing violation interrupted preparation receipt persistence. Both
flushed partial receipts were preserved, the mandatory digests were rechecked,
and recovery made zero additional pull calls. See `models-preparation-partial.json`,
`models-skip-persistence.json`, and `models.json` recovery metadata. This was not a
model failure or permission to rerun comparative trials.


[Private task-level/operational evidence retained in the research repository.]

## Interpretation and Completion Audit

Supported: under this fixed P1/E0 scaffold, all four tested identities showed
perfect interface compliance but the same non-editing failure mode. Neither
tested code specialization nor the tested size increase crossed the minimum
viability threshold. The measured bottleneck is downstream of serialization;
its cause is not established. The negative result is retained without rescue tuning.

Not supported: general coding incapacity; a pure causal effect of parameter count
or specialization; equivalence to large models; benefits of retries, self-improvement,
memory or Planner optimization; an optimal Runner; or Pi hardware feasibility.
Family, quantization, template/tokenizer and backend defaults covary; this small
previously exposed development cohort is not a final-paper benchmark. The shared
scaffold may contribute to the observed behavior, but this comparison does not
test that causal hypothesis.

| Objective Requirement | Evidence / Disposition |
| --- | --- |
| Freeze M0.3 and retain prior records | baseline validation, annotated tag, protected Git diff |
| Fixed P1/E0 across model identities | freeze, all manifests and native schema audit |
| Four mandatory models; optional bounded | inventory, exact digests/metadata, pre-result M4 skip |
| Comparable settings and explicit thinking | 240 raw requests, backend metadata, adapter smoke |
| Frozen parse/sign/total/unique tasks | task-hash checks against M0.3 preregistration |
| Budget-1 trials and complete funnels | 16 finished trials, summary and exported events |
| Deterministic productivity/write/loop definitions | preregistration commit, tests, reconstructed observer events |
| V1/V2, eligible 1/3/5 scaling | all gates fail; no scaling eligible; audited exact trial count |
| Significant E0 evidence without E1 switch | zero edit requests; no such evidence or switch |
| Cost, throughput and undefined zero-success efficiencies | summary and cost table; null ratios verified |
| Public-only viability/selection; hidden measurement only | query audit, reconstructed saved selection, separate final aggregation |
| Leading-model threefold repetition | no leading viable model; conditional requirement ineligible |
| Prior tests and new mocked coverage | implementation and final clean-checkout validations; 133 passing tests, no model-dependent unit tests |
| No Pi benchmark/cleanup | laptop-only pipeline, separate baseline unchanged |
| Saved reports and auditable export | committed records, SQLite and checksummed ZIP paths above |

M0.4 stops here. No subsequent model/scaffold rescue or Pi runtime experiment is
started automatically.
