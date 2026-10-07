> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8C: M0.8B Acquisition Diagnosis and Next-Experiment Proposal

Diagnostic-only report, 2026-10-06. Evidence: M0.8B commit
`038c370ce410c07b93e07cfba1cc93467dd1fac4`. Protocol 0.5.

**Main result: all 72 acquisition failures repeatedly proposed the identical
unchanged source, not malformed patches, inspection loops, or absent edits.**
All 96 windows inspected the source and transitioned to ACT. Every window
attempted an authorized E0 edit. The loss occurs at state-changing edit formation.

This report uses only M0.8B development/calibration records. No live inference,
benchmark changes, prompt changes, scaffold changes, new experiment, repair,
hidden scoring, or Pi work was performed. The follow-up below is a proposal only.

## 1. Provenance and Preservation

- Starting working tree was clean. Current HEAD is `cb08346`, later than the
  requested evidence commit, and already contains a separate M0.8C pilot. No
  reset, amendment, deletion, or reinterpretation of that history was performed.
  Its outcomes were not used in this report or intervention ranking.
- All 30 M0.8B manifest-listed files match both their recorded SHA-256 hashes
  and their exact Git blobs at `038c370`. Original records were not rewritten.
- Annotated tag `m0.8b-calibration-stop` already exists and resolves to precisely
  `038c370`; no replacement tag was necessary.
- The immutable SQLite backup passes integrity and foreign-key checks. It has
  96 finished development runs, 24 public evaluations, zero hidden evaluations,
  zero `m08_scores`, zero continuation branches, and zero retired cohorts.
- The benchmark archive was hashed as opaque bytes, never opened. No frozen
  evaluation task, hidden test, hidden result, reference solution, or public test
  content was opened or executed for this audit. Public development source
  checkpoints and public model outputs were read through a kind/visibility
  allowlist, checked against their content hashes, and linked to development runs.
- M0.8B's recorded calibration stop remains valid: no qualifying tier, no final
  evaluation, no hidden model scoring, and test-time scaling unmeasured.
- These checks establish the preserved campaign's access history and unchanged
  frozen archive, not proof against unlogged access by unrelated external actors.

The audit rechecks all 1,047 raw model responses against recorded actions,
per-window token receipts against measured call telemetry, contiguous event
sequences, source changes against candidate checkpoints, public-test file hashes
against initial hashes, and all 96 controller transitions.

## 2. Exact Acquisition Funnel

Counts are **tasks with at least one qualifying action**, not proposal counts.
Public PASS/FAIL branch from verification; FAIL is not a stage after PASS.
"Syntactically valid" means strict JSON/tool-argument contract validity, not
proof of a correct program. Authorization includes declared source-path and ACT
permissions. "Applicable" additionally requires a nonempty, non-no-op, bounded,
uniquely matching edit admitted by the Supervisor. Reconstructed proposal-level
authorization on reservation-rejected actions does not mean they were executed.

| Stage | L1 | L2 | L3 | Overall |
| --- | ---: | ---: | ---: | ---: |
| Tasks | 32 | 32 | 32 | 96 |
| Inspection completed, untruncated | 32 | 32 | 32 | 96 |
| EDIT attempted | 32 | 32 | 32 | 96 |
| Syntactically/schema-valid EDIT | 32 | 32 | 32 | 96 |
| Authorized EDIT | 32 | 32 | 32 | 96 |
| Applicable EDIT | 2 | 14 | 8 | 24 |
| State-changing EDIT | 2 | 14 | 8 | 24 |
| Candidate checkpoint created | 2 | 14 | 8 | 24 |
| Public Verification reached | 2 | 14 | 8 | 24 |
| Public PASS | 2 | 0 | 0 | 2 |
| Public FAIL | 0 | 14 | 8 | 22 |

All adjacent conversions through authorization are 100%. Authorization to
applicable edit is L1 **6.25%**, L2 **43.75%**, L3 **25%**, overall **25%**.
All subsequent conversions through verification are 100%. Among verified
candidates, PASS/FAIL conversions are L1 100%/0%, L2 0%/100%, L3 0%/100%,
overall 8.33%/91.67%. Unconditional public PASS is 2/96 = 2.08%.

