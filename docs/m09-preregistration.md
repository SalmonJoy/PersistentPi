# M0.9A: Planner-driven scaffold optimization preregistration

Canonical machine configuration: `configs/m09-preregistered.json`. Protocol 0.6
defines the planned infrastructure without changing historical protocols. This
revision authorizes planning changes only: do not implement M0.9B, run Runner or
Planner inference, access final tasks, or perform benchmark hidden scoring.
Implementation and campaign execution each require separate authorization.
The later user-provided `goal-objective.md` explicitly authorizes M0.9B offline
implementation/validation. It does not authorize live inference, final-task access
or benchmark hidden scoring. The planning-only correction above remains historical.

The research question is whether a strong external Planner discovers a general
scaffold that improves the frozen Qwen2.5-Coder 1.5B Runner. Temperature 0, seed
42, context 4096, Q4_K_M, digest d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668
and Ollama 0.35.1 remain frozen. Exact model metadata is copied from M0.8D.
M0.8I used 3B: its failure motivates ending manual serialization engineering,
but is not a direct measurement of 1.5B. No E3, teacher, memory, tool generation,
code mutation or Pi work is included. A 15-point gain is materially important.

B0 is M0.8D-A: C3, E0, schema JSON, generic feedback, output 512, automatic
verification. B1 is M0.8D-B: the corresponding E1 reference. Their exact historical
model-visible prompts/configurations are preserved; protocol 0.6 metadata remains
outside model messages. Both are evaluated freshly; historical scores are not reused.

Search32 consists of exposed L2 development public inputs from M0.8C and M0.8D,
16 templates and eight families. Screen8 selects one task/family by minimum
SHA256 of canonical [9001, task_id]. Remaining24 is its exact complement.
Qualification48 uses the three unused parameters from {2,3,4,5,6} per exposed
development template, the same first two L2 mutations and eight public cases
with seed 9002. Construction proves reference pass, mutant failure, component
witnesses and unique instances. There is no model-based difficulty adjustment.
Failure of construction stops preparation. Qualification measures instance-level
transfer. Freeze all qualification contents before future Planner inference.

The 96 L2 final tasks remain inaccessible. Qualification execution becomes
available only after search closes, the proposal budget closes, a unique finalist
and successful entry decision are durably frozen. One finalist is tested once;
no runner-up can replace it. No qualification content or result reaches Planner.
Both qualification and final cohorts retire after use. A future final study
requires separate authorization and unchanged benchmark content.

ScaffoldSpec v1 is data only: authored system/tool-description text (4096 bytes
combined), approved context inclusion/order, preload, C0-C3, READ 0-2 (zero
requires preload), recent observations 0-4, generic/precise rejection feedback,
stop/retry mechanical failures, stagnation off/2/3, existing E0/E1 interfaces and
per-phase decision/output allocations. E2 remains unmodified and excluded from
this catalog until isolated compiler integration is separately validated. No new
codec, fence stripping, source repair, arbitrary expression, path or executable
field is allowed. Catalog/compiler/renderer versions and hashes enter identity;
parent/proposal metadata does not. Unknown fields and detectable task lookup
tables are rejected; semantic prompt generality is not statically provable.

Each clean task ends at its first accepted state-changing candidate followed by
Supervisor-triggered public verification, or GIVE_UP/budget/STOP. No repair follows
public failure. Limits are 15 decisions/tools, 16000 tokens, 120 seconds, five-second
verification, 8192 edit bytes and existing output/workspace limits. Source preload
is a charged READ. Output allocation 128/256/512/1024 is a reported scaffold factor;
it does not increase context 4096 or the global task ceiling. Verification reserves
capacity before edits. Rejected actions consume budgets.
The retry field governs malformed-response stop/retry; rejected tool actions remain
bounded by decisions/tools/stagnation, preserving B0/B1's historical behavior.

The trusted control plane alone owns task specifications, expected answers,
partitions, verification, hidden evaluation, permissions, logger, provenance,
SQLite, resource accounting, stops, promotion and final selection. Models receive
only restricted data contracts, never database handles, arbitrary processes or
filesystem authority. The public verifier runs bounded Python with fixed public
cases. All M0.9 databases block hidden evaluation. Source-free observations use a
positive allowlist and fixed categories; labels alone are not access controls.

