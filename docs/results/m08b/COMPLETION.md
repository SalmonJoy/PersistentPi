> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8B conditional completion audit

The task's final state is **reported, audited negative calibration**, not a
completed 96-task evaluation. Section 3 of the saved [objective.md](objective.md)
requires stopping if no tier qualifies. All remaining live-research stages are
conditional on eligibility; none is silently treated as executed.

| Objective section | Requirement and authoritative evidence |
| --- | --- |
| 0 | Clean HEAD 75c2e5c, full 248-test preflight, annotated m0.8a, frozen file/preregistration/task/analysis/schedule/model/scaffold hashes: preflight.json and preflight-validation/. |
| 1 | Exact frozen model, digest, runtime, quantization, template and request settings: preflight.json; integrity.json validates all 1,047 requests; reporting operation rechecked complete model identity after execution. |
| 2 | 32 initial acquisitions per tier, 96 total; all requested qualification/cost/termination measures: difficulty.json, tiers.csv, tasks.csv, summary.json and raw database. |
| 3 | No qualifying tier; stop without replacement/tuning/evaluation: tier-selection.json, execution-receipt.json, terminal campaign state and zero evaluation/continuation records. Negative calibration archived and formally reported. |
| 4 | Selected-tier artifact conditional: none selected. The negative selection receipt is preserved and checksummed instead. |
| 5-6 | Selected-tier continuations and 16 reproducibility repeats conditional: not eligible, zero executed; no positive-recovery criterion or determinism claim substituted. |
| 7-8 | Forecast and forecast launch gate conditional: not reached, no forecast calculated; not mislabeled as resource-forecast failure. Thresholds unchanged. |
| 9 | Final evaluation seal conditional: not reached. Preflight preserves all potential evaluation schedules/task identities; no final inference launched. |
| 10-12 | 96 final shared acquisitions, branches, k=1..5 horizons conditional: not executed. Actual calibration contains exactly 96 initial windows and exact prefixes, no branches or free resets. |
| 13 | Hard limits unchanged; 1,122,326 measured tokens and 4,865.993 recorded seconds, with observed creation-to-last-termination span 4,875.531 seconds. No hard-limit termination. |
| 14 | No interrupted/stopped windows or reruns: all 96 runs status finished; stop reasons in summary.json. Frozen interruption rule retained. |
| 15 | Live hidden nonleakage: zero hidden evaluations and zero m08_scores in raw database; all live runs are development/calibration. Reference certifications and mocked tests are not live candidate hidden scores. |
| 16 | Appropriate terminal generation/data seal: raw/generation-seal.json binds tables, artifacts, requests/responses, costs and terminations. Hidden scoring explicitly unauthorized for stopped calibration. |
| 17-20 | Hidden measurement and H-I/H-F/Q3 analysis conditional: not executed; effects, intervals and p-values marked not estimated. No inappropriate partial-cohort statistics or significance/equivalence claim. |
| 21-25 | Final curves, repair rates, marginal efficiencies, feedback/restart comparison conditional: not observed, not assigned zeros; original fixed horizons/conditions preserved. Initial development rates and spent costs remain available. |
| 26 | Frozen, observer-only stagnation metrics applied per initial window: difficulty.json/tasks.csv; counts in summary.json and REPORT.md. No controller intervention. |
| 27 | Applicable live audit: unique initial acquisitions, exact prefix/run/task/scaffold identities, settings, schedule, budgets, receipt IDs, event sequences, no hidden scoring, artifact hashes and DB/export agreement: integrity.json, raw/audit.json and final-audit.json. D/O/R/logical attribution not claimed live; corresponding frozen machinery tests passed. |
| 28 | Full final automated validation: post-validation/validation.json and tests.txt, 248 tests passing without edits. |
| 29 | Formal separated sections, supported/unsupported claims and exact reproduction commands: REPORT.md. SQLite/API backup, searchable Markdown and CSV/JSON data, checksummed complete research export retained here. |
| 30 | Stop after reporting; no next experiment or optimization launched. |

## Scope and limitations

The no-qualification path leaves terminal state `incomplete`; that is intentional
study state, not an infrastructure crash. The two public passes were never scored
privately. Recovery is unobserved, not zero. No formal H-I/H-F interpretation is
available, no repeatability audit ran, and development variants are not independent
evaluation replicates. See REPORT.md for the small residual wall-accounting gap,
intermediate observational readout correction and separate user-requested SSH check.

All frozen implementation/configuration/tests and historical research records
remain unchanged. The only committed additions are this new archival directory.
The archival commit identity is obtained with
`git log -1 --format=%H -- docs/research-records/m08b`; the source and baseline
identities do not change when this archival evidence is committed.

## Artifact checks

`final-audit.json` independently checks the terminal database, all exported tables,
archive entries, benchmark bytes, request/response accounting, per-tier costs,
frozen source identities, preflight chronology and validation receipts.
`checksums.json` binds all other files in this directory, including that audit.
It excludes itself; its identity is supplied by the archival Git commit.
`post-staging-audit.json` repeats the independent checks with immutable backup
access; ephemeral WAL/SHM reader sidecars are not research artifacts.
