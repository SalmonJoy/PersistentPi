# M0.8: Feedback-Driven Test-Time Scaling

Approved research design, protocol **0.5**. M0.8A implements, validates and freezes
the machinery; M0.8B performs live development calibration and, only after its
gates pass, the final evaluation. M0.8A executes neither live calibration nor the
final 96-task evaluation. The canonical configuration is
`configs/m08-preregistered.json`; the freeze binds this document and that object.

This final methodological review changes documentation only. It does not approve
or perform implementation or live execution. Existing implementation files and
historical preparation records are not changed or re-certified by this review.
Any later freeze must bind the revised document; an older document hash is not
evidence that this revision has been frozen.

## Questions and hypotheses

The Runner model remains frozen. For arm X and horizon k, V_X(k) is the fraction
of all 96 tasks whose publicly selected checkpoint passes both public and hidden
tests. Public-only success and raw hidden success are reported separately.

| Question | Contrast | Interpretation |
| --- | --- | --- |
| Q1 - Test-time interaction: Does allowing additional verified candidate cycles improve validated task success? | H-I: D@1 -> D@5 | Primary nested-trajectory interaction effect |
| Q2 - Detailed executable feedback: Does detailed public failure evidence improve results beyond knowing only that verification failed? | H-F: D@5 vs O@5 | Primary paired feedback projection comparison |
| Q3 - Sequential repair vs fresh retry: How does detailed continuation compare with repeatedly starting from the clean task under the same candidate horizon? | D@5 vs R@5 | Secondary policy comparison |

D/R changes workspace state, history and feedback availability. It is not a pure
feedback effect. No claim concerns weight learning, a scaling law, arbitrary
repositories, or a comparison between models.

H-I's primary effect is `Delta_I = V_D(5) - V_D(1)`, with preregistered materiality
`Delta_I >= 0.10` (10 percentage points). It has **no p-value**: horizon one is a
prefix of the exact same detailed-continuation trajectory as horizon five.
Stop-on-public-success preserves an initial validated success at all later
horizons, so the contrast is monotone, not symmetric/exchangeable. A paired
label/sign permutation test is not the primary inferential treatment for H-I.

Report a family-stratified whole-template cluster-bootstrap 95% CI, raw number of
validated recovered tasks, recovery rate among tasks whose first candidate fails
public verification, attempt number of first recovery, and marginal candidate,
token, inference-second and wall-second cost per recovered validated task. With
the fixed 96-task denominator, `Delta_I = validated_recovered_tasks / 96`;
formation failures remain in that denominator but not the initial verified-failure
denominator. Public-only recovery counts/rates are reported separately. No new
model executions at k=1 or k=3 are introduced to manufacture paired treatments.

A meaningful positive label requires an estimate of at least 10 points and a CI
lower bound of at least 10 points. An observed positive estimate below 10 points
is small positive; uncertainty may still permit a material effect. When the CI
crosses the material threshold, materiality remains inconclusive. Zero/negligible
recovery supports a negative interpretation only when actual continuation
candidate formation supplies repair opportunities; report formation counts
instead of treating inability to edit as evidence against repair. Report initial
verified failures, tasks producing a later verified candidate, and unique later
candidates alongside that interpretation; do not silently drop formation failures
or choose a post-hoc adequacy cutoff. Small-positive magnitude and inconclusive
materiality may both be reported when the CI permits a >=10-point effect. Neither
absence of statistical significance nor a degenerate zero-recovery CI establishes
equivalence. No conventional p-value is required for H-I.

H-F's paired effect is `Delta_F = V_D(5) - V_O(5)`. D and O branch from the exact
same initial verified failure and differ primarily in public-feedback projection,
not initial candidate acquisition. H-F uses its effect, cluster-bootstrap 95% CI
and two-sided template-level
D/O label-swap test: 100,000 Monte Carlo permutations, seed 8006, joint swaps of
all three instances in a template, p=(extreme+1)/(100000+1). The exchangeability
assumption is explicit; balanced execution order is not treatment randomization.
This is the sole confirmatory p-value at alpha .05; no Holm correction is needed.
Report that p-value unadjusted because it is the only confirmatory test. No extra
confirmatory tests or outcome-selected sensitivity analyses are added. Additional
confirmatory tests would require an explicit hypothesis family and multiplicity
adjustment preregistered before evaluation; they cannot be added after outcomes
are inspected. H-I is not included in a p-value correction family.