Planner.propose receives a projected observation, archive view and remaining
budget, returning one strict JSON ProposalEnvelope with parents, complete spec,
mutation description/rationale, targeted categories and optional metric predictions.
Whitespace around JSON is accepted; fences, duplicate keys, nonfinite numbers,
unknown/executable fields and extra payloads are rejected. Rejection consumes a
slot. No free format repair, task selection or human proposal edits are permitted.

Planner sees aggregate/per-family public metrics, normalized failures, action
types, controller transitions, repetitions, lengths/hashes, equality flags and
costs. No task/source/reference/specification/public-case/expected-value text, raw
malformed outputs, source-bearing arguments or traceback text is disclosed.
Replace source fields with deterministic placeholders and safe numeric metadata.
At most two typed excerpts, selected by failure frequency then stable task hash,
are 2048 bytes each. Requests are at most 16 KiB. Drop excerpts/older archive detail
before mandatory instructions/parent spec/aggregates. Log the exact projection,
request and policy version. Adversarial nested canaries must never be disclosed.

Use four rounds/two proposals each. Each valid unique proposal screens on Screen8;
proposal two may observe proposal one's projected search results. The better screen
candidate runs only Remaining24. Invalid/duplicate proposals consume slots but no
Runner windows. A round with no eligible candidate skips full evaluation.
The full-search score invariant is:

`FullSearchScore(scaffold) = Screen8(scaffold) + Remaining24(scaffold)`

Here `+` means the identity-checked union of existing task-level outcomes, followed
by recomputation over exactly Search32; it does not mean adding rates, distinct
family counts or lexicographic score tuples. Screen8 and Remaining24 are disjoint
and their union must equal the frozen 32-task manifest. The eight screening results
are reused without rerunning them, including for the eventual winner. Each physical
execution has one receipt and is charged once. Logical full-cohort analysis uses
those same eight receipts together with the 24 new receipts, never additional
inference. Incomplete scaffolds remain screen/proposal entries only: they cannot
become the persistent best fully evaluated entry or enter full-search comparisons.
Cohort hash, scaffold identity, task identity and receipt uniqueness must be
machine-checked before ranking; no archive comparison across different task sets.

Lexicographic objective: public passes, passing families, formations, formation
families, lower complexity, Runner tokens, calls, inference seconds, wall seconds,
ascending scaffold hash. Complexity is authored bytes, enabled states/actions and
non-default fields. Hard bounds provide primary regularization. Objective and gates
never use hidden outcomes. After four rounds, the best complete generated entry
qualifies only with >=4 extra public passes over each reference and >=4 families.

Qualification evaluates selected/B0/B1 on all 48 tasks, with all six arm permutations
balanced using seed 9003. Promotion requires >=36 formations, >=24 passes, >=6
passing families, >=8 extra passes versus each reference, AND LCB95(selected-B0)>0
AND LCB95(selected-B1)>0. Both bounds use 10000 paired whole-template resamples
within fixed families, seed 9004, percentile 95% intervals. All three instances of
a sampled template stay together. This symmetric gate is an engineering progression
rule, not a confirmatory claim. No p-values. Missing infrastructure results prevent
completion; ordinary acquisition failures count as unsuccessful tasks.

Execution maximum: 64 reference windows +64 screens +96 remaining windows +144
qualification windows =368. Runner ceilings are 5520 calls/6M input+output tokens.
Planner ceilings are eight requests/200000 input+output+reasoning tokens; do not
double-count reasoning already included in output. Shared active campaign wall is
12 hours, measured once including overhead, not the sum of nested timers. Forecast
must be <9 hours and <4.5M Runner tokens. Reserve 144 qualification windows/2.304M
tokens and next Planner request before spending. Idle pauses have separate receipts.
The admission forecast uses 2000 exposed-development-window bootstrap resamples,
seed 9005, P90 projected costs across 368 windows plus eight 180-second Planner
deadlines. Forecasts are not guarantees; immutable live ceilings remain binding.

Cloud Planner target is Ollama Cloud glm-5.3, not frozen backend identity yet.
M0.9C is one fully recorded bounded optimization campaign, not a claim of
bit-for-bit cloud reproducibility. Before admission, freeze the exact requested
identifier, available returned model/backend identity, API/runtime and supported
configuration mapping. If the frozen model requirement cannot be satisfied because
identity has changed or cannot be verified to the declared available precision,
execution is blocked. Missing provider identity fields must be explicitly recorded;
they are not permission to ignore an observable identity change.

