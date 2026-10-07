> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.7 Results: Deterministic Edit-to-Verify Orchestration

## Conclusion

The explicit-verification failure reproduced on fresh tasks. Automatic verification
converted every accepted V1 edit into an evaluated candidate and removed the
observed orchestration bottleneck. It did not supply a patch or diagnosis.
The engineering gate passed (7/8 accepted-edit tasks AND 7/8 verification tasks).
Verification reach increased by 7/8, exceeding the preregistered material increase
of 4/8. This is descriptive support for H1 on this smoke suite, not a statistical
rejection of H0 or a general result about small models.

Budgets 1, 3 and 5 all solved the same 7/8 public and hidden tasks. There were zero
failed public candidates and zero recovered tasks. The eighth task never produced
an accepted edit. Therefore this suite demonstrates orchestration improvement,
but does not establish whether feedback-grounded repair improves capability.

## Freeze And Protocol

- Annotated `m0.6` points to `6819ea3c8b2cd05a2cdf2b9c514a599ebe41b6f9`.
- Clean baseline: 181 tests passed, zero failures/errors/skips; six-trial formal
  matrix and export audit passed. See `baseline-validation.json`.
- Task/preregistration freeze: `62727ec`, before any live M0.7 generation.
- All live calibration and evaluation used clean implementation commit
  `627cc31fd671d4700a3c20bddcc41513f383ec2d`.
- Final archival commit is obtained with `git log -1 --format=%H --
  docs/research-records/m07/RESULTS.md`; the clean validation receipt records the
  exact final Git commit. It is separate from the live implementation commit.
- Protocol **0.4**: accepted state-changing EDIT -> checkpoint -> public
  verification completes one candidate attempt. Rejected/no-op/malformed actions
  consume relevant decision/tool budgets but no candidate attempt. Historical
  0.1-0.3 records, migrations and meanings are preserved, not reinterpreted.
- Internal `max_attempts` still counts verifier invocations. 0.4 manifests specify
  `candidate_attempt_budget` and versioned `attempt_semantics`. V0 can leave edits
  unverified; an explicit verifier can checkpoint several preceding edits.
- Implementation validation: **203 passing tests**; final suite adds five
  offline-audit regression tests, **208 total**. No unit test needs live Ollama.

Forty-two protected paths remain unchanged relative to M0.6, including previous
task suites and research records, C3, prompts, model adapter, evaluators, telemetry
and exports. Base Supervisor edits are exactly two reviewed protocol-compatibility
conditions. New lifecycle behavior resides in `orchestration.py`; the Manager
selects that Supervisor for 0.4, including injected/mock Runners, and rejects bare
0.4 without a V0/V1 configuration. The read-only audit adds no live calls.

## Fresh Tasks

Twelve tiny pure-Python tasks were mechanically mutated from fixed reference
functions. No live model was used to design/tune the suite. Categories: comparison,
[Source-bearing example withheld.]
branch omission, argument, parsing predicate, collection order, loop boundary.
Each has three public and four hidden fixed cases. The reference is not visible
to the Runner. All 12 mutants failed both test splits; all 12 references passed
both, through 24 trusted ground-truth trials (legacy protocol 0.3, zero live calls).
See `suite-validation.json`, individual fixture `provenance.json`, and
`configs/m07-suite.json` for all task, recipe, source/test and provenance hashes.

Suite SHA-256: `a8fc445613209e691f20f905ac209430a698733b003744883c3e0a7e6163b52f`.
Recipe hash: `caefb5a7d7cb8569309a3309111c244765bb188e4cd57f0bb468a43e375ecce3`.
Deterministic split: sorted IDs, Python `Random(701).shuffle`, first four
calibration, remaining eight evaluation, sorted within each cohort.

Calibration: `00_threshold`, `02_trim`, `03_different`, `09_letters` (all prefixed
`m07_`). Evaluation: `01_difference`, `04_even_count`, `05_smaller`, `06_second`,
`07_division`, `08_shifted_total`, `10_swap`, `11_triangle`.

