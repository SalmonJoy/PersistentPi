> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8F: 3B Failure Migration Audit

Offline, descriptive audit of immutable M0.8E evidence at `6432243`.
No new model inference, candidate execution, public/hidden tests, evaluation
content inspection or scaffold modification. Historical 1.5B data are the
same 16 development tasks from M0.8D E0, not a rerun or concurrent trial.

## Primary Changed-Edit Funnel

All 106 3B EDIT proposals are reconstructed individually in `analysis.json`
and `3B-proposals.csv`; 62 are unchanged and 44 are changed.

| Stage | Proposals | Conversion from preceding stage |
|---|---:|---:|
| Total EDIT proposals | 106 | - |
| Changed: old != new | 44 | 41.51% |
| Changed with correct old | 20 | 45.45% |
| Applicable under the actual E0 guards | 8 | 40.00% |
| State-changing accepted edits | 8 | 100% |
| Candidate checkpoints | 8 | 100% |
| Public verification | 8 | 100% |
| Public PASS | 0 | 0% of verification |
| Public FAIL | 8 | 100% of verification |

Schema and declared-path authorization succeed for all 44 changed proposals.
Only **18.18% of changed proposals become candidates**. Applicable here means
the complete Supervisor prewrite contract, including syntax/AST policy and
workspace limits, not merely a string replacement that can be constructed.

## Per-Proposal Reconstruction

Each JSON proposal records task/family/template, run and call IDs, decision and
event sequence, exact action/old/new, raw result, source-before hash, E0 match
count, whole-source equality, static and historical applicability, syntax/policy
validation, checkpoint lineage, recorded public outcome, and exact cost receipt.
The stored initial public checkpoint establishes current content. An accepted
replacement is reconstructed in memory and checked against its already-saved
candidate checkpoint. No source file is changed by this audit.

E0 permits an exact **unique substring**, not only a full-file old field.
`correct_old_for_E0` therefore means nonempty old with exactly one occurrence;
`old_matches_full_source` is a separate measurement. In these changed 3B traces,
all 20 correct-old proposals also exactly reproduce the whole source. All 24
incorrect-old proposals have zero occurrences, not ambiguous multiple matches.

For those 24, E0 cannot construct the requested replacement: post-application
syntax is **unknown/not reached**, not false. The E1 content is validated
separately. Historical budget-reservation denials in two 1.5B actions precede
the path/applicability guards; those historical stage values remain unknown.
JSON null and empty CSV cells preserve unknown/not-reached values. No terminal
cause is unknown in this cohort. Static parser results are not telemetry.
Historical syntax-guard reachability and validity are recorded separately:
unchanged/context-rejected proposals have no historical syntax-validity result,
even where their text can be parsed statically. Accepted edits have a recorded
valid guard; syntax rejections have an invalid guard. Not-reached is not invalid.

## Formation Gap and Rejection Taxonomy

| Mutually exclusive 3B terminal cause | Proposals | % of all 106 | Affected tasks |
|---|---:|---:|---:|
| Unchanged: Edit is empty, unchanged or too large | 62 | 58.49% | 5 |
| Context mismatch: Edit requires exactly one matching occurrence | 24 | 22.64% | 2 |
| Syntax rejection: Invalid Python syntax | 12 | 11.32% | 1 |
| Accepted, then recorded public assertion failure | 8 | 7.55% | 8 |
| Unauthorized/path, size, invalid text, no effective change, reservation, other/unknown | 0 | 0% | 0 |

Changed-but-non-candidate partition: **36 proposals / 3 tasks**. Context mismatch
is 24/36 (66.67%) across parsing/1 and parsing/4, 12 repeats of the same EDIT
in each task. Syntax rejection is 12/36 (33.33%) on initialization_accumulation/2.
Repeated rejection is an orthogonal repetition flag, not a second terminal cause;
adding it to this table would double-count failures.

The eight no-candidate tasks ended at the token admission limit. Five repeated
unchanged edits; two repeated context mismatches; one repeated invalid Python.
A binding budget is not evidence that a larger budget would help: no failed
3B window changed its EDIT proposal after rejection.