Inspection, application, checkpointing, and verification are therefore distinct
from model correctness. No accepted state-changing edit was lost downstream.

## 3. Terminal Taxonomy

Each of the 96 windows has exactly one deterministic terminal classification.
Behavior and binding termination limit are separate dimensions. Labels below
are supported by recorded action arguments, errors, checkpoints, and stop reasons.

| Terminal class | L1 | L2 | L3 | Total | Of all 96 | Of 72 acquisition failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `edit_rejected/unchanged_loop/token_budget_exhausted` | 26 | 14 | 20 | 60 | 62.50% | 83.33% |
| `edit_rejected/unchanged_loop/decision_budget_exhausted` | 4 | 4 | 4 | 12 | 12.50% | 16.67% |
| `verified_candidate/public_fail` | 0 | 14 | 8 | 22 | 22.92% | Not acquisition failure |
| `verified_candidate/public_pass` | 2 | 0 | 0 | 2 | 2.08% | Not acquisition failure |

All 72 failed windows contain exactly **one unique canonical edit**, repeated
[Source-bearing example withheld.]
They produced 902 rejected proposals: 890 rejected for unchanged content and 12
by the earlier verification-reservation guard. The 12 guarded proposals are
independently demonstrable no-ops too; preserve their actual recorded rejection
instead of relabeling the guard as an executed no-op check.

Zero windows: no EDIT attempted, read-loop termination, GIVE_UP, malformed or
schema-invalid output, unauthorized edit, patch/context mismatch, invalid edit
syntax, empty old text, edit-size overflow, truncation, infrastructure failure,
manual STOP, or unknown terminal behavior. "No-op" and "not state-changing" are
one measured behavior here, not two additive failure counts. Identical repeated
actions likewise overlap with no-op loops and are not a separate cohort.

## 4. Model-Call Usage Before Acquisition Failure

Values below are median [minimum, maximum]; totals in parentheses where useful.
Wall times are **window wall**, including within-window execution, not campaign
preparation/overhead, and are not added to inference seconds.

| Measure, failed windows | L1, n=30 | L2, n=18 | L3, n=24 | Overall, n=72 |
| --- | --- | --- | --- | --- |
| Model decisions | 13 [12,15] (402) | 13 [13,15] (246) | 13.5 [12,15] (326) | 13 [12,15] (974) |
| EDIT/rejected EDIT | 12 [11,14] (372) | 12 [12,14] (228) | 12.5 [11,14] (302) | 12 [11,14] (902) |
| Input+output tokens | 14,526 [14,218,15,303] | 14,647 [14,166,15,331] | 14,885 [14,283,15,303] | 14,796.5 [14,166,15,331] |
| Token total | 440,176 | 265,478 | 357,766 | 1,063,420 |
| Inference seconds | 23.900 [20.853,27.426] | 23.970 [20.864,26.449] | 24.236 [20.737,27.830] | 24.044 [20.737,27.830] |
| Window wall seconds | 58.609 [25.125,107.984] | 68.610 [25.828,89.078] | 76.461 [26.641,103.953] | 62.524 [25.125,107.984] |

Every failed window: one READ, one unique file, zero repeated reads, one READ
before first EDIT, zero GIVE_UP, zero malformed outputs. Overall failures used
949,228 input + 114,192 output tokens and 1,736.684 inference seconds. They
consumed **94.75% of all M0.8B tokens**. Their window wall sum is 4,498.753s.

`audit.json` supplies n/sum/min/25th/median/75th/max/mean for every measure,
grouped by tier, family, template, terminal class, and formed/failed status.
`windows.csv` supplies the actual measurements and class for **every one of the
96 individual trajectories**. No failed trajectory was omitted.

## 5. Family and Template Patterns

Each family has four tasks per tier. Cells are formations / public passes.

