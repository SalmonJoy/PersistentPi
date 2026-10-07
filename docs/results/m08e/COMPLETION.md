> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8E Completion Checklist

Executed code/preregistration commit: `8d7f5bd9ce7a94e9c7afa9f88893e9e4e54b11e5`.
Evidence commit is the Git commit containing this archive; no self-referential
commit hash is embedded. Protocol 0.5. Repository was clean before freezing and
before inference. All existing execution files remain unchanged.

| Goal requirement | Saved evidence / result |
|---|---|
| 1. Preserve history | `history.json`, final audit; B/C/D hashes match evidence commits; annotated m0.8d -> 7c9c803 |
| 2. Exposed development tasks | Exact 16 L2 M0.8D E0 snapshots/manifest; 8 families, 16 templates |
| 3. Historical baseline | `reference.json`: 7/16, 0/7 public passes; zero baseline reruns |
| 4. Intended model | `model.json`, `show.json`: qwen2.5-coder:3b, full digest, 3085938688 parameters, Q4_K_M, 1929912626 bytes, Ollama 0.35.1 |
| 5. Scaffold held constant | Historical E0 acquire/Window reused; all 16 initial messages and template/system/tokenizer hashes match |
| 6. Decoding | Temperature 0, seed 42, context 4096, output 512, think=false; every request replayed |
| 7. Acquisition | 16 fresh I/1 windows; first public verification ends each formed window; no repair or rerun |
| 8. Budgets | Original limits/reservation unchanged; all window/campaign ceilings audited; no timeout or loading failure |
| 9. Primary formation metric | 8/16 vs 7/16; +1 task, +6.25 percentage points |
| 10. Funnel | All 16 READ -> ACT -> EDIT -> valid/authorized; 8 change/checkpoint/verify; 0 PASS, 8 FAIL |
| 11. Unchanged metric | 62/106 (58.49%) vs historical 118/125 (94.40%); 90 repeated proposals; exact raw rejection counts |
| 12. Family/template | 5 formation families; complete paired rows/CSV; 5 new, 4 lost, 3 both, 4 neither |
| 13. Public correctness | Secondary only: 0/8 PASS, 8 FAIL; no repair or hidden feedback |
| 14. Threshold | All strong-signal criteria missed; small intermediate descriptive gain, no confirmatory claims |
| 15. Optional 7B | Not locally installed at preflight; feasibility untested; no download/inference; authorization required |
| 16. Sealed assets | No evaluation/hidden loader; SQL/audit: zero evaluation, hidden scoring, retirement or repair |
| 17. Validation | 300/300 pre-run and 300/300 post-run, including 12 new fake-model tests; full logs saved |
| 18. Final report | `REPORT.md`, `INTERPRETATION.md`, SQLite backup, export, freeze/config/identity/receipt artifacts and reproduction commands |

`audit.json` independently replays all 122 requests and reconciles 126320 tokens,
130 tool calls, 350.738 inference seconds and 498.312 receipt-based physical wall
seconds. Execution elapsed was 500.062 seconds. No budget was enlarged.

Read-only reproduction of the evidence checks:


[Source-bearing example or private reproduction procedure withheld.]


The live reproduction command is in `REPORT.md` and incurs new expenditure;
it is not launched here. All raw live outcomes are preserved. The report funnel
was reordered only for presentation. Offline annotations do not alter the
frozen analysis or historical results. Post-run validation is under
`post-validation/`; preflight validation remains at archive root.

This milestone does not select a replacement Runner, demonstrate iterative
repair/test-time scaling, establish hidden generalization or isolate parameter
count causally. No sampling, 7B, repair scaling, final evaluation, Planner, Pi
work or benchmark/scaffold modification follows. Stop after M0.8E.