## Comparison With Historical 1.5B

| Measurement | 1.5B E0 | 3B E0 |
|---|---:|---:|
| Total proposals | 125 | 106 |
| Unchanged | 118 (94.40%) | 62 (58.49%) |
| Changed | 7 (5.60%) | 44 (41.51%) |
| Changed with correct old | 7 | 20 |
| Changed and applicable | 7 | 8 |
| Accepted / verified candidates | 7 | 8 |
| Changed tasks | 7 | 11 |
| Changed mechanical rejections | 0 | 36 across 3 tasks |
| Public passes | 0 | 0 |

The 1.5B raw rejection classes are 116 generic no-op rejections and 2 automatic
[Source-bearing example withheld.]
span 10 tasks, including one task that later forms a candidate. Task counts across
raw causes overlap and must not be summed as disjoint failed-task counts.

Arithmetic explains the proposal-level formation gap: **+37 changed proposals
= +36 changed mechanical rejections +1 net accepted proposal**. This identity
is not a one-to-one causal correspondence between individual model outputs.
The share of changed proposals accepted drops from 7/7 to 8/44.

## Correct Old and E1 Counterfactual

`changed_new_and_correct_old`: **20/44 (45.45%), 9 tasks**. Eight are accepted;
12 on one task fail syntax. `changed_new_but_incorrect_old`: **24/44 (54.55%),
2 tasks**. Those 24 are rejected at the E0 occurrence check.

All 24 exact recorded new strings are **E1_mechanically_eligible_counterfactual**:
2 distinct task-level proposals, each repeated 12 times. They have a declared
source path, text without NUL, different content from the current source,
within-limit old/new file sizes, within-limit total workspace size, and valid
Python under the frozen bounded AST policy. The audit removes no code, repairs
no strings and constructs no on-disk candidate. It uses the exact new field.

Thus, for these saved states and strings, inaccurate old is the sole evidenced
E0 guard preventing otherwise structurally eligible whole-file replacement.
Whether the new values are semantically useful is **unknown**. No public or
hidden counterfactual tests are run. Structural eligibility is not correctness,
and E1 prompts may cause entirely different future model outputs.

Holding these exact outputs fixed, the task-level ceiling is **two additional
formations: 8 -> at most 10/16**, not 24 recoveries and not the M0.8E 13/16 strong
threshold. E1 does not fix the recorded invalid-Python proposal or the five
unchanged-only tasks. This ceiling is not a forecast for a live E1 condition.

## Task-Level Migration

| Historical task outcome | 3B task outcome | Tasks |
|---|---|---:|
| Accepted candidate | Accepted candidate | 3 |
| Accepted candidate | Context mismatch | 2 |
| Accepted candidate | Syntax rejection | 1 |
| Accepted candidate | Unchanged-only, no candidate | 1 |
| Unchanged-only, no candidate | Accepted candidate | 5 |
| Unchanged-only, no candidate | Unchanged-only, no candidate | 4 |

The three mechanically blocked tasks were **previous 1.5B formations**, not
previous no-op-only failures. Five former acquisition failures now form accepted
but publicly incorrect candidates. Four former formations are lost, giving
one net gain. Therefore a literal task-wise claim that all no-op failures migrated
to mechanical failures would be false. The **aggregate distribution** migrates
toward changed mechanical rejection and changed-but-incorrect code; task-level
movement is mixed and non-monotonic. No parameter-count causality is established
by this non-concurrent comparison of different weights/training.

## Recorded Public Failure Bucket

All eight accepted candidates are mechanically admissible and fail at least
one already-recorded public assertion. Across their 64 existing public case
records: **47 AssertionErrors, 17 passes, zero runtime exceptions**. There is
no recorded syntax/runtime/infrastructure verifier failure. This establishes
incorrect public behavior for those candidates, not hidden generalization.

