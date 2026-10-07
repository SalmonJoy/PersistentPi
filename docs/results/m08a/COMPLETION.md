> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8A Completion

**Ready for M0.8B development calibration.** Protocol 0.5 experimental machinery
is implemented, validated and frozen. Live calibration remains pending. The final
96-task evaluation has not run. No Raspberry Pi access or modification occurred.

Implementation commit: `3ca52e4b1abbea65e28a0f06f329cafb46f66e77`.
The final archival commit is the repository HEAD containing this report; obtain
its exact identity with `git rev-parse HEAD`, avoiding a circular self-reference.
Annotated baseline tag `m0.7` resolves to
`eeaba4ce01ff1c7d5533018aaaf6855287d23613`. Protocol: **0.5**.
Runtime dependencies remain Python standard library.

## Validation

- The clean M0.7 baseline and exact HEAD were verified before implementation;
  its complete 208-test suite passed. Historical records and migration 001 remain
  unchanged. The original tests are retained; two storage assertions were adapted
  for append-only migrations rather than assuming exactly one schema version.
- The complete final suite passes: **248 tests, zero failures/errors/skips**,
  comprising the historical 208 plus 40 M0.8 tests. See `validation.json` and
  `tests.txt`. Unit tests require no live Ollama or Pi.
- **384 fixtures certified**: eight families, six distinct templates per family,
  three pre-generated tiers. Each tier has 32 development tasks (16 templates,
  two instances each) and 96 evaluation tasks (32 templates, three instances each).
  Each fixture has eight public and 32 disjoint hidden inputs.
- Reference correctness, mutant failure, public component witnesses, collision
  checks and single-E0 repair certification pass. Largest repair: **173 tokens**
  using the checksum-verified installed GGUF tokenizer, below 512 tokens.
- The mock campaign passes: **one shared InitialPrefix, three D/O/R branches,
  four physical acquisition windows** on one development fixture. D/R recover
  at candidate two; O stops without a second candidate. These scripted outcomes
  validate infrastructure, not model performance or scientific hypotheses.
- Physical generation costs 720 simulated tokens; the prefix costs 240 once.
  Logical policies charge D=360, O=360, R=480: 1200 total = 720 + 2*240.
  Actual preparation/private-measurement overhead is recorded separately.
- Horizons k=1..5 reconstruct. Hidden scoring occurs after generation is sealed;
  SQLite integrity, foreign keys, exported lineage and archive checksums pass.
- Shared-parent mismatch, identical-code/different-acquisition, duplicate initial
  execution, persisted lineage, exact restart/history clearing and outcome-only
  nonleakage tests pass. The prefix is not reacquired separately by policy.
- Family-stratified whole-template bootstrap and joint-template D/O permutation
  tests pass, including a full synthetic 96-task/32-cluster/8-family analysis.
  H-I has no p-value; H-F is the sole confirmatory p-value.
- Tier eligibility/tie-breaking, pre-inference audit selection for all tiers,
  reproducibility signatures, seeded schedules and physical forecasting pass.
  Forecast bundles include their preparation overhead and a window-count share
  of common control-plane overhead, rather than summing logical policy costs.
- The read-only audit passes. Its checks and identities are saved in `audit.json`.
  No final-outcome-dependent analysis choices were introduced.

## Freeze Identities

Freeze manifest: `docs/research-records/m08a/freeze.json`

SHA-256:
`4429c0cd91e7a4f06e93cdc0cd540b5808855c1cbc749a5d30c24ab5769c04d1`

Canonical preregistration: `docs/research-records/m08a/preregistration.json`

Canonical SHA-256/content hash:
`834256477c9226edfa3fce886fe30b36fbf1f617477d06f7a47577b6a7213d7d`

Human preregistration: `docs/m08-preregistration.md`

SHA-256:
`e5b41d498416925f3f8203c093e151fa7e018aeff8e4e2fd5cca11ce877ace9d`

Fixture certification SHA-256:
`b663fd3bd7cf7698d8129c35bbbe9b087fce82dc1d06d55101b96fd9f912c858`

Suite manifest content hash:
`714b91ebee1eb006929da5cbf46c7e978e06813d715e62294e1ee2e838e60ceb`

Mock research archive SHA-256:
`4f36513970a66b7ff865ecbb17d0a47ee698becb5c1c7a05ae491014b1c3fbc3`

The freeze binds 74 implementation/test/protocol/design files, all task hashes,
certification and model/tokenizer identity. It covers prompts, generator/recipes/
partition, tier selection, feedback, analysis/statistics, schedules, seeds, budgets,
costs and stopping rules. A changed file set or hash blocks generation/scoring.
Live commands require an externally supplied expected freeze fingerprint; the
manager also rejects an in-memory preregistration hash differing from the freeze.