Bootstrap: 10,000 percentile replicates, seed 8006, 2.5th/97.5th percentiles.
Resample whole templates independently within each of eight fixed families.
Retain all three instances and their paired arms/horizons together. Results are
conditional on these families. Ninety-six variants are not 96 independent tasks.
Q3, intermediate horizons, family results and cost comparisons are descriptive.

## Model, scaffold and context

Preserve M0.7 baseline eeaba4c, annotated tag m0.7, and historical research records.
Use qwen2.5-coder:1.5b, Q4_K_M, model digest
`d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668`,
Ollama 0.35.1, temperature 0, seed 42, context 4096, output ceiling 512,
explicit think=false, existing JSON-schema E0 action interface. Verify identity
before generation; mismatch blocks execution. No prompt jitter or exploration
sampling is introduced if greedy restarts repeat exactly.

INSPECT -> ACT -> accepted state-changing EDIT -> checkpoint -> automatic PUBLIC
VERIFICATION. Only verified FAIL permits a new acquisition window. The model
chooses semantic edits; mechanical verification is never a model decision.
Successful reads retain the C3 two-read ceiling/source-completion transition.
D/O do not reopen INSPECT after edits. Four recent observations, a 7000-byte
prompt bound and 1800-byte field allowance remain fixed.

D continues the failed workspace and bounded history with detailed evidence.
O continues the same state with only FAIL. R restores the exact original
checkpoint, clears visible history and restarts normal INSPECT, paying its cost.
Outcome-only projection exposes no names, counts, exception classes, assertion
text, expected/actual values, timings, truncation or debug metadata.

All eight public cases execute in fixed order. D includes overall FAIL and the
first two failures: public ID, assertion/exception type, first 384 UTF-8 message
bytes and up to 192 bytes of relevant traceback evidence. Expected/actual appear
only through public assertion output. Remove host paths and interpreter frames.
Cap the entire field at 1800 bytes with an explicit marker when truncated. Bound
its transported JSON representation as well. Use identical 1800-byte transport
reservation for D/O eviction, including JSON escaping. No LLM summary or diagnosis.

Runner-visible budgets show current-window allowances only. Future horizon and
global remaining candidate count are absent. Horizons 1..5 are saved analytical
prefixes of one policy trajectory, not differently advertised budget agents.

## Task generation and development calibration

Eight families: coupled conditions; boundary/empty handling; initialization and
accumulation; early returns; bounded state machines; multi-edge parsing;
two-function interaction; list transformations with duplicates/order.
Each has six specified templates. Partition two development/four evaluation
templates per family before inference. Two development instances/template give
32 tasks; three evaluation instances/template give 96 tasks and 32 clusters.

Generate all three tiers before calibration: L1 one compound mutation component,
L2 that component plus a second interacting component, L3 three bounded
components. A compound component may change two related conditions or behaviors
within one fixed recipe; component counts are not counts of changed characters.
Templates contain bounded pure Python functions, explicit requirements, no
libraries/network, and no changes to the existing interpreter permission policy.
Parameter domains and recipes are versioned. Runner IDs are opaque hashes and
reveal no family, mutation, tier or hidden data.

Seeds: parameters 8001, template partition 8002, public cases 8003, hidden cases
8004, execution schedule 8005, analysis/forecast 8006. Every fixture contains eight
public and 32 disjoint hidden inputs, reference/mutant programs, family/template/
instance identifiers and provenance hashes. Mechanically select public component
witnesses from the declared input pool, never model outcomes.

Before inference certify every fixture: reference passes both suites; mutant
fails both; every component has a public witness; no equivalent mutation,
duplicate identity/template collision or reference inconsistency; full reference
repair fits one exact E0 edit, 8192 bytes and 512 output tokens. Count using the
installed, checksum-verified frozen GGUF Qwen2 byte-BPE tokenizer. This authored
ASCII corpus rejects unsupported non-ASCII certification rather than guessing.