| Task template | Failed /8 | Recorded category |
|---|---:|---|
| coupled_conditions/5 | 6 | assertion failure |
| duplicates_order/2 | 1 | assertion failure |
| duplicates_order/3 | 1 | assertion failure |
| early_returns/1 | 8 | assertion failure |
| early_returns/4 | 8 | assertion failure |
| initialization_accumulation/4 | 8 | assertion failure |
| state_machine/2 | 8 | assertion failure |
| state_machine/4 | 7 | assertion failure |

Per-case evidence is copied from stored public results, not reexecuted. No fixes
are diagnosed or given to a model. Public correctness remains a downstream problem
even if E1 removes some acquisition failures.

## Repetition and Diversity

| Measurement | 1.5B | 3B |
|---|---:|---:|
| Repeated unchanged proposals | 108 | 57 |
| Repeated changed proposals | 0 | 33 |
| Unique changed proposals, task-conditioned | 7 | 11 |
| Changed proposals with parseable old/new ASTs | 7 | 32 |
| Unique normalized changed AST pairs, task-conditioned | 7 | 10 |
| Different EDIT after rejected EDIT | 1/109 (0.92%) | 0/90 (0%) |
| Next EDIT is byte-changing after rejected EDIT | 1/109 (0.92%) | 33/90 (36.67%) |
| Unchanged -> changed transitions | 1 | 0 |
| Changed -> unchanged transitions | 0 | 0 |

The two post-rejection metrics answer different questions. Repeating an identical
changed-but-rejected proposal is not adaptation, even though old!=new remains
true. The 12 invalid-Python proposals have no supported normalized AST pair;
they are not silently grouped as an AST-equivalent program. AST normalization
removes formatting/location differences, not semantic differences. It does not
establish reasoning quality or semantic equivalence. Repetitions are within
tasks; templates/tasks are not treated as independent statistical evidence.

## Cost Migration

Each recorded model call is assigned once by call ID to its completed action.
Inspection is a separate bucket; assigning its 16 calls to EDIT categories would
misattribute cost. Verification has no model inference or tokens.

| Model / category | Model calls | Tokens (input+output) | Inference seconds |
|---|---:|---:|---:|
| 1.5B inspection | 16 | 8225 | 4.921 |
| 1.5B unchanged rejected | 118 | 132184 | 203.597 |
| 1.5B accepted candidate | 7 | 5768 | 13.203 |
| 1.5B changed mechanically rejected | 0 | 0 | 0 |
| 1.5B total | 141 | 146177 | 221.721 |
| 3B inspection | 16 | 8225 | 10.555 |
| 3B unchanged rejected | 62 | 70321 | 194.555 |
| 3B changed mechanically rejected | 36 | 41989 | 121.236 |
| 3B accepted candidate | 8 | 5785 | 24.391 |
| 3B total | 122 | 126320 | 350.738 |

The 3B mechanical-rejection bucket splits into context mismatch: 24 calls,
28340 tokens, 82.388 inference seconds; syntax rejection: 12 calls, 13649 tokens,
38.848 seconds. Token shares are 55.67% unchanged rejection, 33.24% changed
mechanical rejection, 4.58% accepted-edit inference, and 6.51% inspection.
Together **88.91% of tokens generate rejected proposals**.

Recorded public verification: 7 tool calls / 2.063 seconds for 1.5B; 8 / 2.859
seconds for 3B. Both have zero model calls/tokens/inference in that bucket.
Inference means recorded prompt-evaluation plus generation duration, excluding
load duration. Verification is not added to inference.

The 3B physical window wall is 487.016 seconds, plus 11.296 preparation/control
seconds = 498.312 receipt wall. Historical E0 is 324.093 + 7.999 = 332.092 seconds.
These sums include inference and verification: they must not be added again.
Timing is descriptive and non-concurrent. This audit consumes **zero new model
calls/tokens**; all numbers above are historical expenditure, not new audit cost.

## Decision Table and Ranked Options