Mandatory provenance for every request is the requested model identifier; returned
identity where available; complete semantic request and response; system prompt;
complete configuration including temperature/sampling and supported reasoning
effort; token/usage accounting; timestamps; request/response hashes; latency; and
proposal validation result. Authentication secrets/headers are never recorded.
Deterministic controls are separate: request seed 42 if supported, otherwise record
unsupported seed explicitly. Lack of seed support alone does not invalidate the
campaign. Request temperature 0/high reasoning where supported, output allowance
4096 and deadline 180 seconds. Verify mapping/identity at M0.9C admission; cloud
structured outputs are not assumed. During the campaign, observable identity drift,
changed configuration semantics, loss of mandatory accounting, or violation of the
frozen response/usage contract triggers an integrity stop. Ordinary variation in
generated proposals is not, by itself, evidence of backend drift. No automatic
provider/model switch, silent restart, or outcome-dependent drift criterion.

Free-only access is intentional operational feasibility: zero purchased credits,
subscriptions, top-ups or paid fallback. Verify included allowance before inference;
no quota exhaustion probes or adaptive expansion. Credential values are excluded
from provenance. Token accounting is mandatory; unresolved usage stops execution.
This is an intentional operational feasibility constraint, not a scientific
hypothesis about free versus paid Planners. Paid access would require a separately
approved preregistration with a fixed monetary ceiling before any search; it cannot
be enabled adaptively after observing results. Future M0.9B adapter validation, if
authorized, must use offline fixtures without cloud calls.

Durably record request reservations before sending, jobs before starting and all
completed results once. Resume only never-started jobs with unchanged identities
and remaining cumulative budgets. Sent unresolved requests and started interrupted
windows are indeterminate and stop; no silent resend or selective rerun. Finalist
freeze is immutable. Archive/projection/proposal/cost decisions replay from artifacts
and SQLite snapshots without inference. Historical evidence is preserved bytewise.

Later, separately authorize selected/B0/B1 on untouched 96 L2 tasks (288 windows).
Seal generation before hidden scoring; primary endpoint is public AND hidden pass.
Acquisition failures score zero. Two paired template-cluster contrasts use 100000
label swaps, 10000 family-stratified bootstrap samples and Holm adjustment. Retire
the cohort. No final content is used by this implementation.

Report both optimization expenditure and deployment cost, family outcomes/funnels,
formation/conditional correctness, repetition/failures, input/output tokens, calls
and timings. Do not equate local/cloud tokens as currency. Defer Relative Improvement
Captured until a defensible denominator exists. Search-only improvement suggests
overfitting/instability; no benefit does not prove impossibility or equivalence. One
bounded cloud campaign does not establish optimizer reliability or superiority
over equally budgeted human/random search. Future optimizer/model controls are
separate studies. If separately authorized, M0.9B should end with offline tests,
fake campaigns and a checksummed freeze, not a live campaign.

## Required future invariants and tests

These are implementation requirements, not claims of tests completed in M0.9A.

- Scoring: prove Screen8/Remaining24 are disjoint and exactly cover Search32;
  preserve the original screen receipt IDs; reject duplicates, missing results,
  changed task/scaffold/cohort hashes and comparisons of unequal task sets.
  Reconstruct nonlinear full-cohort metrics from the 32 outcomes. Assert the screen
  tasks are physically executed once and charged once, including for the winner.
  An eight-task or otherwise incomplete candidate cannot become persistent best.
- Disclosure: use a positive typed allowlist, not regex removal from raw traces.
  Source-bearing action fields become fixed placeholders plus length/hash,
  equality/difference, normalized action, repetition and rejection metadata.
  Never disclose task source, reference solutions, task-specific expected outputs,
  public-test bodies, full benchmark specifications, long source-bearing model
  outputs, hidden information or qualification/final assets. Enforce this across
  nested fields, errors, filenames, free-text labels and request truncation.
- Canary tests: insert distinct synthetic source/reference/expected-output/test-body/
  hidden/specification markers into adversarial traces, malformed outputs and nested
  metadata. Assert none occurs in the final serialized Planner request. Verify safe
[Source-bearing example withheld.]
  Qualification and final-access attempts must fail before projection.