Acquire one window for every development task across all three tiers: 96 initial
acquisitions. A tier qualifies with 10..22 public successes, >=26 verified
candidates, >=8 failures, and failures in >=6 families. Choose smallest distance
to 16 successes, then more failures, then lower tier. No qualifying tier stops
preparation. Never inspect final evaluation model performance to choose a tier.
Run D/O/R continuation calibration on the selected 32 development tasks only.
No positive-recovery criterion is used. Hidden candidate scores are never read
during development selection.

Before any model inference, save one development audit task/family for each of
the three potential tiers, together with all initial/continuation schedules. Use
the preselected map for the chosen tier, then perform two additional clean initial
acquisitions each: 16 reproducibility audit windows. Record changes
in normalized behavior and timing; do not use audit results to tune final prompts.
Final evaluation is 96 shared initial acquisitions and D/O/R continuations, up
to five candidates per logical policy, yielding 288 logical policy trajectories.
No candidate evaluation is performed on these final tasks during M0.8A.

## Acquisition windows, lineage and accounting

Candidate attempt = accepted state-changing edit, checkpoint and automatic public
verification. Reads, rejected/no-op edits and malformed actions are not candidates
but consume applicable budgets. A window ends at one verified candidate, GIVE_UP,
malformed termination, exhaustion, STOP or interruption. Acquisition failure ends
that trajectory without a fresh free window. Public PASS stops immediately.

Per window: 15 decisions, 15 tool calls, 16000 combined tokens, 120 seconds,
5-second verification timeout, 8192-byte edit, 4096-byte raw verifier output,
10-MiB workspace. Reserve a verification tool call and five seconds before editing.
Conservatively admit model requests using frozen prompt token bounds plus the
512-token output allowance. Unknown usage or admission-bound violation interrupts.
Five windows imply <=75 decisions, <=75 tools, <=80000 tokens, <=600 seconds per
logical trajectory. STOP and infrastructure failures prevent further generation.

InitialPrefix is an immutable, content-addressed first-class lineage object. It
binds task hash, experiment/manifest, scaffold/protocol, original/candidate
checkpoints, transcript and public-result artifacts, acquisition run, physical
receipts, timestamp and provenance. Transcript includes model-request/output
references as well as observations. D/O/R reference this exact parent. Code
equality alone cannot establish lineage. Validate all identities at branching
and each subsequent window. SQL and manager checks protect referential integrity.

Execute the first acquisition physically once. Public PASS carries the shared
checkpoint to all logical policies; verified FAIL opens branches; formation
failure terminates all policies. Logical policy costs each include the shared
prefix; physical expenditure includes its unique receipts once. Reconcile
sum(logical generation costs) = physical generation costs + twice prefix costs.
Record private-measurement overhead separately as physical study expenditure.

Shared-prefix lineage is a hard invariant, not merely a reporting convention.
For every initial verified failure, D/O/R must all name the one stored
InitialPrefix as parent, including its exact acquisition-run and candidate
checkpoint identity. R still names that failed prefix as its causal parent even
though its next workspace is restored from the prefix's original checkpoint.
No arm may reacquire candidate 1, substitute a code-equivalent acquisition, or
silently create an arm-specific first candidate.

Required validation tests, before any live campaign:

- Count physical acquisition calls: all three arms share exactly one initial
  model/tool execution sequence and one stored prefix for each task.
- Assert D/O/R have identical parent prefix, acquisition-run, candidate-checkpoint
  and initial-public-result identities, including after persistence/reload.
- Reject a substituted parent from another task/campaign, a different initial
  candidate, and a separate acquisition with identical code bytes. Reject
  missing parents, duplicate initial acquisition, and lineage mutation.
- Assert D/O restore the shared failed checkpoint; R restores the stored original
  checkpoint without replacing or repeating the shared acquisition.
- Reconcile inference/tool receipts: each policy can charge the prefix logically,
  while physical study expenditure counts its receipts exactly once. Count
  actual overhead separately, never as duplicated prefix expenditure.

Save candidate index, checkpoint, outcome, cumulative costs, transcript/workspace
identity, branch, feedback mode and termination. Early success/termination carries
forward to later horizons. At horizon k select first public pass, otherwise latest
verified checkpoint, otherwise original. Never choose a best hidden candidate.

## Hidden scoring, metrics and resource gates

