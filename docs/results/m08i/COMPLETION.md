> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8I Completion and Integrity

Final evidence is identified by annotated tag `m0.8i` (`git rev-parse m0.8i^{}`).
Executed implementation: `e875cfdd6d40762314002ab6922c78f776694c09`.
Starting evidence: `40984078e96cc4217afca25951f21b1c84571e2a`, annotated `m0.8h`.
Protocol 0.5. One complete fresh 32-window campaign; no selective reruns.

## Paired Outcomes

| Measure | A: E1 JSON | B: E2 Compact |
|---|---:|---:|
| Verified candidates /16 | 6 | 0 |
| Public PASS / FAIL | 5 / 1 | 0 / 0 |
| Public pass given candidate | 83.33% | Undefined |
| Terminal ceiling/serialization failures | 10 | 0 |
| Tasks hitting 512 tokens | 10 | 0 |
| Complete ACT JSON/frame outputs | 6 | 96 |
| ACT parse failures | 10 | 13 |
| Unchanged/changed parsed replacements | 0 / 6 | 0 / 96 |
| Passing bug families /8 | 3 | 0 |
| Model calls | 32 | 125 |
| Input tokens | 17,826 | 98,164 |
| Output tokens | 5,786 | 6,740 |
| Total tokens | 23,612 | 104,904 |
| Inference seconds | 138.089 | 175.375 |
| Window wall seconds | 179.344 | 316.782 |
| Within-window repeated generations | 0 | 78 |
| Calls/candidate | 5.333 | Undefined |
| Tokens/candidate | 3,935.333 | Undefined |
| Tokens/public pass | 4,722.4 | Undefined |

Paired formation: six A-only, ten neither, zero B-only/both. E2's zero public
failures is **not** evidence of correctness: it reached no public verifications.
There are 96 parsed E2 proposals, not 96 candidate attempts. No accepted replacement
or checkpoint was produced. All 32 windows finished under their normal stopping rules.

## Serialization Diagnosis

A: six complete JSON actions; ten length-terminated truncated JSON outputs at512;
ten parse failures; six valid changed replacements; zero unchanged replacements.
B:96 complete frames across all16 tasks, zero missing openings,13 missing closings,
zero oversized/invalid-UTF8/trailing-content/reserved-marker parser categories,
zero512 hits. All complete frames resolved the trusted target correctly.
The96 bodies were changed byte content but not valid accepted Python replacements.

Recorded Supervisor rejections:93 `Invalid Python syntax`, three `Automatic
verification reservation exhausted`. Every complete body contains Markdown code
fences and actual LF newlines; none contains literal backslash-n escapes.
This additional descriptive byte-level audit is recorded in `source-serialization-audit.json`; it
corrects a provisional console interpretation of escaped diagnostic output.
Framing succeeded on every task, but source presentation did not conform to the
raw-Python/no-Markdown contract. The strict parser correctly did not strip fences,
repair syntax, unescape content or infer intended source. No counterfactual cleaned
program was executed or scored. Semantic public correctness of E2 is unmeasured.

B terminal states:13 malformed outputs and three decision-budget exhaustions.
A terminal states:ten malformed outputs, five public passes and one public failure.
B generation lengths:125 calls, min16, median58, p90=68, max73; none near512.
A lengths:32 calls, min16, median36, p90/max512. Full distributions are in JSON.

Task funnels (ACT-generation opportunities, not initial READs):

| Stage | A Tasks | B Tasks | A Proposals | B Proposals |
|---|---:|---:|---:|---:|
| Tasks / ACT generation | 16 | 16 | 16 | 109 |
| Protocol parsed | 6 | 16 | 6 | 96 |
| Authorized replacement | 6 | 16 | 6 | 96 |
| Changed replacement | 6 | 16 | 6 | 96 |
| Syntax/static accepted | 6 | 0 | 6 | 0 |
| Candidate checkpoint | 6 | 0 | 6 | 0 |
| Public Verification | 6 | 0 | 6 | 0 |
| Public PASS / FAIL | 5 / 1 | 0 / 0 | 5 / 1 | 0 / 0 |

REPORT.md and results.json provide conversions, all16 paired task rows, parser
categories, family names and per-generation/proposal evidence.

## Efficiency and Gate

B adds93 model calls,81,292 total tokens and37.286 inference seconds; window wall
increases137.438 seconds. No candidate/pass denominator exists for B; these ratios
are null, not zero. Reduced response framing cost did not produce economic benefit.
For fully parsed outputs, text-token overhead median is21.5 for A (n6, range20-23)
and6 for B (n96, range5-6), independently reconstructed from the frozen tokenizer.
This counts transport text minus extracted body text, not hidden reasoning or an
additive attribution. The B body includes invalid Markdown fences, counted as body
tokens rather than frame overhead. These are different, outcome-selected samples;
the medians do not establish total serialization savings for equivalent programs.
Malformed outputs are excluded from this decomposition (A10, B13).

