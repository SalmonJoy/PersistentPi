# M0.8H: E1 Output Ceiling Ablation

Protocol 0.5. Starting clean evidence `00b51ff`, annotated `m0.8g`.
Preserve B/C/D/E/F/G unchanged. No final evaluation, hidden asset access or scoring.
This is an exposed development diagnostic, not final Runner selection.

## Questions and Design

Primary: does increasing only the response ceiling reduce truncation failures and
increase verified candidate formation? Secondary: does public correctness persist
among recovered candidates? Use exactly G's same 16 L2 public development tasks,
no new/fresh tasks. Freeze all eight G E1 ACT length-terminated, 512-token,
JSON-parse-failed task IDs from `outcome-audit.json` as historical_truncation_subset.
The config contains the fixed opaque IDs; provenance/hash is saved before inference.

A: fresh E1/512. B: fresh E1/1024. Everything else stays G E1: exact 3B digest,
Q4_K_M, Ollama 0.35.1, template/system/tokenizer, temperature 0, seed 42, context
4096, think=false, keep_alive=5m, request timeout 30s, E1 schema, generic historical
rejection projection, task/tools/prompts, INSPECT->ACT, Supervisor and public verifier.
No explicit output-length hints, shortening instructions, repair, parser completion
or semantic assistance. Initial A/B messages must be byte-identical to G E1.
Identity metadata includes num_predict; the only permitted identity-settings
difference is 512->1024, not weights/runtime/template/context or any other setting.

Each task starts fresh twice from its exact original checkpoint. Sort templates,
alternate AB/BA starting AB: eight pairs each order, 32 windows. Freeze schedule;
never reorder, selectively rerun or resume. One sequential inference at a time.

## Budgets and Necessary Adapter

Both retain 15 decisions, 15 tools, 16000 measured input+output tokens, 120 seconds;
one-tool/5s public-verification reserve, test timeout 5s, file/edit 8192 bytes,
workspace 10485760 bytes, verifier output 4096 bytes. Model-content parsing remains
the historical 16384-byte bound. Campaign: 32 windows /480 calls /512000 tokens /
4800 seconds including control/finalization, no warmup. Raising num_predict does
not increase the overall window/campaign token budget or context.
Admission necessarily reserves upper-bound prompt tokens plus configured response
ceiling; B may consequently deny a call sooner. Record this, never relax admission.

Historical loop contains a literal measured-output guard of 512. An isolated,
trusted-source AST adapter changes exactly that literal to the frozen arm ceiling.
It takes only the immutable historical loop, never model/telemetry-supplied code.
Both arms use the same adapter; a structural parity test requires every other
statement to be identical. Acquisition reuses the original bytecode with private
module-constant bindings for E1 in both arms and the ceiling-aware window class.
Original modules/globals/bytecode remain unchanged. Request replay adapts only
the expected num_predict field and binds both arms to E1; explicit tests prove it.
No arbitrary self-modification or new Runner-visible tool.

Stop at first verified candidate, GIVE_UP, malformed output, budget exhaustion,
STOP or infrastructure failure. No public failure returns for repair. Interrupted
campaign is incomplete; preserve all costs and do not retry. A STOP file is checked
through the historical cancellation path. No automatic ceiling increase beyond1024.

## Measures and Fixed Definitions

Verified formation: accepted state-changing replacement, checkpoint, automatic
public PASS/FAIL and finished window. Rejects/no-ops/malformed text are not candidates.
Primary truncation failure requires terminal malformed output in ACT, backend
done_reason=length, measured output tokens at the arm ceiling and JSON parse failure.
Other malformed/schema errors, context admission and budget limits remain separate.
Ceiling saturation alone is not failure: complete valid JSON at the exact ceiling
may still form a candidate. Preserve backend termination and structural completeness
separately. Unknown telemetry stays unknown, never forced into truncation.

Every generation, including inspection: phase, measured input/output tokens,
ceiling reached, backend reason/status, response bytes/hash, JSON parse/completeness,
schema validity, action type (unknown for unparseable text), authorized status,
changed replacement, static Python syntax and historical acceptance/checkpoint.
Do not finish or execute truncated/counterfactual code. All generation records remain
available, not only accepted EDITs. For B report distribution of completed output
lengths >512, and all outputs reaching1024. Compare paired task saturation, including
tasks where A hits512 and B hits1024 without formation. No hidden feedback.

