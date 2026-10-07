# M0.8D: E0 versus E1 Acquisition Ablation

Protocol 0.5. Preregister before live inference. Prior M0.8B calibration stop and
M0.8C failed precise-feedback gate are preserved. No wording optimization or
automatic confirmation. This protocol freezes the analysis before outcomes.

## Question and Conditions

Does requiring the small Runner to reproduce both old and new content suppress
state-changing candidate formation? A uses historical E0 `edit_file(path,old,new)`;
B uses existing E1 `replace_file(path,content)`, complete replacement text, no old
field. Strict JSON schemas. No content repair, syntax correction, code selection,
merge, new model, Planner, memory, generated tools, temperature change or Pi work.

Fixed Runner: qwen2.5-coder:1.5b, Q4_K_M, Ollama 0.35.1, digest
`d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668`.
Temperature 0, seed 42, context 4096, output 512, think=false, timeout 30s,
keep_alive=5m. Verify exact model, backend template/system and tokenizer identity
against M0.8C before and after generation; never silently update the environment.

One source READ transitions C3 INSPECT -> ACT. ACT allows the arm's edit primitive
or finish/GIVE_UP. Accepted edit -> automatic public verification -> terminal.
One candidate = byte-changing accepted edit, checkpoint, automatic verification.
Model decides semantic edits; Supervisor decides application and verification.

## Freshness, Pairing, Limits

Use the OTHER instance of each of 16 L2 development templates by excluding the
16 M0.8C manifest IDs from the 32 M0.8B L2 records. Eight families. "Fresh" means
not live-exposed in M0.8C, not unseen: all were M0.8B calibration-exposed. Select
using metadata only, not correctness. Load public development checkpoints and
task-view requests from the historical archive through a kind/visibility whitelist.
Do not open the frozen benchmark ZIP, suite task files, evaluation tasks or hidden
tests. Hash the benchmark archive as opaque bytes for preservation only.

Each task gets independent A/B windows from the exact original public checkpoint.
Freeze template-sorted pairs with AB, BA, AB, BA, starting AB. 32 windows, no
outcome-dependent schedule changes, no warm-up inference or selective reruns.

Each window: 15 decisions, 15 tools, 16000 measured input+output tokens, 120s;
the historical admission guard reserves prompt upper bound plus 512 output tokens.
Reserve one additional tool call and 5s before accepted edits for verification.
One candidate maximum; verification timeout 5s; output bytes 4096, workspace
10485760, edit ceiling 8192. Campaign maximum 480 calls, 512000 tokens, 4800s
including generation overhead; manual shared or arm-local STOP. Stop on first
verified candidate, GIVE_UP, malformed output, budgets, STOP, infrastructure error.
Interruptions produce an incomplete record; no retry/resume. No repair cycle.

## Primitive Fairness and Boundary

Only the edit contract changes. Source, task requirements, tests, budgets, context
packing (7000 bytes, 1800 per field, recent four observations), inspection and
verification are fixed. Prompt changes are the existing primitive example,
replacement-size sentence, tool registry/contract and available-action identifier.
No diagnosis, fix hints or expectations about which arm should work better.
Freeze both initial prompt hashes and token upper bounds; actual per-call hashes,
input/output tokens, schema, options and projection are logged and replay-audited.

E0 is unmodified. E1 uses existing Supervisor path confinement, allowed-editable
source validation, UTF-8/NUL checks, 8192-byte original/replacement file ceiling,
no-op rejection, workspace ceiling, bounded-Python parse, pre-edit checkpoint,
atomic write, and the SAME inherited public verifier with post-edit checkpoint.
Checkpoint receipt IDs can differ but source/public workspace hashes must match
between independently initialized A/B task runs.