## Frozen Runner And Conditions

Primary Runner: `qwen2.5-coder:1.5b`, Q4_K_M, 1,543,714,304 parameters.
Digest: `d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668`.
Ollama **0.35.1**, unchanged from M0.6. Template hash
`47fca52d970e517f889420240f615fa9f8f4c6e2cb062340b9dec6fe266385b5`;
system hash `8559162d10010189cec8cb8adc38358b361db0ad44c4ab34fbfaee002f64eb39`.
Full declared/observed identity is in `model.json`; every live call was checked.
No Llama negative-control run or model download was added.

Temperature 0, seed 42, context 4096, output ceiling 512, think=false, timeout
30 seconds, keep-alive 5m. Context construction: 7000-byte prompt bound,
1800-byte fields, four recent observations. Seed support is not a guarantee of
cross-machine/backend determinism.

Both use unchanged C3 INSPECT -> ACT, at most two successful reads or earlier
transition once all editable source paths are observed. Every task has one source;
all trials read it once. READ never reopens. Calibration confirmed implementation
behavior only; no efficacy-driven setting/prompt/task changes followed it.

V0 requires model-selected verification. V1 runs the same fixed public verifier
automatically after accepting a state-changing edit and checkpointing it. It makes
no semantic coding choice, does not interpret failures, select special tests,
generate hints or expose hidden evidence. Before accepted edits, live V0/V1 model
payloads matched byte-for-byte (two calls for seven tasks, all 15 for the unsolved
task). V1 removes model-selected VERIFY from the subsequent action set.

Common per-trial caps: 15 model decisions, 15 tool calls, 16,000 measured tokens,
120 seconds, five-second tests, 10 MiB workspace, 4096-byte test output,
8192-byte edit. V1 reserves a verifier tool call before accepting an edit. STOP,
wall expiry or interruption takes precedence, with orphan edits explicitly logged.
Verification after the final model decision costs a tool call, not inference.
PASS stops before another model call; only public FAIL permits repair. Verifier
infrastructure errors interrupt, not count as coding negatives. No such error or
interruption occurred. Hidden evaluation runs only after Runner termination.

Laptop profile: Windows release 10, AMD64, Python 3.11.4, 16 logical CPUs.
RAM/temperature are unmeasured in this harness. Windows Job Object process cleanup
and bounded-Python restrictions apply; no hard RAM/disk/network isolation or full
OS sandbox is claimed. No Pi inference/software changes were performed.

## Primary Results

| Measurement | V0 / budget 1 | V1 / budget 1 |
| --- | ---: | ---: |
| Tasks | 8 | 8 |
| Reads | 8 | 8 |
| Edit proposals | 112 | 21 |
| Accepted edits / tasks | 7 / 7 | 7 / 7 |
| Rejected edits | 105 | 14 |
| Candidate checkpoints / completed attempts | 0 / 0 | 7 / 7 |
| Public verifications / tasks reached | 0 / 0 | 7 / 7 |
| Public passes | 0 | 7 |
| Hidden passes | 0 | 7 |
| GIVE_UP | 0 | 0 |
| Model calls / tool calls | 120 / 120 | 29 / 36 |
| Input / output tokens | 97,676 / 8,654 | 20,450 / 2,037 |
| Total tokens | 106,330 | 22,487 |
| Inference seconds | 129.200 | 28.570 |
| End-to-end trial wall seconds | 155.687 | 37.547 |
| Calls per accepted edit | 17.142857 | 4.142857 |
| Tokens per accepted edit | 15,190 | 3,212.428571 |
| Calls per verification invocation | null | 4.142857 |
| Tokens per verification invocation | null | 3,212.428571 |
| Model control-action fraction | 0 | 0 |
| Unverified accepted edits | 7 | 0 |

