> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8D Completion Audit

## Outcome

**E1 does not advance. Retain E0.** All 32 preregistered live development
acquisition windows completed once. E0 formed 7/16 candidates; E1 formed 6/16.
Paired outcomes: zero E1 wins, one E0 win, six both formed, nine neither.
Observed formation difference: -6.25 percentage points; exploratory paired
family-stratified template bootstrap 95% interval [-12.5pp, 0pp]. No p-value.
Failure of the engineering gate does not establish equivalence or a universal
model limitation. The primary contrast is formation, not secondary correctness.

| Gate requirement | Observed E1 | Result |
|---|---:|---|
| >=13/16 formations | 6/16 | Fail |
| >=4 net extra formations | -1 | Fail |
| >=6 formation families | 4 | Fail |
| >=8 public failures | 5 | Fail |

E0 public PASS/FAIL: 0/7. E1: 1/5. Hidden outcomes are **unknown**, not zero.
The one E1 public pass does not justify promotion under the frozen formation gate.
All 13 accepted candidates changed bytes and AST. All nine E0 and ten E1
nonforming windows only repeated unchanged edits. Removing old-content generation
did not resolve the dominant acquisition behavior. This points toward model/action
policy limitations rather than patch matching, but does not isolate their causes.

| Metric | E0 | E1 |
|---|---:|---:|
| Changed-edit / formation rate | 43.75% | 37.50% |
| Edit proposals | 125 | 147 |
[Source-bearing example withheld.]
| No-op proposal rate | 94.40% | 95.92% |
| Model calls | 141 | 163 |
| Input+output tokens | 146,177 | 142,616 |
| Calls per formation, including failures | 20.143 | 27.167 |
| Tokens per formation, including failures | 20,882.429 | 23,769.333 |
| Inference seconds | 221.721 | 158.915 |
| Physical wall seconds, allocated overhead included | 332.092 | 280.565 |

The contract reduces output volume and inference time, but produces more calls
and worse tokens/calls per formed candidate. Lower aggregate token use alone is
not acquisition improvement. Representation and input/output burden are one
complete tool-contract treatment, not independently identified causal factors.

Total study: 304 model calls, 317 tool calls, 288,793 tokens, 380.635 inference
seconds, 612.657 recorded physical wall seconds; elapsed including final
exports/audit/report tail 616.891 seconds (10.282 minutes). Maximum per-window
wall: E0 36.812s, E1 32.313s, below 120s. Maximum generation output: E0 156,
E1 86 tokens, below 512. No infrastructure interruption, selective rerun,
aggregation correction, Planner, hidden scoring, repair loop, or Pi work.

## Requirement Evidence

The executed implementation commit is
`bd72bff5f8278cde60d7742022122049121affa0`. This commit precedes the archive
commit; the final evidence commit is reported by Git history and the close-out.
The frozen implementation is unchanged after inference.

