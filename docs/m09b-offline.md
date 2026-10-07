# M0.9B Offline Operations

Protocol 0.6 is additive. No live model transport or final evaluation launcher is
enabled in this milestone. Use the repository Python 3.11+ environment, with no
new package dependencies. All commands below run from `research/PersistentPi`.

```powershell
.\.venv\Scripts\python.exe -B scripts/m09b.py validate --output .local/m09b-validation-new
.\.venv\Scripts\python.exe -B scripts/m09b.py prepare --output .local/m09b-prepared-new
.\.venv\Scripts\python.exe -B scripts/m09b.py verify-freeze --prepared .local/m09b-prepared-new
.\.venv\Scripts\python.exe -B scripts/m09b.py mock --prepared .local/m09b-prepared-new --output .local/m09b-mock-A-new --scenario A
.\.venv\Scripts\python.exe -B scripts/m09b.py replay --prepared .local/m09b-prepared-new --archive .local/m09b-mock-A-new/research.zip
```

Choose fresh output directories. Preparation never replaces an existing freeze.
Scenarios A/B/C/D are synthetic outcomes, not measured model performance. A
exercises qualification success, B invalid/duplicate proposals and no finalist,
C qualification failure, D an indeterminate infrastructure/integrity stop. Only
scripted fixture executors run deterministic public verification in unit tests.

The full validation command preserves historical test bodies. Historical benchmark
generator tests use separately namespaced synthetic fixtures with parameters 7..11,
not the frozen parameters 2..6/final cohort. Historical private-evaluator regression
tests use synthetic or hand-written unit fixtures only. This is not actual
benchmark hidden scoring. The harness rejects live HTTP connects while permitting
mocked HTTP contract tests. It limits historical archive-freeze inventories to
baseline tracked paths so new protocol files do not reinterpret prior evidence.

The freeze includes code hashes, prerequisite hashes, cohorts/public qualification
instances, reference identities/configurations, catalog and schema, preregistration,
parity proof and environment. `verify-freeze` rejects changed code or artifacts.
It does not pin a cloud backend. Reports are research artifacts, not model inputs.
Only the positive-allowlist projection is shown to the fake/future Planner.

## Trust Boundary

Models never receive database/filesystem handles or an arbitrary command tool.
Planner proposals are data-only; no eval/exec/import of proposed code. Runner edits
are confined to declared task files and must pass the existing bounded-Python AST
policy before checkpoint/public verification. The verifier interprets supported
pure Python functions with existing value/step limits in a timed subprocess;
it does not execute arbitrary generated Python through Python exec. This is a
restricted benchmark platform, not a general-purpose OS sandbox.

SQLite foreign keys/triggers and content hashes enforce lineage, unique task
receipts, phase/arm restrictions and immutable completed records. Trusted host
administrators can still change files/SQLite or run arbitrary Python: no claim of
protection against a malicious host administrator. Frozen-code verification is
required before any future campaign, and only trusted adapters may be admitted.

One clean workspace is created per candidate job. An accepted changed edit triggers
verification and terminates the window, even on public failure. Mechanical retries
are bounded; no post-failure repair, semantic helper or new serialization codec was
introduced. The retry factor controls malformed-response continuation; historical
rejected edits still use ordinary budgets and the optional stagnation cap.

## Recovery

`OptimizationStore(..., campaign_id=recorded_id)` validates unchanged config and
cohort identities. `SearchManager.run()` reuses completed receipts and may start
reserved, never-started work. Started interrupted work or a sent request with no
complete durable result becomes indeterminate and stops the campaign. Do not
delete/reset rows or selectively rerun tasks. A durable finalist freeze resumes
the qualification phase without another search proposal or finalist selection.

An internal planned idle pause requires no operation in flight; `store.pause()`
records it, and `store.resume_pause()` records idle duration without charging it
to active wall. This is campaign accounting, not pausing the assistant's goal.
Unexpected process downtime cannot be measured by a monotonic clock across process
restart; it is not represented as active inference. Persisted elapsed time remains
cumulative, and interrupted started work cannot resume.

## Future M0.9C Admission

The exact currently available command is a non-executing admission checklist:

```powershell
.\.venv\Scripts\python.exe -B scripts/m09b.py m09c-admission-plan
```

There is intentionally no executable live-launch command yet. After separate
M0.9C authorization, connect the transport abstractions to measured/pinned laptop
Runner and cloud metadata without changing frozen scaffold/evaluation semantics.
Freeze available Planner identity, supported configuration mapping and complete
provenance; unsupported seed is explicit, not disqualifying. Verify free included
allowance, no purchased credits/top-ups/fallback, forecast <9 active hours/<4.5M
Runner tokens and qualification reservations. The separately authorized launch
must reject any unfulfilled gate rather than silently enable a backend. Output
variation alone is not an identity-drift detector; unknown usage or observable
model/configuration-contract drift stops integrity. Never use the supplied cloud
credential in saved provenance.

M0.9B does not establish live model correctness, cloud access, statistical benefit
or optimizer reliability. Qualification transfer is instance-level within known
templates. The reserved 96-task final cohort and hidden scoring require a separate
later study. Future arbitrary code mutation, cross-task memory, generated tools
and Pi deployment are excluded.