V0 uses 15 calls on each task, then stops at the decision cap. Its hidden
evaluation is of the selected initial checkpoint, not the seven unsubmitted
working edits. Consequently hidden 0/8 does not establish those patches were
incorrect. V1 checkpoints and verifies the edits; seven tasks stop after two
model calls (READ, EDIT). The eighth consumes 15 decisions with no accepted edit.

V1 uses 91 fewer calls (75.83%) and 83,843 fewer tokens (78.85%) than V0.
Inference decreases by 100.630 seconds and trial wall totals by 118.140 seconds.
Timing is descriptive, affected by sequential execution and backend caching.
Tokens include measured prompt and generated tokens, including cached prompt
tokens reported by the backend; they are not GPU-work or paid-token estimates.

Control-action fraction deterministically counts schema-valid model-selected
VERIFY/finish divided by all model decisions. READ/EDIT remain semantic, including
rejected EDIT; malformed calls are separately unclassified. Both fractions are
zero: V0 did not choose control actions at all. The savings are avoided repeated
semantic proposals after accepted edits, not a measured decline in control-action
fraction. Null ratios mean zero denominator, not zero cost. Per-task ratios and
all scalar counters are available in `per-task.csv` and `summary.json`.

## Eligible Scaling Smoke Test

The gate was saved to `public-gate.json` before scaling and before private score
aggregation. Its only thresholds are >=4/8 accepted-edit and verification tasks;
neither public correctness nor hidden score authorizes it. The offline SQL trace
reconstructs that same gate without private result columns/events. Primary V1
budget one is reused, not regenerated. Budgets three and five are independent
trials with all other settings fixed; no task/policy retuning occurred.

| V1 budget | Public / hidden solves | Actual attempts | Recovered / new solves | Calls | Tokens | Inference s | Wall s |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| 1 | 7/8 / 7/8 | 7 | 0 / 0 | 29 | 22,487 | 28.570 | 37.547 |
| 3 | 7/8 / 7/8 | 7 | 0 / 0 | 29 | 22,487 | 30.764 | 38.640 |
| 5 | 7/8 / 7/8 | 7 | 0 / 0 | 29 | 22,487 | 30.872 | 39.031 |

Incremental pooled costs relative to budget one: budget three, 0 tokens,
+2.194 inference seconds, +1.093 wall seconds; budget five, 0 tokens,
+2.302 inference seconds, +1.484 wall seconds. Marginal token/inference/wall cost
per new public or hidden solve is **null/undefined**, because there are no new
solves. Zero incremental tokens is not evidence that repair is free: no repair
cycle was executed. Total calibration plus evaluation: 40 live trials,
288 model calls, 241,718 tokens (81 calls/67,927 tokens calibration; 207 calls/
173,791 tokens evaluation). Ground-truth and unit-test calls are simulated.

`m07_08_shifted_total` repeatedly proposed unchanged edits: V0 had 14 unchanged
edit rejections; each V1 budget had 13 and a final tool-reservation rejection.
It exhausted model decisions, never produced a checkpoint, and received no
verification feedback. The remaining seven tasks passed on their first candidate
under all budgets. Thus there are no first-failure cases from which to estimate
repair efficacy. Do not redesign this observed suite to force a desired result.

## Scope Of Evidence

Supported: this frozen Qwen/C3 configuration failed to select explicit verification
on fresh tasks; deterministic verification tested every accepted V1 edit, passed
the gate, produced seven correct public/hidden outcomes, and reduced recorded
calls/tokens. Extra candidate budgets did not change outcomes on this suite.

Unsupported: general model capability gains, larger/repository-level tasks, a
scaling law, significance, superiority on other models/hardware, effective repair
learning, memory/Planner/tool-generation benefits, or Pi performance. Budget is
visible in context, so independent scaling runs are not guaranteed identical
prefixes even though this run produced the same outcomes/token counts. Constant
decision/tool caps limit usable candidate capacity. Calibration is not evaluation.
No new experiments are selected from hidden scores. M0.7 stops here; no M0.8 work.


[Private task-level/operational evidence retained in the research repository.]
