> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8C Completion and Integrity

The development-only pilot finished all 32 preregistered windows. Precise no-op
feedback failed its progression gate. It formed fewer candidates and consumed
more inference than the baseline on these exposed L2 development tasks.

| Measurement | A: baseline | B: precise no-op feedback |
|---|---:|---:|
| Verified candidate formation | 7/16 (43.75%) | 6/16 (37.50%) |
| Public pass / fail | 0 / 7 | 0 / 6 |
| Families with formations | 4 | 4 |
| AST-changing candidates | 7 | 6 |
| No-op proposals / repeated no-ops | 124 / 112 | 133 / 121 |
| Post-rejection byte/AST change | 3/115 (2.61%) | 2/123 (1.63%) |
| Model calls | 147 | 155 |
| Input / output tokens | 136,855 / 16,625 | 147,164 / 17,873 |
| Total tokens | 153,480 | 165,037 |
| Inference seconds | 236.725 | 254.129 |
| Recorded wall seconds, including preparation | 351.265 | 371.610 |
| Tokens per verified candidate | 21,925.71 | 27,506.17 |

Paired results: zero B wins, one A win, six formation ties and nine nonformation
ties. The paired effect is -6.25 percentage points; the exploratory,
family-stratified template-bootstrap interval is [-12.5, 0] percentage points.
This is descriptive development evidence, without a confirmatory p-value.

All four gate checks failed: B formations 6 < 13; net formations -1 < 4;
B formation families 4 < 6; B verified public failures 6 < 8. No confirmation
is authorized by this result. It does not establish equivalence, final benchmark
performance, feedback-driven repair, test-time scaling or hidden generalization.
A separately designed E0/E1 development experiment may be considered later.

Execution used the exact M0.8B Runner: qwen2.5-coder:1.5b, Q4_K_M, Ollama 0.35.1,
digest `d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668`,
temperature 0, seed 42, context 4096 and output ceiling 512. Model/template/system
identities, original model/window configurations, prompt/scaffold hashes and
feedback strings are archived in `model.json`, `configs.json` and `freeze.json`.

Executed implementation commit: `a59adbeae1eb4ea96210b90569dfa02c14f09d75`.
Freeze SHA-256: `eee725692c9971db3cfbae55e2ce36e76e86224462302d0f833059993083fefe`.
Manifest hash: `ac1c980449c209a4a13ed982b44d473439ad1b12f8b3426352e19686b1c7761a`.
Schedule entry hash: `a273ab818eb8497cc8147207972c51b6376db4cb3ffebe5abfa46a89761f49b4`.
Exact file hashes, all 16 selected task identities and the 32-entry A/B schedule
are in the freeze, manifest and schedule artifacts. Final evidence commit:
`git log -1 --format=%H -- docs/research-records/m08c`.

Validation: 269 tests passed before inference; 271 passed after the accounting
fix, including the two added regressions. Both runs had zero failures, errors or
skips. The 23 focused pilot tests cover projection, pairing, budgets,
authorization/isolation, reservation, automatic verification, gate, diagnostics,
STOP/infrastructure handling, shared accounting and denial of live inference
through historical-audit validation.

The independent audit replayed all 302 requests and verified matching database
and export snapshots, checksums, original checkpoints, order, budgets, model
settings, diagnostics and gate. Actual initial and first-edit request payloads
were identical between A/B for every selected task. Pilot inference used exactly
the selected 16 tasks; the other development instances received no pilot calls.
There were zero evaluation runs, hidden scores, repair windows or reruns.

Total verified expenditure: 302 calls, 318,517 tokens and 490.854 inference
seconds. Recorded physical wall cost was 722.875 seconds; execution elapsed,
including additional control-plane overhead, was 735.922 seconds (12.27 minutes).
All 32 per-window limits and aggregate campaign ceilings were satisfied.

## Recorded Accounting Defect

The executed aggregate counter passed a generator to a multi-field summation.
The first sum exhausted it, so the original overall summary retained 13
candidates but zeroed its other fields. This also impaired the aggregate live
token/call counter. Independent per-window limits and the 32-window limit still
bound this exact pilot to 480 calls and 512,000 tokens. Measured expenditure was
below those ceilings; the independent live elapsed-clock wall ceiling operated.

`raw-results.json` preserves the original live result byte-for-byte. Corrected
physical totals in `results.json` were reconstructed from immutable receipts and
overhead records. Every primary outcome, diagnostic, condition total, model
identity, schedule record, bootstrap and gate matches the original artifact.
The ledger fix occurred after inference; no trajectories were repeated. The
read-only historical audit validates the executed commit and confirms unchanged
treatment and analysis code. Historical validation cannot authorize live runs.

M0.8B at `038c370ce410c07b93e07cfba1cc93467dd1fac4` remains byte-for-byte intact
with the annotated tag `m0.8b-calibration-stop`. Its result remains: no difficulty
tier qualified. The frozen evaluation cohort remains unused.

`REPORT.md` and `paired.csv` contain the full paired table, first changed-edit
decisions/tokens/no-op counts, family breakdown and costs. JSON, public-only raw
exports, consistent SQLite backups, validation logs, audit receipts and all
checksums are stored alongside this file. Read-only verification and deliberate
fresh reproduction commands are provided in `REPORT.md`. No subsequent
confirmation, evaluation, E1, Planner or Raspberry Pi work was performed.