| Family | L1 | L2 | L3 | Acquisition failures across tiers |
| --- | ---: | ---: | ---: | ---: |
| boundary_empty | 0/0 | 0/0 | 0/0 | 12 |
| coupled_conditions | 0/0 | 4/0 | 2/0 | 6 |
| duplicates_order | 0/0 | 0/0 | 0/0 | 12 |
| early_returns | 0/0 | 0/0 | 0/0 | 12 |
| initialization_accumulation | 2/2 | 2/0 | 0/0 | 8 |
| parsing | 0/0 | 4/0 | 4/0 | 4 |
| state_machine | 0/0 | 4/0 | 2/0 | 6 |
| two_functions | 0/0 | 0/0 | 0/0 | 12 |

[Source-bearing example withheld.]
hit token admission. This is descriptive association, not evidence of causal
family-specific resource need. Related instances/tiers are not independent tasks.

Each template has two instances per tier. Counts below are formations / 2.
They provide the full template pattern rather than highlighting favorable cases.

| Template | L1 | L2 | L3 | Failed-window median calls / tokens, all tiers |
| --- | ---: | ---: | ---: | ---: |
| boundary_empty/0 | 0 | 0 | 0 | 13 / 14,426 |
| boundary_empty/2 | 0 | 0 | 0 | 13 / 14,426 |
| coupled_conditions/0 | 0 | 2 | 2 | 14 / 14,503 |
| coupled_conditions/5 | 0 | 2 | 0 | 14 / 14,717 |
| duplicates_order/2 | 0 | 0 | 0 | 13 / 14,283 |
| duplicates_order/3 | 0 | 0 | 0 | 14 / 15,187 |
| early_returns/1 | 0 | 0 | 0 | 15 / 15,088 |
| early_returns/4 | 0 | 0 | 0 | 15 / 15,103 |
| initialization_accumulation/2 | 2 | 2 | 0 | 13 / 14,946 |
| initialization_accumulation/4 | 0 | 0 | 0 | 13 / 14,647 |
| parsing/1 | 0 | 2 | 2 | 13 / 14,777 |
| parsing/4 | 0 | 2 | 2 | 13 / 14,751 |
| state_machine/2 | 0 | 2 | 2 | 12 / 14,437 |
| state_machine/4 | 0 | 2 | 0 | 12 / 14,697 |
| two_functions/2 | 0 | 0 | 0 | 14 / 15,289 |
| two_functions/4 | 0 | 0 | 0 | 13 / 14,309 |

## 6. L2 Deep Analysis

The L2 funnel is 32 -> 32 inspected -> 32 EDIT attempts -> 32 schema-valid
and authorized -> 14 applicable/state-changing -> 14 checkpoints -> 14 verified
-> **0 PASS, 14 FAIL**. Formation 43.75%; acquisition failure 56.25%.
The 14 verified failures span only four families, not the required six.

The 18 nonforming tasks are all four boundary-empty, duplicates-order,
[Source-bearing example withheld.]
[Source-bearing example withheld.]
exhaust token admission. Every task repeats one unique unchanged full-source edit.

Across **all** L2 windows: 288 decisions, 256 edit proposals, 14 accepted and
242 rejected, 299,657 tokens. Rejections: 238 unchanged + four reservations.
Across **only the 18 failures**: 246 decisions, 228 rejected edits, 265,478
tokens; 224 unchanged errors + four reservation errors. The reservation proposals
are unchanged too. No proposed changed patch was blocked for mechanical mismatch.

Ten of the 14 formed candidates appear on the first edit, one on edit 2,
two on edit 5, and one on edit 6. Their 14 pre-acceptance rejections are no-ops,
not public-test feedback. Thus rejected-action recovery sometimes occurs, but
this is **not feedback-driven test-time repair**: each window stops on its
first accepted edit and verification.

Mechanically addressable *exposure*: all 18 failures encounter a generic no-op
error; an informative deterministic projection could reach them. Mechanically
recoverable *demonstrated candidates*: **zero**. The records do not show a good
changed edit that could simply be rescued by correcting serialization or matching.
No L2 change is made or assumed effective.

## 7. Formed Versus Failed Candidates

"Formed" means candidate acquisition, not solved task.

