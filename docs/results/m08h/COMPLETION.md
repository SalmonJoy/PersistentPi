> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8H Completion and Integrity

Final evidence is identified by annotated tag `m0.8h` (`git rev-parse m0.8h^{}`).
Executed implementation: `e1aaea27899a6d60e2e14bf603b9dbe00b57b753`.
Starting G evidence: `00b51ff4e1b22cbddd84b14f0fab0e152b00c265`, annotated `m0.8g`.
Protocol 0.5. One complete fresh 32-window campaign; no selective reruns.

## Observed Result

| Measure | E1/512 A | E1/1024 B |
|---|---:|---:|
| Verified candidates /16 | 6 | 6 |
| Public PASS / FAIL | 5 / 1 | 5 / 1 |
| Public pass given candidate | 83.33% | 83.33% |
| Terminal truncation + JSON failure | 10 | 10 |
| Historical-subset truncation /8 | 8 | 8 |
| Completed outputs above 512 | 0 | 0 |
| Model calls | 32 | 32 |
| Input tokens | 17,826 | 17,826 |
| Output tokens | 5,786 | 10,906 |
| Total tokens | 23,612 | 28,732 |
| Inference seconds | 136.996 | 248.013 |
| Window wall seconds | 152.342 | 260.283 |
| Calls/candidate | 5.333 | 5.333 |
| Tokens/candidate | 3,935.333 | 4,788.667 |
| Tokens/public pass | 4,722.4 | 5,746.4 |

Paired formation: six both, ten neither, zero arm-exclusive candidates.
The entire historical eight-task subset shifts from 512 to 1024 without formation.
Frozen classification: **ceiling merely moves**; strong and partial criteria fail.
B adds 5,120 tokens (+21.68%), 111.018 inference seconds and 107.941 window wall
seconds, without recovering a candidate or public pass. Marginal cost per recovered
candidate is undefined (zero recoveries), not zero.
All 64 generation token counts are known. Each arm has 16 inspection outputs of 16
tokens, six completed ACT outputs of 56,56,65,73,74,86 tokens, and ten cap-terminated
ACT outputs. Distribution n=32, min=16, median=36, p90 at the arm cap, max at cap.
Full stage counts, conversions and all 16 paired/eight subset rows are in REPORT.md.
The funnel for each arm is 16 ->16 ACT ->6 complete ->6 JSON ->6 authorized ->6
changed ->6 syntax ->6 checkpoints ->6 verifications ->5 PASS/1 FAIL.

## Scope and Reproducibility

Exact 3B Q4_K_M identity/digest, Ollama 0.35.1, tokenizer, template/system hashes,
seed 42, temperature 0, context 4096, think=false and request options are pinned in
model.json/configs.json. The manifest hash is
`8d14874e09e2379d08261dde4a55428b27536fd70849d456ef37fa6f32ab9cd7`.
The freeze hash is `1d2af9d8713ff8ecd998f18518a5dc8409f7bf2c1219c55f0e3e5ea0427aba56`.

Request-parity audit: all 16 pairs' requests differ only in num_predict. All 32 A
requests byte-match G E1. Only eight tasks' full output trajectories byte-match G.
Fresh A therefore does not reproduce G's 8/16 candidates and 7 public passes.
This is observed non-byte-reproducibility despite pinned settings, not evidence of
a diagnosed backend cause. G remains unchanged and valid as its recorded outcome.
All A/B inspection outputs match; every B ACT output starts with the A ACT output.
The paired H comparison, rather than G-vs-H difference, is the treatment evidence.

No hidden correctness, final benchmark performance, generalization, model-size
scaling, universal E0 superiority, final Runner selection or iterative-repair
conclusion follows. The exposed development cohort is not a final evaluation set.

Recommendation only: keep the smaller bounded configuration absent other evidence.
Preregister a development-only diagnostic of nonterminating replacement output and
cross-run reproducibility, using saved traces before authorizing more inference.
Do not automatically raise the cap, change models/sampling, or launch repair.
No follow-up was executed.

## Requirement Evidence

| Objective | Evidence |
|---|---|
| 1 Historical preservation | history.json, audit.json; B/C/D/E/F/G untouched; annotated m0.8g |
| 2 Same exposed16 | tasks.json/manifest.json exactly match G; no fresh tasks |
| 3 Only ceiling treatment | configs.json, request-parity.json; private E1 bindings for both arms |
| 4 Fixed Runner | model.json preflight and raw-results.json post identities match |
| 5 Unchanged budgets | 16000 tokens,15 decisions/tools,120s; reservation/size bounds unchanged |
| 6 Pairing | schedule.json;32 fresh checkpoints, eight AB/eight BA; audit verifies order |
| 7 Historical subset | subset.json/config; eight IDs derived before inference from G evidence |
| 8 Primary outcomes | results.json analysis; ten truncations and six candidates per arm |
| 9 Subset stages | REPORT.md Historical Truncation Subset; generations.csv |
| 10 Public correctness | five PASS/one FAIL per arm; no hidden scoring |
| 11 Full funnel | REPORT.md Funnel; counts and conversion percentages in JSON |
| 12 Every output |64 generation rows; tokens/bytes/JSON/action/backend reason/hash |
| 13 New saturation | ten B1024 hits, zero completed>512; no further cap increase |
| 14 Efficiency | per-window and physical receipts; costs and ratios above/REPORT.md |
| 15 Fixed interpretation | preregistration/config frozen at executed commit; ceiling merely moves |
| 16 Claims bounded | exposed development only; unsupported claims explicitly excluded |
| 17 No repair | candidate_index1/arm I only; accepted candidates terminate; repair_windows0 |
| 18 Sealed cohort | evaluation_runs0, hidden_scores0; no evaluation registry created |
| 19 Validation | pre validation.json/tests.txt and post-validation.json/post-tests.txt |
| 20 Integrity | freeze,64 request replays, receipts, consistent SQLite backups/ZIPs/checksums |
| 21 Delivery | report, raw JSON, CSVs, audits, this document, final evidence tag/reproduction |

Preflight ran 355 tests (328 historical +27 H), with zero errors/failures/skips and
zero live inference. Postflight also passed all 355 tests with zero errors, failures
or skips; its receipt and full logs are retained separately.
Offline audit blocks HTTP transport and new public verification while reconstructing
requests, results, analysis and exports. Physical campaign totals: 64 model calls,
52,344 tokens, 385.009 inference seconds, 422.781 accounted wall seconds; elapsed 424s.
This is below 32 windows/480 calls/512000 tokens/4800s. No warmup, repair, hidden/final
evaluation, Planner, memory/tool generation, other model, sampling or Pi work.


[Private task-level/operational evidence retained in the research repository.]