- Disclosure receipts: log the exact post-truncation observation sent on every
  request, its policy version/hash and complete request. Replaying that projection
  must reproduce the bytes logged; logging a richer pre-truncation object is not
  sufficient. No unprojected task-specific trace reaches Planner.
- Provenance/drift: require all mandatory fields, recording unsupported seed and
  unavailable identity fields explicitly. Fixture-test unsupported seed admission,
  pre-start identity mismatch rejection, mid-campaign integrity stop, unavailable
  usage rejection and the absence of automatic fallback/top-ups.
- Qualification isolation: deny content/results to Planner in every phase;
  execution is allowed only after immutable finalist/entry/closed-search receipts.
  A qualification failure cannot reopen search or admit a second finalist.
- Resource accounting: one screen execution contributes once to Runner ledgers;
  Planner tokens include separately reported reasoning only when not already
  included in output. Charge overhead/shared active wall once. Reject exhausted
  budgets without adaptive ceiling expansion.

## Final consistency audit

| Decision or boundary | Fixed rule |
| --- | --- |
| Screen winner | Compare only identical Screen8 results; same lexicographic objective and fixed tie-breakers. Invalid/duplicate proposals consume slots, not executions. |
| Persistent best / round parent / finalist | Only complete identical Search32 results. Reuse Screen8 plus Remaining24; no winner-only rerun or subset comparison. |
| Physical versus logical use | Eight existing receipts plus 24 new receipts produce one logical 32-task score. Physical expenditure counts each receipt once; logical reuse is labelled, not added to expenditure. |
| Planner visibility | Typed public search aggregates and protocol-only projected excerpts; normalized parent ScaffoldSpec and approved budget/archive fields. No task-bearing trace, qualification/final content or result, or hidden information. |
| Qualification access | Trusted cohort preparation may construct/freeze new public qualification instances offline; search workers and Planner cannot access them. Qualification workers receive them only after closed search, entry gate and one immutable finalist. |
| Qualification ranking | One frozen finalist versus B0 and B1 on identical Qualification48; symmetric predefined gates. No feedback to Planner, runner-up substitution or adaptive retuning. |
| Final cohort | Remains untouched; later authorization required. No final task/test content is read during this revision or search/qualification. |
| Cloud identity | Available identity/configuration precision frozen before campaign. Unsatisfied freeze blocks start; observable identity/contract drift during execution stops integrity. Unsupported seed is recorded, not a stop by itself. |
| Runner-only ceilings | 368 physical windows, 5520 Runner calls and 6M Runner input/output tokens; the <4.5M forecast and qualification reserve concern Runner consumption only. |
| Planner-only ceilings | Eight requests and 200k input/output/reasoning tokens without double-counting; per-request byte/output/time caps remain separate. |
| Shared ceiling / access cost | Twelve active hours include both models, verification and overhead once; <9h campaign forecast. Zero purchased credits/top-ups/paid fallback is a fixed operational constraint. |
| Analysis choices | Cohorts, selection, objective, ties, promotion, bootstrap, stopping and disclosure are specified before inference. No analysis choice depends on final evaluation outcomes. |

## Revision changelog

- Made full-search receipt reuse, equal-cohort ranking and complete-archive eligibility
  explicit, with future validation tests: prevent subset comparisons and double
  execution/accounting.
- Strengthened protocol-only disclosures, exact sent-observation logging and canary
  tests: optimize interfaces/control without teaching task-specific solutions.
- Separated mandatory cloud provenance from optional seed control; specified model
  admission/drift stops and one bounded recorded campaign without deterministic
  replay claims.
- Preserved zero purchased credits explicitly as feasibility rather than a research
  hypothesis; ruled out adaptive paid fallback and resource expansion.
- Added the task-set/access/accounting consistency audit and clarified that this
  revision authorizes planning only, not M0.9B.
- Unchanged: frozen 1.5B Runner, B0/B1, Search32/Screen8/Qualification48/final96,
  instance-level qualification interpretation, protocol 0.6, configuration-only
  ScaffoldSpec v1, trusted boundary, proposal contract, four rounds/two proposals,
  public-only lexicographic objective, hard complexity/resource limits, one-shot
  qualification with no Planner feedback, and separately authorized final study.
  No memory, tool generation, arbitrary code mutation or Pi dependency was added.