Generation must be sealed before any hidden scoring. Calibration never scores
model candidates privately. Hidden outcomes cannot affect continuation, checkpoint
choice, prompts, tier selection, exclusions or reruns. An evaluation cohort is
retired once launched, including interrupted campaigns. No cross-task memory,
Planner, generated tools, teacher, Pi access or adaptive scaffold optimization.

Report success@1..5, public/hidden/validated outcomes, first recovery, candidate
formation, candidate and decision counts, calls, input/output tokens, inference,
verification and wall time, accepted/rejected edits, repetition and unique byte/
AST candidates. Public recovery rate = initially verified-failing tasks later
publicly passing / initial verified failures; validated recovery also requires
hidden success of that publicly selected checkpoint. Zero denominator is null.
Formation failures remain in whole-cohort success denominators.

First validated recovery is the earliest k>=2 whose first publicly passing
selected checkpoint also passes hidden measurement after sealing. Public PASS
with hidden FAIL stops execution but is not validated recovery; hidden outcomes
must not reopen the trajectory. Recovery rates use all initial verified failures,
including those that never form a later candidate. Marginal costs use whole-cohort
cost differences, including unsuccessful continuation costs, divided by additional
validated recoveries, not costs only on the recovered subset.

Stagnation is observed without intervention: repeated canonical edits; rejected
action/category/checkpoint tuples; longest repeated-action streak; normalized
failure signatures; unique byte/AST candidates; distinct valid actions/valid
actions. Strip host paths and do not include timestamps/durations in signatures.
GIVE_UP is terminal, so repeated GIVE_UP is meaningful only across executions.

For 1->3, 3->5 and 1->5 use the entire paired cohort: additional validated
recoveries, candidate verifications, tokens, inference/wall cost per recovery,
and recoveries per 100000 additional tokens. No recovery gives null cost ratios
while retaining cost numerators. Categorize inference by observed control phase
and chosen action, without claiming to observe internal reasoning.

Use 10000 development template-resampled physical cost forecasts, seed 8006,
90th percentile. Include measured difficulty/continuation calibration and audit
already spent, projected 96-task evaluation generation and separately bounded
private measurement overhead. Each development physical bundle includes its
recorded window-preparation overhead. Common generation control-plane overhead
is apportioned by executed window count, not success or logical-policy costs.
These overheads are forecast inputs, not additional logical Runner cost.
Forecast must be strictly below 9 execution hours
and 9 million measured tokens. Hard campaign ceilings: 12 accumulated execution
hours and 12 million measured tokens. Human development/pauses are excluded.
Failure stops launch; do not shrink the cohort or change conditions.

Freeze seeded task order and balance six D/O/R permutations before execution.
One inference request at a time; no unrecorded warm-up. Persist schedule, receipts,
checkpoints and stops. Interruptions remain incomplete; no selective arm reruns.

## Integrity, artifacts and acceptance

Freeze human/canonical preregistration, model identity/config, protocol, scaffold,
prompts, generators/domains/partition, feedback, tier selection, analysis,
statistics, scheduling, seeds, budgets, costs and termination/exclusion rules.
The manager refuses mismatched preregistration or freeze identities before
generation and scoring. A changed frozen asset requires a new version/freezing
procedure, not a mid-campaign correction. No analysis choice depends on final
evaluation outcomes; edge-case rules and development gates are predetermined.

Retain checksummed fixture/certification manifests, calibration choice/forecast,
audit results, execution/model/hardware identities, exact model requests/outputs,
actions, public raw/projected evidence, lineage, physical/logical receipts, SQLite,
prefix CSV/JSON, analysis JSON, and a checksummed research export.

M0.8A requires all historical tests plus lineage, masking, restart, horizon
blindness, budget, hidden isolation, fixture, calibration, schedule, forecast and
statistical edge-case tests. A deterministic development-fixture dry run must
exercise shared acquisition, D/O/R, >=2 candidate windows, recovery, sealing,
hidden scoring, analysis, cost reconciliation and export integrity. Scientific
success is not an infrastructure acceptance requirement. Live calibration and
the final campaign remain pending at M0.8A completion.

