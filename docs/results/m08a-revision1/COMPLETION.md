> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8A Completion

M0.8A implements, validates and freezes the experimental machinery. **Ready for
M0.8B development calibration.** Live calibration remains pending. The final
96-task evaluation has not run. No Raspberry Pi access or modification occurred.

Implementation commit: `9cde63ad580dd5e0430a85f8a735371256cc6045`.
The final archival commit is the repository HEAD containing this report; use
`git rev-parse HEAD` to obtain it without a circular self-reference in the file.
Annotated baseline tag `m0.7` resolves to
`eeaba4ce01ff1c7d5533018aaaf6855287d23613`.
Protocol version: **0.5**. Runtime dependencies remain Python standard library.

## Evidence

[Private account observation retained privately.]

## Freeze Identities

Freeze: `docs/research-records/m08a/freeze.json`

SHA-256:
`e5af2b923dbd3a6a6e9637f250f1d05d75f5651ed7c198c08966e696509039c9`

Canonical preregistration: `docs/research-records/m08a/preregistration.json`

Canonical SHA-256/content hash:
`b08429d0b48aa35c016d08ab7f44f53ac30482b9b4339c282a8c13e6715184d4`

Human preregistration: `docs/m08-preregistration.md`

SHA-256:
`9907be0034ead174c91d76ce5aa0e5630b03a4702aea6ea1ad02c6649e94c048`

Fixture certification SHA-256:
`b663fd3bd7cf7698d8129c35bbbe9b087fce82dc1d06d55101b96fd9f912c858`

Suite manifest content hash:
`714b91ebee1eb006929da5cbf46c7e978e06813d715e62294e1ee2e838e60ceb`

The freeze binds code, tests, protocol, human/canonical design, prompts,
generator/partition, feedback, analysis, scheduling, seeds, budgets and costs.
The manager refuses a changed freeze, preregistration, task or model identity.
An external expected freeze fingerprint is mandatory for live commands.

## Components Added

`src/persistentpi/m08/` contains separate benchmark/certification, tokenizer,
window runtime, immutable prefix and campaign manager, projections, calibration/
forecast/scheduling, analysis, stagnation measurements, freeze and mock fixtures.
Migration 002 adds campaign/window/prefix/branch/physical receipt/private score
records with lineage and sealing guards. Existing generic manager paths refuse
unconfigured protocol 0.5 and preserve finished deferred windows in status checks.

`scripts/m08.py` exposes suite generation, validation, mock dry run, freeze checks,
and explicit future calibration/evaluation. `scripts/audit_m08a.py` verifies saved
preparation evidence without model calls. Configuration and permanent
preregistration documents are saved. Export includes new records and checksums.

Archived artifacts here include the final test log, canonical preregistration,
certification, freeze, audit, mock analysis/prefix CSV/JSON/cost report and a
checksummed mock research archive. Current local suite and dry-run database are
under `.local/m08a-suite-final` and `.local/m08a-dry-run-final`.

## Validation Commands

Run from `<private-workspace>`:


[Source-bearing example or private reproduction procedure withheld.]


To rebuild missing local fixtures on the same frozen installation, use a new
destination and replace the suite path in later commands:


[Source-bearing example or private reproduction procedure withheld.]


## Future M0.8B Commands: Not Executed

Live calibration acquires 96 development prefixes, applies the fixed tier gate,
continues only the chosen 32 development tasks, performs 16 audit acquisitions and
produces a physical forecast. It never hidden-scores model calibration candidates.


[Source-bearing example or private reproduction procedure withheld.]


Only after calibration qualifies and the 90th-percentile forecast is below both
9 hours and 9 million tokens would this command launch final evaluation:


[Source-bearing example or private reproduction procedure withheld.]


Evaluation uses 96 shared prefixes/288 logical policies, horizons 1..5, and the
12-hour/12-million-token hard campaign ceiling including prior measured work.
There is no guarantee any tier qualifies or the forecast permits launch.
Neither command above was run during M0.8A.

## Limits

Online Ollama identity/availability and actual calibration difficulty/cost are
still unmeasured in M0.8A. The installed model manifest/GGUF tokenizer was verified
offline; runtime version and quantization are checked again at live launch.
Tokenizer certification supports this ASCII authored corpus and rejects other
text instead of approximating its Unicode pre-tokenization. Temperature zero is
not claimed to guarantee backend determinism; the audit records repeated behavior.

Forecasting reserves up to 13 private selected checkpoints/task at five seconds
each, adding 6240 seconds without inspecting hidden development candidate scores.
Cleanup/commit scheduling can overshoot a subprocess deadline; actual overhead is
recorded separately and stops prevent further launches. Unknown inference usage
interrupts the campaign. Interruptions are not silently rerun or partially promoted.

These API/path controls and the bounded interpreter do not establish an OS
sandbox. No unrestricted generated Python, shell tool, Planner, persistent memory,
generated tool, cloud model or Pi operation was introduced. Fixed-family synthetic
tasks constrain generalization. Mock recoveries are infrastructure evidence only.
