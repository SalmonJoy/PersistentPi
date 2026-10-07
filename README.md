# PersistentPi

Researching how much capability fixed small language models can recover through test-time iteration, deterministic orchestration, verification, and automated agent-scaffold optimization.

## Research Question

How much capability can a frozen small coding model recover from a better agent
system around it, rather than from larger or retrained model weights?

The **Runner** inspects code, proposes edits, observes deterministic public test
feedback and retries within a fixed budget. The **Planner** proposes changes to
the Runner's interface and scaffold. A trusted Supervisor and evaluator enforce
permissions, measure outcomes and decide whether changes qualify for promotion.
Neither model may rewrite the evaluator, hidden tests, logger or acceptance rules.

Capability externalization means assigning mechanical work, such as verifying an
accepted edit or expanding a legal configuration, to deterministic software.
Semantic choices remain with the model. Reflection, memory, tools and additional
agents are experimental factors, not assumed improvements.

## Milestones

| Milestone | Main observation |
| --- | --- |
| M0.1 | Deterministic research harness and accounting fixtures |
| M0.2-M0.4 | Initial Runner/tool-interface failures, including repeated reads without edits |
| M0.5-M0.6 | Manual inspection/action/interface investigations unlocked some bounded coding behavior |
| M0.7 | Automatic edit-to-verify orchestration produced 7/8 public and hidden passes versus 0/8 with model-selected verification |
| M0.8 | Harder-task calibration and edit-interface investigations; feedback-driven test-time scaling remains unmeasured |
| M0.9C | 0/8 valid GPT-OSS 120B Planner proposals; no generated scaffold reached Runner evaluation |
| M0.10A | Same-Planner interface feasibility study; F0/F1 frozen, awaiting execution |

M0.7 used the same Qwen2.5-Coder 1.5B Runner. Model calls fell from 120 to 29 and
tokens from 106,330 to 22,487. All successful candidates passed immediately;
budgets 1/3/5 did not establish iterative repair or a test-time scaling law.

M0.8B stopped at its preregistered calibration gate: no difficulty tier qualified.
Subsequent manual scaffold investigations repeatedly moved rather than eliminated
failure modes. M0.8I ended manual serialization tuning; the 3B comparison produced
6/16 candidates with E1 JSON and 0/16 with E2 compact, not a model-size comparison.

Historical M0.9C result remains:

> 0/8 valid GPT-OSS 120B proposals under the preregistered Planner-to-ScaffoldSpec contract; no generated scaffold reached Runner evaluation.

The two manually designed M0.9C references were evaluated separately; their costs
and scores are not scores of a Planner-generated scaffold. The result does not
show that scaffold optimization is impossible.

## Current Status

**M010A_READY_2_ARM**. F0/F1 are admitted for 24 paired synthetic scenarios:
48 future feasibility requests, **zero executed** at this publication boundary.
No Runner calls or scaffold-search evaluation belong to this feasibility study.

The single neutral native-tool probe returned an extra `rationale` argument,
violating the frozen exact-argument contract. F2 was excluded without repair or
retry. A native tool call was observed; this is not evidence that the model lacks
native-tool capability. Readiness is not authorization to execute the study.

## Repository Layout

- `src/persistentpi/`: Runner/Supervisor, verification, telemetry, accounting and experiment management.
- `src/persistentpi/m08/`: iteration/acquisition analysis; private benchmark construction is withheld.
- `src/persistentpi/m09/`: scaffold compiler, disclosure, search and promotion contracts.
- `src/persistentpi/m010/`: interface schemas, mutation compiler, synthetic scenarios, paired analysis and durable receipts.
- `migrations/`: SQLite schema history, without research databases.
- `tests/`: audited public offline interface/accounting/scheduler tests.
- `docs/`: protocols, public scientific report excerpts and disclosure policy.
- `PUBLICATION.json`: safe-file provenance and publication transformations.

## Reproducibility

Python 3.11+; runtime code uses the standard library. From the repository root:

```sh
python -B scripts/validate_public.py
```

This runs only the distributed offline tests with synthetic protocol responses.
It makes no real Planner/Runner requests and executes no benchmark. Runtime
receipts stay in ignored `.local/`. Historical test counts in report excerpts
describe private milestone validation, not tests run by this public command.

The public checkout cannot reproduce protected benchmark results or historical
raw-response parity without the separately retained private evidence. Missing
benchmark constructors fail explicitly with `PrivateAssetUnavailable`; there are
no fake replacements claiming to be the original datasets. Public-copy differences
and excluded regression checks are documented in [Disclosure](docs/PUBLICATION.md).

This is a fresh public snapshot of private source commit `5420476` with independent
Git history. Original research tags were not imported. Cloud identity/provenance
does not establish immutable backend weights or bit-for-bit cloud reproducibility.

## Protected Evaluation Policy

PersistentPi uses held-out and protected evaluation cohorts to reduce adaptive
overfitting and preserve experimental validity. These assets and certain
operational account evidence are intentionally excluded from the public repository.
Public artifacts include protocols, source code, aggregate results, hashes and
non-sensitive reproducibility metadata where disclosure does not compromise future
evaluation. Qualification48, Final96, hidden cases, reference solutions, private
task sources and raw source-bearing traces remain private.

## License

No project license has been selected. Public visibility is not a license grant.
A license requires an explicit project-owner decision.