Final methodological changes: H-I permutation inference removed because nested
prefixes are not exchangeable; H-F remains the sole paired p-value; unnecessary
Holm removed; Q1/Q2/Q3 and D/R confounding explicit; shared-prefix lineage and
physical accounting enforced. All approved major design choices remain fixed.

Preparation revision 2 corrects audit-choice persistence so all three possible
audit selections are saved before inference. It adds semantic repeat-comparison
receipts without using them for tuning or selection and includes recorded
preparation/control-plane overhead in physical forecasting. It adds explicit
single-execution and persisted-lineage validation cases. Research contrasts,
budgets and selection rules are unchanged; no live calibration or final evaluation
preceded these corrections. The earlier documentation-only review remains a
historical scope statement, not authorization for that review to execute code.

## Final preregistration check

Documentation review: no analysis selection is conditional on final evaluation
outcomes. The following choices must be fixed before any final evaluation access:

| Choice | Predetermined rule / outcome-independent check |
| --- | --- |
| Questions and contrasts | Q1 D@1 -> D@5; Q2 D@5 vs O@5; Q3 D@5 vs R@5, descriptive and confounded |
| H-I treatment | Effect, 10-point threshold, 95% cluster-bootstrap CI and recovery/cost evidence; no permutation p-value |
| H-F treatment | Two-sided paired template swaps, 100000 draws, plus-one p-value, alpha .05; sole confirmatory test, no Holm |
| Bootstrap | 10000 percentile replicates, seed 8006; whole templates within each fixed family, all instances/arms/horizons together |
| Cohort and difficulty | 96 tasks, 32 template clusters, eight families; all three tiers generated before development-only tier selection |
| Calibration decisions | Existing eligibility thresholds and deterministic tie-breaks; no hidden candidate scores, final-task trial runs or recovery-based tier choice |
| Checkpoint selection | First public pass, otherwise latest verified checkpoint, otherwise original; never best hidden candidate |
| Denominators / missingness | Whole cohort for success, initial verified failures for recovery, null for zero denominators; incomplete campaigns remain incomplete |
| Runtime and exposure | Fixed feedback, masking, continue/restart, horizons, budgets, schedule and stopping; no selective arm reruns or evaluation reuse |
| Interpretation | Prespecified materiality and uncertainty rules; report candidate formation and no equivalence claim from a nonsignificant or zero-recovery result |
| Additional analyses | Q3, intermediate horizons, family and cost summaries descriptive; no outcome-selected confirmatory tests, exclusions or sensitivities |

This is a design review, not a runtime validation result or authorization to
implement. A discovered integrity defect requires a documented amendment before
new execution; do not repair the analysis silently using final outcomes. Any
analysis added after exposure must be labeled exploratory and cannot change the
preregistered conclusion. The exposed evaluation cohort is retired.

## Methodological changelog

- **Changed:** made H-I's nested-prefix effect, 10-point materiality threshold,
  cluster-bootstrap inference, recovery denominators and marginal costs explicit;
  no H-I permutation/sign test or conventional p-value. **Why:** k=1 and k=5 are
  monotone prefixes, not exchangeable treatments.
- **Retained / clarified:** H-F paired effect, CI and cluster-aware label-swap
  p-value; no Holm across H-I/H-F. Any future confirmatory family must preregister
  its multiplicity rule. **Why:** D/O share the initial failure and H-F is now the
  sole confirmatory p-value.
- **Changed:** explicit Q1/Q2/Q3 labels, D/R confounding caveat, mandatory shared
  InitialPrefix lineage and validation cases, and the final outcome-independence
  checklist. **Why:** prevent conflating interaction with feedback or policy
  state, accidentally comparing different first candidates, or selecting analyses
  after seeing final results.
- **Unchanged:** 96 evaluation tasks / 32 clusters / eight families; three
  pre-generated tiers and development-only selection; D/O/R; detailed feedback
  and outcome-only masking; fresh restart versus failed-edit continuation;
  prefixes k=1..5; hidden-test isolation; protocol 0.5; 9h/9M forecast gate and
  12h/12M hard ceiling; task-cluster bootstrap; cohort retirement; fixed model
  and scaffold; no Planner, memory, generated tools or Pi work.
- **Scope:** documentation only. No M0.8 implementation, calibration, evaluation,
  freeze regeneration or hardware operation is performed in this revision.