Funnel: tasks -> ACT candidate-response opportunity -> output complete -> JSON
parsed -> authorized E1 -> changed replacement -> syntactically valid -> checkpoint
-> public verification -> PASS/FAIL. ACT opportunity excludes parsed finish, but
includes unparseable ACT responses; it is not proof of a fully expressed EDIT.
Report recognized replace_file count separately to avoid misclassifying truncations.
Output complete means normal backend completion OR structurally complete JSON;
backend length flag remains explicit. Syntax is static Python syntax, not semantic
correctness; policy rejection is separately reported. Task counts mean at least
one qualifying response; raw generation/proposal counts remain separate.

Report all 16 paired rows and eight historical-subset stage rows, E0 not rerun.
Public pass/fail, public_pass_given_candidate, fresh/historical subset rescues,
first candidate status and stop reason; completed>512 tasks/generations; new1024
saturation; token distributions (min/median/p90/max and sorted values, inclusive
linear-interpolation quantiles), model calls, input/output/total tokens, inference,
window and physical wall, calls/tokens per candidate and tokens per public pass.
Include failed windows in cost denominators; zero denominators=null. Inference and
verification are components of wall. Allocate shared overhead equally, not by outcome.

## Engineering Rules (Before Outcomes)

Strong: paired truncation count reduction within fixed historical subset >=6;
B formation>=12; B public passes>=6 (at most one below historical G7) AND no more
than one below fresh A. This operationalizes "not materially reducing" public count.
Partial: truncation decreases and net formations increase, but B<12. If formation
>=12 but other strong requirements fail, label mixed/qualification failure with
explicit failed criteria, not strong. A one-task partial is small descriptive evidence.
Ceiling merely moves: >=4 historical-subset tasks truncate under both512 and1024
without a B candidate. Report this flag even alongside partial gains; do not raise
the ceiling again. Classification priority: incomplete, strong, moves, partial,
mixed/qualification failure, no observed operational benefit. No benefit means
no truncation decrease or no net formation gain, with all secondary outcomes retained.
All flags/counts are reported, so a label cannot erase public correctness or costs.
No p-value, population/equivalence claim or final benchmark promotion.

Next step is recommendation only: strong may support separately preregistered
development confirmation of E1/1024 (no final evaluation/repair automatically).
Partial/moves/mixed/no-benefit calls for a separate development-only acquisition
diagnosis/confirmation, not an automatic further ceiling increase or model switch.
If few verified failures remain, do not claim readiness to measure repair scaling.
No 7B, sampling, Planner, memory/tools, Pi work or further experiment launched.

## Validation and Integrity

Before inference: all 328 historical tests and isolated H mock tests pass; guard/
acquisition/replay parity, only num_predict changed, prompt/schema equality, exact
identity/tokenizer, budgets/admission, subset/manifest, schedule/checkpoint pairing,
metrics/boundary classification, public-only/no-repeat/no-repair, STOP/infrastructure
and receipt reconciliation. Synthetic unit fixtures are not the sealed evaluation
cohort and perform no live inference. No actual frozen evaluation/hidden loader.

Freeze clean implementation commit/files, identities, exact public inputs, subset
provenance, configs/schedule/prompts/E1 schema/budgets/analysis and test receipts.
Metadata preflight only before run, no chat/pull/warmup. Material mismatch blocks.
After execution, replay requests and projections, exact ceilings/tokens, receipts,
pairing, one candidate and public verification, task/permission boundaries, DB/ZIP
checksums and consistent SQLite backup API. Preserve raw data and all failure costs.
Save full Markdown report, JSON/CSV generations/task results, paired/subset tables,
histories, archive checksums, pre/post tests and requirement-by-requirement audit.
Freeze/executed/evidence commits remain distinct. Read-only reproduction is default;
new live reproduction needs authorization and a fresh frozen checkout/state.
Stop after H; all 96 evaluation tasks remain sealed and G is not reinterpreted.