| Observable | 24 formed windows | 72 acquisition failures |
| --- | ---: | ---: |
| Reads / unique files / repeated reads, each task | 1 / 1 / 0 | 1 / 1 / 0 |
| Decisions, median [range] | 2 [2,7] | 13 [12,15] |
| Edit proposals, median [range] | 1 [1,6] | 12 [11,14] |
| Calls total | 73 | 974 |
| Edit proposals / no-op proposals | 49 / 25 | 902 / 902 |
| Tokens, median [range] | 1,246 [1,195,7,721] | 14,796.5 [14,166,15,331] |
| Tokens total | 58,906 | 1,063,420 |
| Inference s, median | 2.686 | 24.044 |
| Window wall s, median | 11.727 | 62.524 |
| Source bytes, median [range] | 182 [136,225] | 165 [131,225] |
| Source lines, median | 8 | 6 |
| Initial INSPECT prompt input tokens, median | 496 | 498 |
| First ACT prompt input tokens, median | 597 | 596 |
| Max prompt bytes, median | 2,587 | 4,465.5 |

All 951 proposals use E0 and echo the complete current source as `old`.
The 24 accepted proposals change bytes **and AST**, with serialized argument
size 324-514 bytes (median 441), comfortably below 8,192. Seventeen formations
occur on first edit; seven follow 1-5 rejected no-ops. No accepted edit has
subsequent acquisition failure. Twenty-two formed candidates fail public tests.

File size and first-request context overlap substantially; formed tasks are not
simply shorter. Later context/cost differences are partly *consequences* of
longer failed loops. Do not treat them as causes or infer hidden model reasoning.
Family/template/tier associations prevent a causal formed-versus-failed analysis.

## 8. E0 Interface Diagnosis

All 96 tasks attempt E0. Twenty-four tasks accept one edit and 72 accept none.
Proposal counts: **951 attempted, 24 accepted (2.52%), 927 rejected (97.48%)**.

| Recorded rejection | Proposals | Fraction of rejected | Resolved evidence |
| --- | ---: | ---: | --- |
[Source-bearing example withheld.]
[Source-bearing example withheld.]

Every rejected proposal has exactly one old-context match. Largest edit arguments
are 514 bytes. No context mismatch, schema/JSON problem, syntactic repair need,
or output-cap hit appears. All 1,047 responses end with backend `done_reason=stop`;
largest single-call output is 164 tokens, below 512.

Edit rejection is quantitatively the dominant interface exit. However, the
Supervisor correctly rejects no-ops; accepting them would create false candidates.
The mechanism is unchanged source generation, not failure to apply changed code.
A whole-file primitive is an eligible later ablation, not an evidenced fix for
[Source-bearing example withheld.]

## 9. Inspection and Budget Diagnosis

Inspection is not the observed bottleneck: every task reads `src/solution.py`
once, untruncated, then immediately enters ACT. All controller-mediated edits
are offered in ACT with only `edit_file`/`finish` available. No later READ or
GIVE_UP occurs. The 12 reservation-rejected edits bypass controller execution
only after prior ACT edits; they are not failed INSPECT transitions.

No field truncation occurs in recorded contexts; max packed prompt is 5,022
bytes versus the 7,000-byte limit. Older observations are dropped as specified by
the recent-four policy. This alone does not establish ideal context construction;
it is not evidence of a broken controller. Source text also appears in repeated
edit arguments. Source preloading would change a working stage and is not justified
as the first intervention.

| Ceiling | Recorded binding failures | Theoretically exposed windows | Evidence of otherwise usable candidate blocked |
| --- | ---: | ---: | ---: |
| Token admission, 16,000 | 60/72 (83.33%) | At most 60 with more token allowance, other caps unchanged | 0 |
| Model decisions, 15 | 12/72 (16.67%) | 12, but tool limit co-binds | 0 |
| Tools, 15 | 0 primary stops; 12 co-binding | Same 12, not another 12 | 0 |
| Verification tool reservation | 12 proposals in those same 12 windows | 12 proposals | 0: all no-ops |
| Wall, 120s | 0 | 0 observed ceiling hits | 0 |
| Edit size, 8,192 bytes | 0 | 0 | 0 |
| Generation ceiling, 512 tokens | 0 | 0 | 0 |
| Context admission / other ceilings / infrastructure | 0 | 0 | 0 |

