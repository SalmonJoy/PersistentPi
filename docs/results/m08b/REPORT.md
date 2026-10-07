> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8B: Live Calibration and Final Evaluation

Date: 2026-10-05. Protocol: **0.5**.

**Outcome: incomplete study; no qualifying development tier.** All 96 frozen
initial development acquisitions completed. The preregistered calibration gate
stopped the study before continuation calibration, reproducibility repetitions,
forecasting or final evaluation. This is a preserved negative calibration result,
not a negative test-time-scaling result.

## Experimental integrity

- Clean starting/archive baseline: `75c2e5c3a99a24ac285f41fe55d2dff5a555bf67`.
- Annotated tag `m0.8a` points to that baseline.
- Frozen implementation source commit recorded by the manager:
  `3ca52e4b1abbea65e28a0f06f329cafb46f66e77`.
- Historical `m0.7` and its records were preserved. Only new M0.8B archival
  records and operational reporting helpers were added after generation.
- Campaign: `122dcd2a-580b-4c30-84be-891ec1e48bd6`; phase `calibration`;
  terminal state `incomplete`; command exit code 0; selected tier: **none**.
- Preflight and post-campaign complete validation: **248 tests passed each**,
  no failures, errors or skips. Tests were not edited.
- Frozen-file validation passed before inference and after calibration. All 96
  InitialPrefix objects and 1,047 model requests passed the live integrity audit.
- Database integrity and foreign keys passed; event sequences were contiguous;
  export tables exactly agreed with the database. All 3,738 archived artifacts
  were checksum-checked.

Authoritative identity and execution evidence: [preflight.json](preflight.json),
[execution-receipt.json](execution-receipt.json), [integrity.json](integrity.json),
[raw/audit.json](raw/audit.json), and both validation folders.

| Frozen identity | SHA-256 |
| --- | --- |
| Freeze manifest | `4429c0cd91e7a4f06e93cdc0cd540b5808855c1cbc749a5d30c24ab5769c04d1` |
| Canonical preregistration | `834256477c9226edfa3fce886fe30b36fbf1f617477d06f7a47577b6a7213d7d` |
| Human preregistration | `e5b41d498416925f3f8203c093e151fa7e018aeff8e4e2fd5cca11ce877ace9d` |
| Benchmark manifest | `714b91ebee1eb006929da5cbf46c7e978e06813d715e62294e1ee2e838e60ceb` |
| Fixture certification | `b663fd3bd7cf7698d8129c35bbbe9b087fce82dc1d06d55101b96fd9f912c858` |
| Analysis code | `0df28ce5d6b5b7dbf00f1e6e1a1c6938324278dc89ab75bd5142027f261976b8` |
| Initial calibration schedule | `0d48c4f395531581bf71798d0cf44344978a7264b00efa2d3ed675f31ef7a3a1` |

Full file, task, model/scaffold and potential evaluation schedule identities are
in the preflight receipt. No freeze was regenerated or silently repaired.

### Runner and orchestration

Runner: `qwen2.5-coder:1.5b`, Q4_K_M, Ollama **0.35.1**, digest
`d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668`.
Temperature 0, seed 42, context 4096, output ceiling 512, explicit `think=false`.
Chat template and system identity matched the frozen M0.7 identity before and
after execution. The template hash is
`47fca52d970e517f889420240f615fa9f8f4c6e2cb062340b9dec6fe266385b5`.

The fixed INSPECT -> ACT -> accepted state-changing EDIT -> automatic public
verification scaffold was retained. A candidate means an accepted edit followed
by verification, not a model call or rejected edit. Per-window limits remained
15 decisions, 15 tool calls, 16,000 combined tokens and 120 seconds, with the
frozen verification reservation and admission rules. Maximum recorded window
wall time was 107.984 seconds. No unrecorded generation warm-up or selective rerun
was introduced. Laptop hardware/environment metadata is retained in the raw
experiment manifest; no Pi specifications were inferred.

### Calibration qualification

Eligibility required **all** of: 10-22 first-candidate public successes, at least
26 verified candidates, at least eight verified failures, and failures spanning
at least six families. Closest-to-16/more-failures/lower-tier tie-breaking applies
only to eligible tiers. None was eligible, so no tie-break was applied.

| Tier | Tasks | Verified candidates | Public passes | Verified failures | Failure families | Acquisition failures | Qualifies |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| L1 | 32 | 2 | 2 | 0 | 0 | 30 | No |
| L2 | 32 | 14 | 0 | 14 | 4 | 18 | No |
| L3 | 32 | 8 | 0 | 8 | 3 | 24 | No |
| Total | 96 | 24 | 2 | 22 | Not additive | 72 | No selected tier |

