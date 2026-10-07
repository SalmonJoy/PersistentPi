> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.9C Primary Search: No Finalist

Protocol: `0.6`. Campaign: `253eff62-13fd-476f-9b6f-918b97c16abe`.

Terminal: `SEARCH_COMPLETE_NO_FINALIST`; phase: `finished`;
reason: `no_generated_full_scaffold`. Proposal access is permanently closed.

The preregistered bounded GPT-OSS 120B Planner search did not discover a
scaffold meeting the Search32 qualification-entry threshold.

All eight proposal slots were consumed. All eight proposals were invalid.
There were no valid generated scaffolds, no Screen8 executions, no Remaining24
executions, no generated full-search archive entries, and no finalist.
This is not evidence that automated scaffold optimization is generally
ineffective. No Planner-generated scaffold reached live Runner evaluation,
so this campaign does not measure the performance of a valid optimized scaffold.
No claim of qualification, unseen-task improvement, or generalization is made.


[Private task-level/operational evidence retained in the research repository.]

## Fresh References

Both references were freshly executed on the identical frozen Search32 cohort.

| Reference | Public passes / 32 | Passing families / 8 | Formations / 32 | Formation families / 8 | Runner calls | Runner tokens | Inference seconds | Task wall seconds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0, E0 JSON | 0 | 0 | 14 | 4 | 286 | 297,447 | 459.247 | 522.124 |
| B1, E1 JSON | 2 | 2 | 12 | 4 | 331 | 290,460 | 327.981 | 394.340 |

B0 scaffold ID:
`3523ba5db8fee37ed9465947970b20ef61a336ee08527c3c9abdf9cda2cf8413`.

B1 scaffold ID:
`816fe91c71baad3187fa4168f2d5f450c512a14477843d642f0d435992476640`.

B0 consumed 265,361 input and 32,086 output tokens. B1 consumed 268,650
input and 21,810 output tokens. All 26 formed candidates were verified
automatically: 24 public failures and two public passes.


[Private task-level/operational evidence retained in the research repository.]

## Archive And Gate

The only full archive entries are fresh B0 and B1. Each contains exactly
32 distinct physical task receipts on the same cohort, with full scores
reconstructed from the eight designated screening-task outcomes plus the
24 remaining-task outcomes. References were executed as references, not
as generated-scaffold screening jobs.

There are **zero fully evaluated generated scaffolds**: generated scaffold
rank, complexity, Screen8/Remaining24/Search32 scores, family coverage and
Runner costs are therefore unavailable, not zero-valued measurements.
The header-only `generated-archive.csv` and empty JSON array record this.
All four round-winner decisions are null and were reconstructed successfully.

| Final generated candidate / gate field | Result |
|---|---|
| Finalist scaffold ID | None |
| Generated candidate public passes / 32 | Not evaluated |
| B0 public passes / 32 | 0 |
| B1 public passes / 32 | 2 |
| Delta vs B0 / B1 | Not measurable |
| Generated passing families | Not evaluated |
| +4 vs B0 gate | Not evaluated: no eligible candidate |
| +4 vs B1 gate | Not evaluated: no eligible candidate |
| >=4 families gate | Not evaluated: no eligible candidate |
| Numerical qualification-entry gate | Not computed |
| Qualification entry authorization | Not obtained; no finalist |

The scheduler's preregistered no-generated-full-scaffold exit was taken.
It would be misleading to invent a scored zero-pass generated scaffold or
three numerical gate FAILs. The overall search found no eligible scaffold.
Generated Screen8 physical reuse was not exercised; its invariant remains
covered by frozen offline validation, rather than claimed as live evidence.

## Costs