| Observed failure pattern | Recommended next experiment |
|---|---|
| Changed new, wrong old dominates changed non-candidate proposals | 3B E0 vs E1 |
| Changed edits accepted, then semantic public failure dominates | 7B same-scaffold capability control |
| 1.5B greedy collapse is primary and alternatives are mechanically viable | Separate stochastic 1.5B ablation |
| No dominant testable mechanism | Planner experiment or stop manual tuning |

**1. Option A: development-only 3B E0 vs E1. Recommended single next experiment.**
Wrong old accounts for 24/36 (66.67%) of changed-but-non-candidate proposals and
2/3 affected tasks; all exact new strings satisfy the E1 structural guards. This
is a directly testable model/interface interaction. It does not dominate all
failures: five of eight acquisition-failure tasks remain unchanged-only.
M0.8D establishes a negative E1 result for **1.5B**, not for 3B. Neither that
history nor the counterfactual is evidence that live 3B E1 will succeed.

**2. Option B: 7B same-scaffold control, conditional and separately authorized.**
Eight accepted 3B edits all fail public assertions, so more semantic capability
is a meaningful later question. But 36/44 changed proposals are blocked before
verification. A 7B E0 run would mix source reproduction, syntax, semantic effects
and different latency/resource feasibility. Do not download or run 7B here.

**3. Option C: stochastic 1.5B, conditional rather than the immediate choice.**
The 1.5B traces show dominant no-op repetition and its seven changed edits all
reach verification. This makes alternatives mechanically plausible, but says
nothing about their distribution under sampling or public correctness. The 3B
data show that extra byte-changing proposals can just repeat mechanical failures.
Temperature-driven diversity alone is not a sufficient recommendation. Keep
deterministic decoding until a separate sampling protocol is approved.

**4. Option D: Planner or stop manual tuning; defer a Planner.**
Failures span multiple stages, but a specific small interface hypothesis is still
testable. Adding Planner intelligence now would conflate interventions and compute.
Stopping is preferable to unregistered open-ended tuning; no Planner is launched.

## Smallest Proposed Follow-Up, Not Implemented

Preregister a paired, development-only 3B E0/E1 ablation on these 16 exposed
tasks, with a fresh acquisition per arm, alternating AB/BA task order. Only the
edit primitive/contract changes. Pin the same 3B digest, Ollama 0.35.1, temperature
0, seed 42, context 4096, output 512 and all original per-window limits. Both arms
keep automatic public verification, historical generic feedback and stop at the
first candidate; no repair, hidden feedback, Planner, memory, generated tools or Pi.

Plan 32 acquisition windows with explicit campaign caps no greater than the
reviewed M0.8D pilot caps. Preregister task-level formation effect, paired gains/
losses, mismatch/syntax/no-op/repetition changes and category costs before inference.
Public correctness is secondary. Do not restrict the cohort to the two mismatch
tasks or replay saved E0 outputs as a live E1 result. E1 changes token burden,
tool description and generated-output distribution; these are treatment effects,
not a pure counterfactual deletion of old. Quantify any new failure migration.

Any progression threshold, statistical treatment and forecast gate require a
separate prospective preregistration. Do not tune for public passes. The objective
is candidate formation sufficient for eventual repair research, not selecting a
new Runner. The exact-output +2 ceiling does not justify predicting qualification.
This proposed experiment is **not implemented or run** by M0.8F.


[Private task-level/operational evidence retained in the research repository.]

## Supported and Unsupported Conclusions

Supported: the large changed-proposal increase is mostly mechanically blocked;
incorrect old is the largest changed-rejection category, eligible for a narrow
3B interface test. Repetition persists even for changed outputs. Accepted edits
remain publicly incorrect. Task-level gains and losses largely offset each other.

Unsupported: counterfactual correctness; guaranteed E1 gain or qualification;
7B benefit or operational feasibility; stochastic decoding benefit; hidden/final
generalization; feedback-driven repair/test-time scaling; Planner benefit; pure
parameter-count causality; replacement of the frozen 1.5B Runner. M0.8B's stop,
M0.8C/D's negative results and M0.8E's below-threshold result remain unchanged.

Stop after this audit. No next experiment is implemented or run.
