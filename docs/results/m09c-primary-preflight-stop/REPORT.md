> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.9C Primary Search Preflight Stop

**Outcome A: integrity stop before research inference.** The requested primary
search was not launched. This is not a completed four-round campaign and is not
a negative Planner/scaffold-optimization result. The research hypothesis remains
untested. M0.9C-R2's operational admission remains valid historical evidence.

Parent commit: `0ceb6ea3c2c297943423a2282c4872ef557c12f0`. Protocol: `0.6`.
Attempt: `m09c-primary-32f086da-6fdc-4875-9085-e75e38be741e`.
No scientific code, model, benchmark, prompt, search space, threshold, resource
ceiling or historical artifact was modified. Evidence is additive only.

## Mandatory Launch Gate Failure

The current implementation has no admitted live, search-only execution path:

- `SearchManager` rejects live Planner/evaluator adapters before initialization.
- `CandidateExecutor` rejects a live Runner backend before its first model call.
- The frozen research renderer still emits `model: glm-5.3`; the existing cloud
  mapper does not replace that with the admitted `gpt-oss:120b` API identifier.
- The admitted native transport deliberately accepts only the already-consumed
  neutral probe, not research proposal requests.
- `SearchManager.run()` automatically executes qualification after a passing
  entry gate. No search-only authorization barrier/launcher is present.

These findings were reproduced with offline fixtures and network-blocking stubs,
not live model requests. See `launch-path-audit.json`. Marking real adapters
`offline=True`, monkey-patching the trusted loop, changing the frozen model field,
or invoking the neutral probe again would not satisfy the required execution
contract. None was done. The objective's mandatory preflight-stop rule applied.

The missing operational transport binding and search-only launch barrier need
separate implementation, parity/security validation and an explicit execution
freeze before a future authorized search. They must preserve scientific semantics;
this report does not authorize changing them or restarting this closed attempt.

## Verified And Deferred Gates

Initial HEAD was exactly the admitted parent, with a clean worktree. All 102
M0.9B-frozen code files and the M0.9C-R2 source/configuration freeze verified.
Search32, Screen8 and Remaining24 matched their frozen manifests and formed the
exact disjoint 8/24 partition. Qualification provenance was checked through
unchanged clean-tree Git object identities, without loading qualification cases.
Final96 and hidden assets were not read or executed.

The installed Runner matched the frozen 1.5B identity, digest, Q4_K_M,
Ollama 0.35.1, template/system hashes, explicit non-thinking policy and tokenizer.
Only non-generating local discovery/tokenizer inspection occurred.

Current cloud account allowance and identity were **not** revalidated after the
mandatory launch-path stop. The saved ADMITTED account/model observations are
historical evidence, not a claim about their current external state. No cloud
API request or new admission probe was sent. No credential was transmitted.

## Requested Search Results

Fresh B0: **not executed**, zero task receipts; score unavailable.
Fresh B1: **not executed**, zero task receipts; score unavailable.
No historical reference scores were substituted.

| Round | Slot 1 | Slot 2 |
|---|---|---|
| 1 | Not executed | Not executed |
| 2 | Not executed | Not executed |
| 3 | Not executed | Not executed |
| 4 | Not executed | Not executed |

All eight slot records in `result.json` have no parent, mutation, scaffold,
Screen8 result or validation outcome because no proposal was requested. None was
consumed. No candidate was screened/promoted, no Remaining24 execution occurred,
and the complete-search archive is empty. There is no best generated scaffold or
finalist. The +4/+4 and four-family entry gate is **NOT APPLIED**, not FAIL.
No finalist freeze for M0.9D exists and no runner-up substitution was attempted.

## Cost And Integrity

Research Planner: **0 requests / 0 provider-accounted tokens / $0 usage**.
Research Runner: **0 calls / 0 tokens / 0 windows**.
Active campaign time: **0 seconds**; no optimization campaign was created.
Preflight/testing time is not represented as campaign inference time.

[Private account observation retained privately.]

The qualification reservation remains intact: 144 windows, 2,160 Runner calls and
2,304,000 Runner tokens. Qualification48 execution, Final96 execution and hidden
scoring remain **zero**. All historical campaigns/tags/artifacts are unchanged.

**579 tests passed in each full-suite run**, before and after the stop, with zero
failures/errors. Receipts and logs are stored under `pre-validation` and
`post-validation`. They use the existing synthetic-fixture/real-cohort-denial
harness, without editing historical tests. `completion-audit.json` records the
actual pass counts, source identities, secret exclusion and export/replay checks.
No research-outcome test accommodation was made.

`preflight.sqlite` is an operational evidence ledger, not an optimization database.
Its consistent SQLite backup and the sanitized export retain the stop receipts,
zero resource accounting and slot inventory. Offline replay reconstructs the stop
and empty schedule/archive; proposal validation, rankings, FullSearchScores and
entry-gate application are explicitly not applicable. It does not fabricate those
results or invoke a cohort loader/hidden evaluator.
Database and backup replay agree; eight in-memory negative fixtures rejected
fabricated calls, scores, proposal states, gate/finalist/archive data and unsafe
access flags. The export is `../m09c-primary-preflight-stop-export.zip`, with an
external checksum receipt alongside it. Credential exclusion checks cover public
files, databases and uncompressed export members; no secret is persisted.

## Interpretation And Stop

This attempt establishes a reproducible preflight integration failure while
preserving budgets and protected assets. It establishes **nothing** about whether
GPT-OSS can improve the frozen Runner, whether any scaffold meets the search
threshold, or whether an improvement generalizes. No search-outcome conclusion
can be drawn from an empty research ledger.

The stop is complete; this attempt will not be resumed or used to expand another
campaign's budgets. Live search and all later qualification/final work remain
subject to separate validated authorization.


[Source-bearing example or private reproduction procedure withheld.]


Evidence tag: `m0.9c-primary-preflight-stop`, distinct from historical `m0.9c`.