The old `m08a-revision1/` snapshot is superseded, not a second valid freeze. Its
bytes and checksums were preserved. Revision 2 corrects pre-inference persistence
of audit choices, adds behavioral comparison and explicit lineage tests, includes
preparation overhead in forecasting, and binds the final methodological review.
No live calibration or final evaluation preceded these preparation corrections.

## Components

New package `src/persistentpi/m08/`:
`benchmark.py`, `tokenizer.py`, `runtime.py`, `campaign.py`, `feedback.py`,
`design.py`, `analysis.py`, `stagnation.py`, `freeze.py`, `mock.py`,
`case_harness.py`, and `__init__.py`.

`migrations/002_feedback.sql` adds campaigns, windows, immutable prefix/branch/
receipt lineage, deferred private scores, overhead and retired-cohort records.
The generic manager refuses unconfigured protocol 0.5 and preserves completed
windows awaiting deferred scoring. Existing protocol meanings remain unchanged.

`scripts/m08.py` provides explicit suite, validation, dry-run, freeze and future
live commands. `scripts/audit_m08a.py` audits saved evidence without inference.
`tests/test_m08.py`, `configs/m08-preregistered.json`, the permanent human
preregistration and protocol documentation are included. Export supports the new
records and a checksummed SQLite/JSON/CSV research archive.

This directory preserves tests, audit, canonical design, certification, freeze,
mock analysis/prefix CSV/JSON/costs and the mock research archive. `checksums.json`
binds the evidence files. Local fixtures and the dry-run database are in
`.local/m08a-suite-final` and `.local/m08a-dry-run-release`.

## Requirement Audit

The numbers below correspond to the goal objective's numbered requirements.
Evidence was inspected in source, tests, saved receipts and the freeze, not inferred
merely from a green summary. Live scientific results are deliberately pending.

[Private account observation retained privately.]

## Validation Commands

Run from `<private-workspace>`:


[Source-bearing example or private reproduction procedure withheld.]


To create independent repeat evidence, choose new, unused destinations:


[Source-bearing example or private reproduction procedure withheld.]


Use the rebuilt suite path if the original ignored local directory is absent.
Rebuilding is mechanical with frozen seeds/recipes, not task tuning.

## Future M0.8B Commands: Not Executed

Live calibration acquires 96 development prefixes (32 per tier), selects only by
the fixed public gate, continues the chosen 32 development tasks, performs 16
additional audit acquisitions and calculates the physical forecast. It does not
hidden-score model calibration candidates. If no tier qualifies, it stops.


[Source-bearing example or private reproduction procedure withheld.]


Only if that calibration receipt qualifies and its 90th-percentile forecast is
strictly below both 9 accumulated execution hours and 9 million measured tokens:


[Source-bearing example or private reproduction procedure withheld.]


The final matrix is 96 shared initial acquisitions, 288 logical D/O/R policies,
up to five candidates per policy and prefixes k=1..5. At most 1248 physical
windows occur (96 roots plus 96*3*4 continuations), not 1440 independently charged
windows. Actual success/formation stops reduce that bound. The hard 12h/12M
ceiling includes measured difficulty/continuation calibration and audit already
spent. No cohort shrinking, adaptive conditions, selective reruns or reuse of an
exposed evaluation cohort is permitted. Neither live command was run in M0.8A.

## Limits and Pending Measurements

Live Ollama availability/runtime identity, model determinism, actual development
difficulty and campaign cost remain unmeasured. Offline installed-model/GGUF
identity and tokenizer were verified; live launch checks digest, Q4_K_M and Ollama
0.35.1 again. Temperature 0/seed 42 do not guarantee backend determinism. Audit
repeats record behavior rather than introducing diversity or tuning the policy.

ASCII tokenizer certification rejects unsupported text instead of approximating
Unicode pre-tokenization. Forecast reserves up to 13 unique selected private
checkpoints/task at five seconds each (6240 seconds) without scoring hidden
development candidates. It is a development-based forecast, not a guarantee.
No tier qualification or launch approval is promised by infrastructure tests.

Subprocess cleanup/commit scheduling may overshoot a deadline; actual overhead
is recorded and remaining budgets prevent further work. Unknown token usage
interrupts the campaign. Interrupted campaigns stay incomplete, without automatic
resume or selective arm reruns. API/path checks, SQLite guards and the bounded
interpreter are not an OS sandbox or protection against a malicious same-user
administrator. No unrestricted generated Python or shell tool was added.

No Planner, persistent cross-task memory, generated tools, teacher/cloud model
or Pi work was introduced. Synthetic fixed-family tasks limit generalization;
small template counts and degenerate bootstrap intervals are not equivalence
evidence. D/R remains a confounded policy comparison. Mock recoveries are not
a scientific positive result. M0.8A stops here, before live calibration/evaluation.
