# M0.8G: 3B E0 vs E1 Mechanism Test

Protocol 0.5. Development diagnostic only, not Runner selection or repair scaling.
Starting evidence: clean `5843da7`, tagged `m0.8f`. B/C/D/E/F evidence remains immutable.

## Questions and Frozen Conditions

Primary: does removing exact-old matching rescue changed mechanically blocked edits?
Secondary: is formation improvement broader than the two known context-mismatch tasks?
Use the exact 16 exposed L2 public/development tasks from M0.8E, unchanged.
They are diagnostic development data, not independent performance evidence.
The subset is fixed from F: `pf1c6ba1a368d939c` and `p952bd0ab55e4f241`
(`parsing/1`, `parsing/4`). Do not select any new favorable subset.

A uses historical E0 path/old/new. B uses the existing M0.8D E1 path/content
whole-file replacement. E1 checks replacement against current source and rejects
unchanged content. Historical generic rejection projection only, never precise
M0.8C no-op feedback. The edit contract is the whole treatment: prompt/schema
wording, output burden and E1 prewrite checkpoint are inherent confounds, not
separately identified effects. No semantic assistance or generated diagnosis.

Freeze exact M0.8E `qwen2.5-coder:3b` identity and tokenizer. Digest:
`f72c60cabf6237b07f6e632b2c48d533cef25eda2efbd34bed21c5e9c01e6225`.
Q4_K_M; Ollama 0.35.1; temperature 0; seed 42; context 4096; output 512;
think=false; keep_alive=5m; request timeout 30s. Template/system/tokenizer hashes,
stored bytes and full discover identity must match E. Mismatch blocks execution;
do not download/reconfigure models. No warmup inference.

## Execution and Limits

One fresh A and one fresh B window per task, same original checkpoint. Sort by
template and alternate AB/BA starting AB: eight pairs each order, 32 windows.
Freeze and checksum schedule before any inference; never rerun selectively.
Reuse existing PrimitiveCampaign.acquire, Window/PrimitiveWindow, model/controller,
Supervisor, verifier, restrictions, public tests, prompts and context policy.
INSPECT offers source read; successful read deterministically transitions to ACT.
No mechanical VERIFY decision is delegated to the model.

Each window: 15 model decisions, 15 tools, 16000 measured tokens, 120 seconds;
one-tool/5-second verification reservation. Output bytes 4096; edit bytes 8192;
workspace bytes 10485760; test timeout 5s. All are historical values, unchanged.
Campaign: 32 windows, 480 calls, 512000 tokens, 4800 seconds including control
and finalization. No budget increases, sampling, memory, Planner, teacher or Pi work.
Stop at first verified candidate (PASS or FAIL), GIVE_UP, malformed response,
budget termination, STOP or infrastructure failure. Failed public tests never
[Source-bearing example withheld.]
no restart/resume or automatic follow-up. STOP file at campaign state root works
within acquisition. Timeouts and cancellation remain existing supervisor behavior.

## Outcomes and Analysis (Fixed Before Inference)

Primary formation means one accepted state-changing edit, checkpoint and automatic
public PASS/FAIL under a finished window. No-op/rejected edits are not candidates.
Report 16 paired rows, A-only/B-only/both/neither and public transitions for both.
Report known-subset E1 formation and fresh A/B rescue separately: historical E0
rejection plus E1 formation alone is weaker than fresh paired rescue.

Report task and proposal funnels with absolute counts and adjacent conversions:
tasks -> inspected -> EDIT -> valid/authorized -> changed -> mechanically
applicable -> accepted state change -> checkpoint -> public verification -> PASS/FAIL.
Proposal syntax/schema validity is not post-application Python validity. Historical
applicability is observed acceptance; static applicability and unreachable checks
are separately labeled, never assumed to have executed. Proposal inspection means
prior complete successful source read, not a new inspection per proposal.