Both primitives project equivalent unchanged and oversize rejections to historical
`Edit is empty, unchanged or too large`. Raw E1 errors stay in telemetry. Do not
carry forward precise M0.8C feedback. Path, schema, bounded-Python and reservation
errors are unchanged. E1-specific NUL/text error remains `Replacement requires
text files`; E0-only match error remains `Edit requires exactly one matching
occurrence`. No effort is made to hide unavoidable semantic contract differences.
E0 sizes serialized patch arguments; E1 sizes complete original/replacement files.
Both ceilings are 8192, not artificially equal token costs. E1 prewrite checkpoint
adds mechanical overhead; report it, do not claim equal-compute treatments.

Historical execution files are unchanged. E1's isolated loop duplicates historical
Window.run with only two edit-identifier predicates generalized; AST parity test
enforces this. E0 directly uses historical Window.run and historical prompt.
The controller's E1 identifier adapter only updates accepted-edit bookkeeping;
it never rewrites a model action or supplies old code to E1 execution.

## Outcomes, Analysis, Gate

Primary: paired verified-candidate formation difference B-A over 16 task pairs.
Report B-only wins, A-only wins, both, neither; net formations; family coverage.
Preregister ALL progression conditions: B>=13 formations; B-A>=4; B formations
in >=6 families; B>=8 public failures. This is an engineering gate, not a p-value
or proof of equivalence. Passing permits consideration of separate confirmation,
not its automatic execution. Missing any gate does not advance.

Funnel per arm: tasks -> source inspected -> EDIT generated -> strict action/schema
valid -> authorized -> state-changing -> candidate checkpoint -> verification
-> parallel public PASS/FAIL. At-task at-least-one counts with adjacent conversion
rates. Strict action validity is not program correctness. Offline authorization
reconstruction for reservation-rejected edits is separate from actual execution.

Diagnostics: accepted and rejected proposals/errors; repeated canonical proposals;
[Source-bearing example withheld.]
no-op proposals/all proposals; changed-edit tasks/16; formations/16; first changed
edit decision index and cumulative measured tokens; preceding no-op count (null
if no changed edit); calls/tokens/inference/wall per formation including failures.
AST-changed candidates and post-rejection byte/AST proposal change are secondary.
[Source-bearing example withheld.]
execution never uses that representation. Normalization does not establish semantic
reasoning or equivalence. Public correctness is secondary; hidden is unobserved.

Exploratory paired template-cluster bootstrap, stratified by fixed family, 10000
replicates, seed 8006, percentile 95% interval. No p-value or data-dependent
selection, exclusions, threshold changes, stopping, or promoted condition.
Incomplete campaigns cannot pass the gate. Report all exposure/costs nonetheless.

Interpretation: clear gate-passing formation benefit supports an E0 representation
bottleneck on these development instances; improved changes below gate are promising
but do not advance; E1 repeats source without more changes means removing old did
not resolve the dominant behavior; worsening favors retaining E0. These cannot
establish intrinsic capability, final/hidden generalization, or feedback-driven
repair/test-time scaling. If E1 improves, representation/output burden/state checks
are a complete contract treatment, not separable causal effects in this pilot.

## Integrity and Deliverables

Freeze code commit, public inputs/manifest, A/B configs, schedule, identity,
prompt hashes, schemas/contracts, error projection, budgets, gate/analysis code.
All prior tests and new fake-model tests pass before live inference; unit tests
do not need Ollama or frozen benchmark access. Historical code/assets are checked
against cb08346, accounting fixes included; earlier live freezes remain historical.

After execution: replay every request/schema/projection/remaining budget, controller
and model identity; verify arm primitive, paired original checkpoints, order,
single verification, candidate bookkeeping, time/call/token ceilings, cost receipts,
SQLite integrity/FKs, export tables/artifact hashes, hidden/evaluation exclusion.
Read-only archived audit must work without live model. Preserve raw results;
document corrected derived reports without reruns if an aggregation defect appears.

Archive consistent SQLite backups, exports, raw/corrected results, paired CSV,
freeze inputs, test receipts, audit, checksums, report and reproduction commands.
Record final evidence commit and annotated M0.8C tag. Leave all 96 intended final
evaluation tasks sealed (96 per potential tier). No evaluation decision, retirement,
confirmation, repair scaling or M0.9 automatically follows. Stop after M0.8D.