| Preregistered Progression Criterion | Observed B | Met |
|---|---:|---|
| >=12 verified candidates | 0 | No |
| >=8 public passes | 0 | No |
| >=+4 net formations vs paired A | -6 | No |
| >=4 fewer ceiling/serialization-failed tasks | 10 fewer | Yes |
| Public passes span >=6 bug families | 0 | No |

Frozen classification: **no_observed_benefit**. One of five criteria passes;
strong progression fails. E2 eliminated512 saturation and reduced transport overhead
but did not expose more usable coding capability or preserve E1's observed public
success. This does not establish equivalence or the impossibility of compact
serialization, and it does not diagnose hidden model reasoning.

The mechanical progression check was preregistered specifically for cap-associated
parser failures. Total terminal protocol failures increased from10 to13; this is
not an improvement in all serialization failures. Neither the gate definition nor
its thresholds were changed after observing these outcomes.

End one-factor manual serialization tuning. Recommendation only: separately
preregister an automated scaffold-search experiment with the Runner frozen and
Supervisor/evaluator/logging protected, using independent development confirmation
before promotion. This would test objectively whether candidate/prompt/interface
policies improve formation and public success. It was not implemented or run.
No E3, larger output cap,7B, stochastic sampling, Planner optimization, repair,
final evaluation, hidden scoring or Pi work followed.

## Reproducibility and Requirements

Exact H3B Q4_K_M identity/digest, Ollama0.35.1, temperature0, seed42, context4096,
think=false, chat template/system/tokenizer and options are in model.json/configs.json.
Manifest: `8d14874e09e2379d08261dde4a55428b27536fd70849d456ef37fa6f32ab9cd7`.
Freeze: `2401898c9172a4ed3c7062229e5f6d15d40945da189ac45340df94b38b01aaaf`.
All32 A requests and their outputs byte-match H A across16 tasks. All16 A/B initial
inspection requests and outputs match; post-read task semantics/observations match.
Only B ACT contract messages/tool descriptions and omitted JSON-format constraints
differ. That bundled intervention cannot isolate raw framing from constrained decoding.

| Objective | Authoritative Evidence |
|---|---|
| 1 Preserve B-H | history.json/audit.json; historical tags/files byte-preserved |
| 2 Same exposed16 | tasks.json/manifest.json exactly match H; no new/final tasks |
| 3 Conditions | configs/requests: exact E1/512 A; versioned E2 B; both512 |
| 4 Deterministic parser | m08i_runtime.py freeze, strict parser tests, every output replayed |
| 5 Supervisor | normalized trusted-path E1 actions; old authorization/static/checkpoint/verifier unchanged |
| 6 Scientific boundary | contract-only framing/target handling; no semantic repair |
| 7 Fixed Runner | pre/post identities and per-call digest/runtime receipts agree |
| 8 Hold constant | request-parity.json, initial/post-read prompts, budgets/controller/verifier hashes |
| 9 Pairing | schedule.json, eight AB/eight BA, original checkpoint equality |
| 10 Budgets |15 decisions/tools,16000 tokens,120s,512 ceiling; reserves/byte bounds unchanged |
| 11 Co-primary outcomes | six vs zero candidates; five vs zero public task successes |
| 12 Serialization outcomes | parser categories/raw outputs; full frames, failures, changed/no-op counts above |
| 13 Ceiling analysis |157 measured generation rows; A ten512 hits, B zero |
| 14 Funnels | task/proposal counts/conversions, checkpoints/public outcomes above/REPORT.md |
| 15 Efficiency | receipts, input/output tokens, latency/wall, repeats, frozen counter reconstruction |
| 16 Progression | criteria frozen before inference; one of five satisfied |
| 17 Interpretation | no observed benefit; no equivalence/generalization/repair claim |
| 18 Manual tuning stop | ends here; no E3 or subsequent experiment launched |
| 19 No repair | index1/arm I only; terminal public verification; repair_windows0 |
| 20 Isolation | evaluation_runs0, hidden_scores0; retirement registry absent |
| 21 Tests | pre/post validation receipts and complete test logs |
| 22 Integrity |157 request replays, raw/parser/receipt reconstruction, DB/ZIP/hashes/checkpoints |
| 23 Delivery | report/raw JSON/CSVs, backups/audits/hashes, this document, evidence tag/reproduction |

Preflight 384 tests (355 historical +29 I) passed with zero errors/failures/skips,
zero live inference. Postflight also passed all 384 tests with zero errors, failures
or skips; its receipt and full logs are retained separately.
Offline audit disables HTTP and new verification and reconstructs all157 requests,
parser outcomes and overhead counts from frozen data. Physical totals:157 calls,
128,516 tokens,313.465 inference seconds,525.641 accounted wall seconds;
elapsed527.375s. Below32 windows/480 calls/512000 tokens/4800s. No warmup or retries.
Consistent SQLite backup-API snapshots and ZIP exports agree; all raw failures remain.

Read-only reproduction (no new inference/candidate execution):


[Source-bearing example or private reproduction procedure withheld.]


REPORT.md gives the separately authorized live reproduction procedure. Do not
resume or selectively rerun this campaign. Stop after I.