Token termination is conservative **pre-call admission** of prompt upper bound
plus maximum output, not a claim of consuming exactly 16,000. Failed totals are
14,166-15,331. Decision termination wins precedence over the simultaneously
exhausted tool counter. Increasing decisions alone or tools alone does not remove
the joint restriction; changing both is not a one-factor edit.

All 72 failures could hypothetically be given more resources, but **none contains
an observed state-changing proposal whose acceptance was prevented by a ceiling**.
Unobserved later calls might differ; no justified numerical rescue forecast can
be made. Do not enlarge budgets just because budgets eventually end a loop.

## 10. Capability Versus Scaffold

**Direct correctness/difficulty evidence:** 22 byte/AST-changing candidates fail
public verification; two pass. Hidden correctness is unknown. The fixed
model/scaffold can generate changes on some templates but those changes are
usually wrong on this development set.

**Direct scaffold/interface evidence:** the generic composite error withholds the
specific, mechanically knowable no-op cause, even though each of the 915 such
errors can now be resolved unambiguously. This is an information limitation,
not demonstrated causal suppression of changed edits. No controller, patch
matching, serialization, or verifier defect is observed.

**Ambiguous attribution:** all 72 unchanged loops could reflect action-policy/model
capability, redundant E0 source generation, weak rejection feedback, or their
interaction. The records do not isolate these causes or establish intrinsic
model incapability. There are zero unknown *terminal classifications*, but causal
attribution of the dominant behavior remains unknown.

## 11. Ranked Interventions, Not Implemented

| Rank / intervention | Measured exposure | Scientific confound / complexity | Nature |
| --- | --- | --- | --- |
[Source-bearing example withheld.]
| 2. E0 versus whole-file replacement, historical-equivalent no-op feedback | All 72 failures; all proposals echo entire source | Changes representation, token burden, schema and application semantics; moderate integration/testing | Mechanical contract, unchanged weights; efficacy unknown |
| 3. Deterministic repeated-no-op early stop, log-only metric first | All 72 failures; 830 duplicate edit proposals within them | Saves cost but can prevent delayed candidate formation: seven formed after no-ops; low complexity | Resource/control policy, not formation improvement |
| 4. Additional decisions/tokens, separately budget-controlled | 60 token and 12 jointly decision/tool-bound failures; zero blocked changed proposals | Explicit added-compute treatment, likely more duplication; low code complexity but costly | More inference, not a demonstrated mechanical fix |
| Defer preloading / forced ACT / larger output / patch repair / model change | 0 broken transitions, 0 truncations, 0 mismatches; causal model attribution unresolved | Unnecessary factors, or changes semantic capability; variable complexity | Not justified by this audit |

Exposure percentages do not predict rescue percentages. Never turn no-ops into
accepted candidates, silently repair patches, suggest a likely code fix, or relax
verification to improve this funnel. Stronger model, sampling, Planner, memory,
and generated tools are out of scope.

## 12. Smallest Proposed Development Follow-Up

**One-factor paired diagnostic-feedback pilot**, derived only from M0.8B, not
from subsequent experiment outcomes. This is not authorization to rerun or modify
the separately archived M0.8C pilot; that history remains independent and untouched.
Before any future live work, reconcile this proposal with the later repository
history and register the next experiment under an unambiguous identity.

1. Select exactly one L2 development instance per each of 16 templates using
   lexicographically smallest task ID, without outcome-based selection. Eight
   families; one instance/template. Freeze public-only inputs, manifest/hash,
   configurations, code, analysis/gate, and template-sorted alternating AB/BA
   schedule before inference. These are already calibration-exposed tasks, not
   fresh holdouts. Do not inspect or use the final cohort.
2. A: historical E0 plus unchanged baseline rejection. B: identical E0 and
   orchestration, replacing only the generic error with deterministic
[Source-bearing example withheld.]
   within size limit. Other errors unchanged; raw errors preserved and both raw
   and projected feedback hashed. No source rewrite or proposed semantic fix.
3. Fresh independent windows from identical original public workspace for A/B;
   no cross-window memory or sharing of attempts. Temperature 0, seed 42,
   exact M0.8B digest/quantization/runtime, 4,096 context and 512 output unchanged.
   No model change. E0, source visibility/context policy, C3 inspection, tools,
   verification reservation, public verification, and all stops unchanged.
