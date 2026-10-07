> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.9B Offline Completion Record

Status: offline implementation and evidence verified. This is not a live model result.
The implementation starts from `28e44ee045a69f074e800d780129bd6457d4f0cd`.
The annotated `m0.9a-plan-baseline` tag preserves that point. The final evidence
commit is resolved by `git rev-parse m0.9b^{commit}`. The implementation commit is
`4e327a1eb6e4310ebe5bdcff6ff73a2452ec912e`.

## Verified Results

- 479 tests passed: 384 historical regressions and 95 new offline tests, zero
  failures/errors/skips. `validation.json` certifies unchanged trusted source
  hashes throughout testing, matching the authoritative freeze.
- All 304 historical public wire requests match: B0 141, B1 163. Full historical
  system text is explicit in each reference spec; prompt-only mutations preserve
  context/schema/options, avoiding an unintended renderer switch.
- Search32 hash: `b05e7688f679513c2af880c081e5a4c0324ddb05899548539c97bb7963982e35`.
- Qualification48 hash: `6784d6b2694ef0f35165f3ecd2cf6d3850de322ff27ad7214a9ee9bc397fd0df`.
- B0 scaffold: `3523ba5db8fee37ed9465947970b20ef61a336ee08527c3c9abdf9cda2cf8413`.
- B1 scaffold: `816fe91c71baad3187fa4168f2d5f450c512a14477843d642f0d435992476640`.
- All 48 qualification instances certified: eight reference passes each, at least
  one mutant failure, two component witnesses, exact family/template/parameter counts.
- Disclosure/canary, budgets/forecast, interruption, bootstrap/promotion, SQLite
  migration/WAL/integrity and deterministic export/replay checks passed.
- `prepared/freeze.json` SHA256:
  `341f379a52d7c3afcf32a761f6eb160b31b6db0d4119e0abdb8055f1126ffd56`.
  `completion-audit.json` reconstructs all saved campaigns and binds test/source hashes.

| Synthetic campaign | Started / completed windows | Terminal result | Replay |
| --- | --- | --- | --- |
| A | 368 / 368 | Qualified; both lower-bound gates pass | Pass |
| B | 64 / 64 | No generated full scaffold after invalid/duplicate slots | Pass |
| C | 368 / 368 | Qualification failed; no replacement finalist | Pass |
| D | 1 / 0 | Indeterminate infrastructure stop; no rerun | Pass |

These counts are offline simulated equivalents, not measured Runner capability.
Unknown D usage is a separately labelled reservation upper bound. All four databases
reported `integrity_check=ok`, no foreign-key violations. Historical tracked code,
tests/configurations/evidence remain unchanged; the 96 final tasks are untouched.

## Scope

Protocol 0.6 adds a standard-library-only, configuration-only Planner optimization
platform. No Runner/Planner inference, credential use, final-task contents or actual
benchmark hidden scoring is authorized or performed. Historical private-evaluator
regressions use hand-written/synthetic fixtures, not the reserved benchmark.
All fake outcomes/calls/tokens are simulated equivalents, not measured capability
or purchased compute. Actual offline wall time is recorded separately.

The stronger progression gate is symmetric: the family-stratified paired whole-
template 95% bootstrap lower bounds must exceed zero against both B0 and B1,
in addition to formation/pass/family/+8 thresholds. It is not confirmatory inference.

## Components

- `src/persistentpi/m09/spec.py`: strict ScaffoldSpecV1, normalized identity,
  compiler, frozen E0/E1 JSON/schema-JSON/DSL catalog and strict proposal envelope.
- `render.py`, `runtime.py`, `screening.py`: deterministic rendering/controller
  allocation, charged preload, bounded single-candidate execution and offline
  smoke validation. Existing Supervisor/public AST interpreter are reused.
- `cohorts.py`, `preparation.py`: exposed Search32, Screen8/complement, deterministic
  Qualification48 certification, access barriers and freeze verification.
- `disclosure.py`, `planner.py`: source-free typed projections and exact request
  receipts; fake Planner and disabled-by-default cloud transport abstraction.
- `storage.py`, `manager.py`: durable four-round/two-slot search, full-cohort archive,
  one frozen finalist, one-shot qualification, separate ledgers and recovery rules.
- `analysis.py`, `export.py`: exact score unions/ranking, symmetric paired bootstrap,
  consistent SQLite backup exports and inference-free decision replay.
- `migrations/003_optimization.sql`: additive optimization tables, foreign keys,
  actor/phase restrictions, hidden-scoring denial and immutable receipt triggers.
- `scripts/m09b.py`, `scripts/m09b_tests.py`: offline commands and acceptance tests.

## Requirement Audit

The entries below identify the evidence to inspect, rather than treating absence
of errors as proof. The final validation/freeze/campaign receipts must all pass
before this milestone is marked complete.

[Private account observation retained privately.]

## Cohort Identities

Execution and frozen manifests use canonical cohort labels `search` and
`qualification`; their exact hashes are identical in `prepared/freeze.json`, the
corresponding cohort manifest and every result receipt. The filenames `search32`,
`screen8`, `remaining24`, and `qualification48` are descriptive filenames only.
Full-search comparisons always use the execution `search` hash and all 32 tasks;
qualification comparisons always use the execution `qualification` hash and all 48.
The final 96-task cohort is not loaded to construct either cohort.


[Private task-level/operational evidence retained in the research repository.]

## Limits

Trusted host administrators are outside the threat model. The benchmark executes
only bounded pure-function ASTs, not arbitrary repositories or arbitrary Python.
Malformed/code-bearing fields are rejected rather than repaired. Complete records
are immutable to model-facing clients, not cryptographically signed against a
malicious host administrator. Unresolved resource usage is separately labelled
reserved/indeterminate upper bound, never claimed as measured expenditure.

Historical regression fixtures are intentionally different from the reserved
benchmark; the logs document that policy. An early full run had one timing-sensitive
M0.8G mock-count failure; its isolated rerun passed and the subsequent 470-test
combined run passed. Those earlier logs remain under `.local` and are not rewritten.
The final run must verify the current code remained unchanged throughout execution.