| Objective item | Authoritative evidence and verification |
|---|---|
| 0. Preserve B/C; annotated C tag; prior tests | `history.json`; all B/C archival checksums and evidence-commit blobs rechecked; `m0.8b-calibration-stop` -> 038c370, annotated `m0.8c` -> cb08346; prior 271 tests remain included in 288-test validation |
| 1. Other development instances | `manifest.json`, `tasks.json`, provenance; 16 L2 development tasks, 16 templates/eight families, no overlap with C's 16 selected IDs; all already B-calibrated, not C-live-exposed |
| 2. Paired E0/E1 contracts | `configs.json`, `contracts.json`; only model.edit_primitive differs; all raw actions and request schemas replayed; no E0 action executed in B |
| 3. Supervisor-mediated replacement | Existing unchanged `supervisor.py`; new boundary fixtures cover confinement, protected path, text/NUL, size, no-op, state change and checkpoints; archived accepted content exactly matches proposed content |
| 4. Equivalent rejection information | Frozen projection in `contracts.json`, `m08d-preregistered.json`, `primitive_runtime.py`; 461 transported E1 history fields replayed with generic error; raw E1 errors retained; zero precise C feedback |
| 5. Fixed model, runtime, scaffold and budgets | `model.json`, `configs.json`, `freeze.json`; same digest/quantization/runtime/template/system/tokenizer as C; pre/post identity identical; all options/requests replayed; C3 and automatic verifier unchanged |
| 6. Prompt fairness and hashes | `initial-prompts.json`; E0 prompt byte-identical fixture; initial task user message equal; system differs only in contract example/size sentence; per-call hashes, actual token counts and schemas in exports |
| 7. Fresh pairing and order | Frozen `schedule.json` hash; all 32 start events reconstructed in AB/BA template order; source/public starting checkpoint identities match for each pair |
| 8. Bounds | Per-window receipts/usage and campaign ledger checked: <=15 decisions/tools, <=16000 tokens, <=120s; 32 windows; total <=480 calls, <=512000 tokens, <=4800s; conservative admission and verifier reservation preserved |
| 9. Primary formation semantics | 13 accepted byte-changing edits -> 13 candidate checkpoints -> 13 automatic public verifications; no no-op accepted; only one candidate per window |
| 10. Fixed ALL progression gate | Frozen `gate` config and analysis; independent reconstruction agrees; every criterion fails; no post-outcome threshold changes |
| 11. Behavioral funnels | `results.json`/`REPORT.md` and `paired.csv`; every arm: 16 inspected, generated, valid, authorized; state changes/checkpoints/verification 7 versus 6; parallel PASS/FAIL counts and adjacent rates |
| 12. Metrics | `paired.csv`, per-window diagnostics and arm aggregate results: first changed decisions/tokens/preceding no-ops (null if absent), rates, edits, rejections, repeats, uniqueness, costs and public outcomes |
[Source-bearing example withheld.]
| 14. No repair loops | Windows have arm I, index 1, no parent; one or zero candidates; immediate termination after verification; branches table empty; methods reject repair and repeated task acquisition |
| 15. Hidden isolation | Public-only input whitelist and SQLite triggers; zero hidden evaluations/scores, zero formal evaluation runs, no suite task loader; opaque checksum of benchmark ZIP only |
| 16. Automated tests | `validation.json`/`tests.txt`: 288 passing tests before inference, 17 new targeted fixtures; `mock-validation.json`: 32 synthetic windows, 96 fake calls, no real inference/tasks, positive-gate/archive/replay fixture; post receipts stored separately |
| 17. Interpretation | Fixed four outcome cases in preregistration; negative formation outcome, retained E0, generic acquisition behavior unresolved; no equivalence, repair or final-generalization claim |
| 18. Final cohort sealed | Only whitelisted development IDs in every run; zero evaluation/scoring/retirement records; original frozen benchmark archive checksum unchanged; no final-tier or final-evaluation decision |
| 19. Freeze and post-audit | All code/config/input hashes and commit frozen before started.json; 304 requests replayed, SQLite integrity/FKs, all DB/export tables and artifact hashes checked; supplemental audit reconciles all nine COSTS fields and 653 unique receipts; raw outcomes/analysis unchanged |
| 20. Required report and stop | `REPORT.md`, this audit, paired data, frozen identities, consistent SQLite backups, exports, test/audit receipts, checksums and read-only/fresh-reproduction commands; no follow-up launched |

This audit was written after outcomes solely to verify compliance with the frozen
protocol, not to choose analyses, alter outcomes, or change progression rules.
The supplemental auditor adds integrity checks only; it does not change the
frozen Runner, analysis or model windows. Raw results, arm analyses and pairing
are unchanged. SQLite backups were created using the backup API, not raw copies
of an active WAL database. The read-only archive audit requires no model server.


[Private task-level/operational evidence retained in the research repository.]