The recorded decision exactly matches recomputation using the frozen
`select_tier` implementation: [tier-selection.json](tier-selection.json).
Forecast: **not run**, because no tier qualified. This is not a forecast-gate
failure and does not demonstrate that final evaluation would fit within 9h/9M.
The 12h/12M hard ceiling was not reached. No budgets or thresholds were changed.

### Operational notes and limitations

There were no interrupted or selectively repeated live acquisition windows.
Readonly operational helpers were outside the frozen Runner/tool set; they only
verified, observed and archived evidence. An intermediate progress readout was
corrected to distinguish active windows from completed formation failures;
terminal counts were recomputed from the complete database. No research data,
scaffold, evaluator or statistical implementation was repaired.
The backup verifier uses immutable read access; temporary reader-created SQLite
WAL/SHM sidecars were excluded from the archive without altering the backup.

The frozen no-qualification path does not close residual control-plane wall
overhead. Recorded physical wall time is 4,865.993 seconds; campaign creation to
the final window termination spans 4,875.531 seconds, 9.538 seconds longer.
Both are reported, rather than silently rewriting the ledger. The supervisor's
hard guard also checks elapsed monotonic time. Validation and reporting time are
outside the live campaign ledger; these figures are not total project compute.

A separate user-requested SSH connectivity check succeeded during this work.
It ran only a marker, login-name and hostname check, with no Pi changes. It was
not a Runner action or research workload; no Pi data, inference or optimization
entered this campaign. This incidental access is disclosed rather than claiming
that no Pi connection occurred anywhere in the session.

## Benchmark

The existing frozen suite contains 384 certified fixtures: three pre-generated
tiers, each with 32 development and 96 evaluation tasks. Only the 96 development
acquisitions were executed. Development uses 16 template clusters per tier,
two instances per template and eight families, with four tasks/family/tier.
The planned final cohort remains 96 tasks, 32 template clusters and eight
families. No final evaluation cohort was launched or retired by this campaign.
The 288 potential evaluation fixtures received no live model evaluation.

Each fixture has eight public and 32 disjoint hidden inputs. Reference/mutant
certification was verified before inference; reference certification is not
hidden scoring of a model-generated candidate. Instances/tiers share template
structure; the 96 calibration tasks are not 96 independent research replicates.

Candidate formation rates were L1 6.25%, L2 43.75%, L3 25.00%; overall 25.00%.
Initial public success rates were L1 6.25%, L2/L3 0%; overall 2/96 (2.08%). These
are descriptive development rates, not final evaluation or validated pass rates.

| Family | L1 formed / passed | L2 formed / passed | L3 formed / passed |
| --- | ---: | ---: | ---: |
| boundary_empty | 0 / 0 | 0 / 0 | 0 / 0 |
| coupled_conditions | 0 / 0 | 4 / 0 | 2 / 0 |
| duplicates_order | 0 / 0 | 0 / 0 | 0 / 0 |
| early_returns | 0 / 0 | 0 / 0 | 0 / 0 |
| initialization_accumulation | 2 / 2 | 2 / 0 | 0 / 0 |
| parsing | 0 / 0 | 4 / 0 | 4 / 0 |
| state_machine | 0 / 0 | 4 / 0 | 2 / 0 |
| two_functions | 0 / 0 | 0 / 0 | 0 / 0 |

## Q1 - Test-time interaction

V_D(1..5), Delta_I, its 95% cluster-bootstrap interval, validated recovery rate,
first recovery distribution and marginal recovery costs are **not estimated**.
The 10pp materiality threshold remains fixed, but no H-I interpretation label is
assigned. The 22 verified failures received no continuation windows. Recovery is
unobserved, not measured as zero. No H-I p-value was calculated.

## Q2 - Detailed feedback

D@5 versus O@5, Delta_F, its interval, the sole confirmatory cluster label-swap
p-value and feedback-policy cost differences are **not estimated**. No D/O
branches were executed. Detailed feedback is not assumed beneficial or useless.
The frozen 100,000-permutation, seed-8006 analysis was not invoked on calibration.
D/O would not be equal-token treatments; a future completed comparison measures
the complete feedback policies and their costs.

## Q3 - Continuation vs restart

V_R(5), D@5 minus R@5, restart repetition, duplicate-candidate rates and restart
costs are **not estimated**. No R branch ran. Temperature zero alone does not
prove behavioral determinism; the conditional 16-window reproducibility audit
was not reached. D/R changes workspace, interaction history and feedback
availability simultaneously and is not a pure feedback comparison.