4. Each window: 15 decisions, 15 tools, 16,000 measured tokens, 120s, one accepted
   edit automatically verified. Stop on first verified candidate, GIVE_UP,
   malformed output, exhausted limit, STOP or infrastructure failure. No feedback
   from a public failure for another edit. At most 32 windows, 480 calls,
   512,000 tokens, 80 execution minutes including overhead. No selective reruns.
5. Primary endpoint: paired verified-candidate formation, B minus A. Report
   B-only/A-only/both/neither; per-family counts; full funnel; rejection behavior;
   decisions/tokens to first changed edit; public FAIL availability; costs per
   formation. Secondary public success, not optimization target. Count repeated
   no-ops and behavior on the next action after rejection. No hidden scoring.
6. Engineering progression gate, preregister **all**: B >=13/16 formations,
   >=4 net extra formations versus A, formations in >=6 families, and >=8
   verified public failures. This approximates the original 26/32 formation
   requirement without declaring the original difficulty qualification satisfied.
   Missing any criterion: do not automatically advance. Passing warrants separate
   development confirmation/recalibration, not final evaluation authorization.
7. Freeze descriptive paired analysis, including an exploratory family-stratified
   template bootstrap 95% interval, 10,000 resamples, seed 8006. No confirmatory
   p-value or post-hoc threshold/tier selection. Sixteen clusters are a small
   engineering pilot, not a formal validation of general capability.
8. Pre-live fake-model tests: identical A behavior; precise message only when
   supported; other error projection unchanged; budgets/termination identical;
   accepted candidate automatically verified once; rejected edit never candidate;
   evaluation/hidden loader inaccessible; per-call and campaign costs conserved.
   Audit requests, projections, order, checksums, DB/export and all conditions after.

If the single-factor feedback treatment is ineffective, its result would favor
testing representation separately before any budget expansion. Do not combine
feedback and primitive changes in one arm. Success would show a development
acquisition effect under the fixed model, **not semantic repair/test-time scaling**.
No improvement would not establish equivalence or isolate intrinsic capability.

## 13. Evaluation Cohort Eligibility

The intended 96-task evaluation cohort remains unexecuted in the audited campaign
and sealed for this work; there are 96 evaluation fixtures per frozen candidate
tier, with no tier selected. Do not silently choose an evaluation tier now.

Development-only scaffold/acquisition changes can leave the unchanged, untouched
cohort eligible for a **new preregistered experiment**. Finalize scaffold, budgets,
feedback, tier selection, success criteria, compute caps and analysis from
development before unsealing. No outcome-dependent final changes or iterative
[Source-bearing example withheld.]
scaffold, not completion or reinterpretation of stopped M0.8B. Retire after use.

Related templates limit claims of out-of-family generalization even with clean
instance splits. Development reuse can overfit template behavior; disclose all
exposures, keep all families, and use an independent development confirmation
where feasible. A public-test formation effect need not generalize to hidden tests.

If generator, bug definitions, requirements, reference behavior, test content, or
difficulty semantics change, freeze a new version and regenerate/disjointly certify
a new evaluation cohort *before* comparative outcomes. Do not modify the sealed
cohort in place or choose exceptions after seeing it. This audit found no reason
to change benchmark content; candidate formation is the first unresolved issue.

## 14. Supported and Unsupported Conclusions

Supported: M0.8B correctly stopped. The dominant failure is repeated unchanged
E0 generation after successful inspection. Patch matching and output ceilings
are not observed bottlenecks. Accepted changes reliably reach verification.
L2 supplies 14 verified failures, but formation and family breadth are inadequate.
The small fixed model/scaffold sometimes moves from rejected no-op to a changed
candidate without public feedback; its causal mechanism is unmeasured.

Not supported: that any proposed intervention works; that E0 intrinsically
suppresses coding; that more budgets rescue tasks; that no model capability
remains; that retries, detailed executable feedback, fresh restarts, memory,
Planner or test-time scaling improve or fail; that public outcomes imply hidden
outcomes; or that the final evaluation tier is qualified. All M0.8B H-I/H-F
questions remain unmeasured, not negative or equivalent.


[Private task-level/operational evidence retained in the research repository.]