| Quantity | Research campaign value |
|---|---:|
| Planner requests | 8 / 8 |
| Planner prompt_eval_count | 16,441 |
| Planner eval_count | 29,823 |
| Planner provider_accounted_tokens | 46,264 / 200,000 |
| Cached prompt tokens, recorded separately | 4,704 |
| Planner request latency total | 106.923 seconds |
| Included-credit charge observed in provider request rows | US$0.01976 at UI display precision |
| Charge calculated from provider counts and frozen published rates | US$0.019720206 |
| Runner calls | 617 |
| Runner input / output tokens | 534,011 / 53,896 |
| Runner total tokens | 587,907 |
| Physical task windows | 64 |
| Runner inference seconds | 787.228 |
| Sum of Runner task wall seconds | 916.464 |
| Active campaign wall seconds | 1,061.157 (17.686 minutes) |

`provider_accounted_tokens = prompt_eval_count + eval_count`.
Cached tokens are not added again. Thinking bytes are provenance, not an
estimated extra token charge. The historical 127-token operational admission
probe is excluded from all research totals. Post-run offline validation cost
is also separate from campaign cost.

[Private account observation retained privately.]

## Integrity And Validation

- Frozen Runner: Qwen2.5-Coder 1.5B Q4_K_M; digest
  `d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668`;
  Ollama `0.35.1`; temperature 0, seed 42, context 4096, output 512,
  thinking false. All 617 recorded requests/responses were reconciled.
- Planner alias `gpt-oss:120b-cloud` mapped to API/catalog `gpt-oss:120b`
  at `https://ollama.com/api/chat`, temperature 0, thinking high,
  output allowance 4096. Seed support remained unestablished; no seed was
  silently introduced. All eight returned model identities and saved identity
  records agree with admission. Catalog/metadata identity checks ran before
  requests. Observed digest `d98fe6ba01e6` is provenance, not proof of immutable
  backend weights or bit-for-bit cloud reproducibility.
- Exact disclosure projection was independently reconstructed from original
  search protocol events for all eight requests, including sanitized excerpts
  and prior invalid-proposal counts. No task source/test bodies, expected
  answers, benchmark specifications or hidden outcomes entered requests.
- All eight requests and 72 completed operations reconcile; there are no
  unresolved, reserved, indeterminate or resent operations. Resource caps
  stayed unchanged and were not exceeded.
- Qualification48 executions: **0**. Final96 executions: **0**. Hidden
  evaluations: **0**. Qualification identity metadata alone was permitted;
  qualification task contents, Final96 and hidden contents were not loaded.
- SQLite backup API produced a consistent backup with `integrity_check=ok`.
  A fresh post-run export is byte-identical to the automatic terminal export.
  Replay passed, reconstructed both full archive entries, all proposals,
  physical costs/disclosures and null round winners, and found no finalist.
- Fresh regression: **643 passed, one error, 644 tests executed**. The frozen
  aggregate validation command exited 1 after its first 479-test batch
  (478 passed, one error). The error was
  `test_storage.StorageTests.test_export_reconstructs_all_tables_and_artifacts`,
  at `tests/test_storage.py:148`: `_csv.Error: field larger than field limit
  (131072)`. No code, test, CSV reader limit, or result was changed to clear it.
  The original failure/log is preserved. The remaining 165 unchanged frozen
  checks were executed separately and passed: operational 8, admission
  amendment 55, Pro amendment 37, launcher 46, evidence 19. Six additional
  synthetic campaign scenarios and their export/replays completed. Their
  fixtures are not real qualification/final tasks. **Post-run regression
  certification is not clean**; the earlier L2 644-pass receipt is historical,
  not substituted for this fresh result.
- Frozen sources, admission linkage, historical evidence and launcher freeze
  remain unchanged. Original M0.9C admission-stop and subsequent historical
  records are not rewritten.

Metadata limitation: legacy per-run `git_commit` is null and `platform_json`
is empty in the frozen executor. This is disclosed, not repaired in the data.
The campaign's starting-state receipt, launcher freeze, anchored admission,
configuration and frozen model/tokenizer identity provide independent linkage
to the exact execution baseline. Cloud catalog snapshots are checked by the
frozen adapter; saved identity records and response IDs do not prove backend
weight immutability.


[Private task-level/operational evidence retained in the research repository.]