## Public vs hidden

There were two initial public passes. Their hidden and validated outcomes are
**unknown**, not zero and not assumed passes. Public-only overfitting/regression
counts cannot be estimated without hidden measurement. No live candidate hidden
scoring occurred during or after calibration. The terminal data seal explicitly
does **not** authorize hidden scoring of this calibration state.

## Efficiency

| Tier | Model calls | Tool calls | Input tokens | Output tokens | Total tokens | Inference s | Recorded wall s incl. preparation | Rejected edits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | 406 | 408 | 394,850 | 47,804 | 442,654 | 724.211 | 1,807.377 | 372 |
| L2 | 288 | 302 | 267,301 | 32,356 | 299,657 | 494.488 | 1,305.356 | 242 |
| L3 | 353 | 361 | 338,721 | 41,294 | 380,015 | 630.072 | 1,753.260 | 313 |
| Total | 1,047 | 1,071 | 1,000,872 | 121,454 | 1,122,326 | 1,848.771 | 4,865.993 | 927 |

Public verification took 14.483 seconds in total. Inference and verification
times are components of elapsed execution, not additions to the wall total.
Requests, completed responses and physical model receipts each number 1,047.
The 1,071 tool calls comprise 96 reads, 951 edit proposals and 24 automatic
verifications. Unique physical receipts count the acquisitions once; no logical
D/O/R policies were executed, so no logical policy totals or arm-cost
reconciliation are claimed for this stopped calibration.

| Observable inference purpose | Calls | Input tokens | Output tokens | Inference s |
| --- | ---: | ---: | ---: | ---: |
| INSPECT | 96 | 47,902 | 1,536 | 42.027 |
| ACT selecting edit_file, including rejected edits | 951 | 952,970 | 119,918 | 1,806.744 |

These labels use recorded control phase/action, not inferred internal reasoning.
All unsuccessful acquisitions and rejected proposals remain in the cost totals.
The k=1..5 evaluation curves, common-compute comparisons and increments 1->3,
3->5 and 1->5 were not observed. Incremental costs/successes and cost per validated
recovery are **not estimable**; they are not assigned zeros. No economic claim
about additional repair attempts follows from these calibration costs.

## Failure modes

Sixty windows ended at token admission exhaustion and twelve at decision budget
exhaustion. The other 24 ended after automatic verification: 22 FAIL, two PASS.
GIVE_UP, malformed-output, infrastructure and manual-STOP terminations were zero.

Of 951 edit proposals, 24 were accepted (2.52%) and 927 rejected (97.48%).
915 rejections carried the composite error `Edit is empty, unchanged or too large`;
12 carried `Automatic verification reservation exhausted`. The composite message
alone does not identify which of its conditions caused each rejection.

Frozen observer-only stagnation metrics, summed **within** acquisition windows:
848 repeated canonical edits, 836 repeated rejected tuples and a maximum
repeated-action streak of 14. Per-task distinct valid-action ratios and unique
byte/AST candidate counts are supplied in the JSON/CSV. Repeated public failure
signatures were zero because each initial window can verify at most one candidate;
that structural zero is not evidence of effective repair. No stagnation
intervention, Planner, memory or generated tool was introduced.

## Supported conclusions

1. None of the frozen tiers satisfied the declared calibration requirements with
   this fixed Runner, interface, scaffold and acquisition budget.
2. Formation failures and repeated rejected proposals dominated these initial
   acquisitions. This is evidence about the complete model/scaffold/tool policy,
   not an isolated estimate of intrinsic model coding capability.
3. The eligibility gate correctly prevented an unqualified final evaluation.
   The negative calibration evidence, including unsuccessful costs, is retained.
4. The live run demonstrated initial acquisition, automatic public verification,
   durable prefix/cost logging and terminal export/auditing. Live D/O/R repair,
   hidden evaluation and feedback effects were not demonstrated.

## Unsupported conclusions

This outcome does not establish that retries, detailed feedback or sequential
repair do or do not work. It is not an equivalence result or an absence-of-
significance argument. M0.7 used different tasks/protocol, so its pass rate is not
a paired comparator here. Nor does M0.8 alone establish universal test-time
scaling laws, equivalence to large models, Planner/self-improvement effectiveness,
general software-engineering performance, Raspberry Pi feasibility or cross-model
generalization. No post-hoc significance tests, exclusions or prompt improvements
were added.


[Private task-level/operational evidence retained in the research repository.]
