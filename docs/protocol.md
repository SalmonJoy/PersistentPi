# Research protocol 0.1

`PROTOCOL_VERSION` is `0.1`. Changing these semantics requires a new protocol
version. Configurations contain harness-validation limits, not Pi production defaults.

- A decision is one call to the model adapter, reserved and durably recorded before
  invocation. Finish, rejected actions and failed/uncertain model calls count.
- A tool call is a requested non-finish action admitted after a decision. Rejected
  calls count. Decision/token/wall exhaustion may prevent tool admission entirely.
- An attempt is an authorized public-verification submission of a content-addressed
  checkpoint, charged before launch. Failures, timeouts and verifier errors count.
  Invalid requests rejected before submission do not count as attempts.
- Runner sees only TaskView, public observations and remaining-budget DecisionState.
  Public feedback identifies its verifier/version, outcome, duration and bounded
  evidence. Hidden test paths, expected outputs, outputs and scores are absent.
- Stop at first public pass, explicit finish, attempt/decision/tool/token/wall
  exhaustion, manual STOP or interruption. A public pass is not benchmark success.
- Select the last submitted checkpoint, or the initial checkpoint if none. Unsubmitted
  edits are not the final benchmark candidate. Each submitted checkpoint records
  its parent; content-identical checkpoints retain the same hash.
- Hidden evaluation runs once after normal Runner termination, including budget
  exhaustion. It cannot restart the Runner or feed any observations to it/Planner.
  STOP and interruption are unevaluated. Evaluation failures/timeouts remain distinct
  from an ordinary hidden test failure; their score is NULL, not zero.
  Empty suites and skipped/expected-failure evidence are errors, never a pass.
- Runner wall budget uses monotonic time, including its model/actions/public tests.
  Preparation/private evaluation are separate overhead, recorded in end-to-end
  timing. Each test subprocess has its own cap; public cap is also bounded by
  remaining Runner time. Cleanup/commit overhead can overshoot wall-clock limits.
- Scripted token accounting is synthetic: task JSON size rounded up in units of
  four bytes, plus 32 input units per observation; output is action JSON size rounded
  up in units of four bytes. Minimum is one. No tokenizer or real inference is used.
  The deterministic estimate is admitted only if remaining token allowance suffices;
  denied estimates charge the decision but zero simulated tokens and no tool call.
- Limits apply to UTF-8 returned body bytes, exact-edit request size and total task
  workspace content. These are not hard caps on the database, evaluation copies,
  process RAM, CPU or host disk. Output streams are drained but only a bounded
  prefix is retained. Metadata envelopes can add serialization overhead.
- Manual STOP is a durable per-run flag. Check it at action boundaries and while
  polling supported public-test subprocesses. CTRL+C cleans up execution and records
  a stopped Runner; an interrupted active operation may remain pending/uncertain.
- Record starts before work and results after completion. Crashes leave incomplete
  receipts/attempts and last committed usage; status reconciles dead owner identity
  to interrupted, without replay or resume. Unknown owner state stays unresolved.
- Formal trials require clean Git provenance. Their key binds resolved manifest,
  task hash, budget, seed and replicate. Manifest binds protocol, scaffold, code,
  model/tool identities and execution profile. Same formal key cannot be inserted
  twice in one database; new databases do not provide global deduplication.
- UUIDs, UTC, monotonic session values and measured durations vary. Reproducibility
  means identical semantic actions, checkpoint hashes, budget counts and outcomes
  under controlled inputs. Exports of an unchanged database snapshot are deterministic.

Lifecycle: queued -> running -> finished / stopped / interrupted. `finished` means
Runner termination, not successful benchmark completion. Private evaluation has
its own pending/running/pass/fail/error/timeout/incomplete state and nullable score.
Every formal run records scaffold_id, nullable parent_scaffold_id, scaffold_hash,
scaffold_version, protocol_version and immutable harness hash via its manifest.

## Protocol 0.5: M0.8 acquisition and shared lineage

Protocol 0.5 is a separate campaign-manager path. Versions 0.1 through 0.4 retain
their existing meanings. All new window, prefix, receipt, projection and analysis
payloads carry version 1. The frozen M0.8 preregistration defines exact constants.

One acquisition window ends with one accepted-edit/checkpoint/automatic-public-
verification candidate or a terminal formation/STOP/infrastructure outcome.
Only verified FAIL opens another window. Each window has independent allowances,
with additional logical trajectory and physical campaign ceilings. The Runner
sees only current-window allowances, never its future candidate horizon.

An immutable InitialPrefix binds the single physical first acquisition, task,
manifest/scaffold/protocol, original and candidate checkpoints, model transcript,
public result and physical receipts. D/O/R have that exact shared parent. D/O
continue the failed state; R restores the original checkpoint and clears history.
D gets bounded public failure evidence; O gets only FAIL. Equal feedback capacity
governs context eviction. Candidate horizon 1..5 is reconstructed from saved
prefixes with terminal states carried forward, without advertised-budget reruns.

Generation seals before private scoring. Selected checkpoint = first public PASS,
else latest verified candidate, else original. Hidden tests never control retries
or selection. Logical policies each charge the prefix; physical generation pays
it once. Private scoring overhead is reported separately. SQLite enforces
immutable prefix/branch/receipt records and rejects private scoring before seal.

Canonical and human preregistration, generator/certification, prompt/projection,
statistics, schedules, budgets and code are frozen by hashes. Changed assets block
execution. Development-only calibration and forecast gates precede final launch;
the final evaluation cohort retires on launch. See `m08-preregistration.md`.