E0 partition: unchanged, changed correct-old, changed incorrect-old/context mismatch,
syntax rejection, other rejection, accepted. E0 exact matching is a unique nonempty
substring, not a full-file-only restriction. E1 partition: identical-current,
changed replacement, syntax/other rejection, accepted. Report raw errors as well.
Report changed/unchanged fractions of all EDIT proposals; syntax rate of all EDITs
and changed EDITs; context mismatch rates; repeated proposals; decisions/tokens
through first changed proposal (including rejected changes, null means censored);
normalized accepted candidate AST count, calls/tokens/inference/wall per formation.
Include failed windows in costs. Report input/output tokens separately. Inference
and verification are components of wall, not additive wall expenditure. Receipt
costs and per-window costs are separate; allocate shared overhead equally by arm.

Mechanism confirmed only if: at least one known-subset task forms in B but not A;
context-failure tasks decrease; total net formations >0; and B has no increase in
tasks ending without formation after changed mechanical rejections. This is a
prespecified conservative meaning of no offsetting failure mode. Raw subset rescue
and every A-only task remain reported even when this rule fails.
Broader E1 benefit requires mechanism confirmed AND >=4 net formations.
Narrow-only benefit requires mechanism confirmed AND <4 net formations.
If subset rescue occurs with offsetting losses/new failures, label mixed/offset,
not confirmation. If no rescue but formations improve, label non-subset behavioral
signal, not exact-old mechanism confirmation. Otherwise no observed benefit.
Incomplete execution is not a negative model result. No 13/16 progression gate.
No conventional hypothesis test, population claim or equivalence conclusion.

Public correctness is secondary. More candidates with zero public passes means
mechanical formation improved without evidence of semantic coding improvement.
Development correctness is not hidden generalization; no repair effect measured.
Recommend 7B control if benefit absent/narrow and candidates still semantically fail;
consider E1 for later development only on broad benefit, never adopt here. Mixed
offsetting failures select Planner/stop (stop manual tuning, not automatic Planner
execution). Incomplete execution selects stop/review, not a model judgment. Zero
formations select stop/review. Otherwise, absent/narrow/unconfirmed benefit selects
a separately authorized 7B same-scaffold development capability control; any
public passes qualify the rationale, not the selection or a model promotion.
Stochastic 1.5B requires specific evidence beyond diversity and is not the default.
Recommend one next experiment or an explicit stop; execute none.

## Validation, Freeze and Integrity

Before inference run all historical tests plus isolated mock G tests: inherited
E0/E1 parity, exact identities, budget/reservation, schedule/pairing/checkpoint,
generic rejection, public-only/no-repair/no-repeat, subset derivation, funnel,
cost reconciliation and classification boundaries. G never loads the frozen
evaluation or hidden assets. Historical unit tests may exercise synthetic private
scoring/boundary fixtures; those are not the sealed M0.8 evaluation cohort and
incur no live model inference. G mock acquisitions use only synthetic development
fixtures and public verification.
Freeze implementation commit/files, full identity, tokenizer, task manifest,
subset provenance, schedule, configs, prompts, contracts, budgets, analysis rules,
test receipts and historical checksums. Preflight/freeze makes metadata requests
only (version/tags/show/ps); no chat/pull endpoint. Historical frozen source files
must be byte-identical. New G code is isolated under scripts, not the scaffold.

After execution replay every request and controller state read-only, validate
receipts, ordering, task pairing, exact original checkpoint, edit semantics,
single automatic verification and costs; compare SQLite backup against research
ZIP tables and all artifact hashes. Reject any hidden/evaluation/repair records.
Check final identity and ceilings. Archive consistent SQLite backup-API exports,
both public research ZIPs, raw/derived results, proposal/paired CSVs, report,
tests, checksums and requirement-by-requirement completion audit. Final commit
records evidence; executed commit remains distinct. Offline audit is the default
reproduction check. Live reproduction requires explicit new authorization and
clean executed commit; exact byte-identical generation is not promised.

The 96 evaluation tasks and hidden tests remain sealed. Do not inspect contents,
score, retire the cohort, mutate benchmark definitions or start another experiment.
M0.8B remains a valid calibration stop; this study cannot retroactively qualify it.
