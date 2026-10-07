> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.3 Results

## Outcome

Completed negative calibration result. No alternate meets both preregistered gates.
Backend schema constraints remove envelope-format failures in this sample, but
the Runner never edits or verifies under that interface. The dominant remaining
action-to-verification bottleneck is repeated reading, not malformed JSON. The
tested DSL does not improve validity. No additional attempt scaling or selected-
protocol repeats are eligible. Stop after M0.3; no M0.4 or Pi work was performed.

Implementation: `4f55e8953a72c2255b164e90b0879ad249ab6492`.
Evaluation freeze: `3fc168c` (documentation/receipts added, implementation unchanged).
Preregistration: `fd07c05`, before comparative inference.
Annotated `m0.2` tag resolves to `e8cd17f2f95e7cb79d2dbf1ff01c44d20731dd26`.
The older annotated `m0.1` tag is unchanged. The final report-only commit can be
identified with `git log -1 --format=%H -- docs/research-records/m03/RESULTS.md`.

## Fixed Runner and Split

Ollama API 0.35.1; local `llama3.2:1b`, Q8_0, 1,235,814,432 parameters.
Digest: `baf6a787fdffd633537aa2eb51cfd54cb93ff08e28040095462bb63daf552878`.
Temperature 0, seed 42, context 4096, output cap 256, timeout 30 seconds, keep-alive
5m. Same Windows laptop, i5-13500H (12 cores/16 logical CPUs), RTX 3050 Laptop GPU,
Windows 11 10.0.26200, project Python 3.11.4. CPU/GPU/RAM identity was rechecked via
CIM and saved in laptop-environment.json. No model download or replacement.

[Private account observation retained privately.]

All eight task/version hashes match preregistration and the M0.2 fixtures. These
tasks were exposed during M0.2; this is not a pristine generalization benchmark.

## M0.2 Failure Decomposition

All 57 decisions, disjoint primary categories:

| Primary category | Count | Percentage |
| --- | --- | --- |
| Patch context absent | 25 | 43.86% |
| Missing required field | 24 | 42.11% |
| Unexpected field | 3 | 5.26% |
| Truncated JSON (backend length termination) | 2 | 3.51% |
| Unchanged edit / operationally inapplicable | 2 | 3.51% |
| JSON syntax error (duplicate key) | 1 | 1.75% |
| All other specified categories | 0 | 0% |

The 27 valid envelopes were all rejected edits, not successful actions. The 30
invalid envelopes never reached authorization. The JSON artifact includes 1-3
bounded public-output examples per populated category and all decision references;
repetition is separately counted as overlapping evidence. Hidden tests/evaluations
were not read by the audit. Extra checkpoint inspection proved all 25 context
failures had zero occurrences of the requested old text. This justified E1, without
assuming that replacement would solve the model's behavioral or coding failures.

## Protocols and Funnel

A: unchanged P0 `runner-json-1` + E0 exact single-match edit.
B: P1 `runner-json-schema-1` + E0; native schema accepted by installed runtime.
C: P2 `runner-dsl-1` + E0; strict parser, no fuzzy repair or extra reasoning hints.
D: P1 + E1 bounded whole-file replacement. No accepted E0 protocol existed, so D
used the preregistered best-ranked alternate fallback. E1 is Supervisor-mediated,
protected-path/text/size/AST checked, and checkpoints before atomic writes.

Four evaluation tasks per condition; attempt budget 1 throughout:

| Stage | A: P0/E0 | B: P1/E0 | C: P2/E0 | D: P1/E1 |
| --- | --- | --- | --- | --- |
| Model decisions / responses | 8 | 60 | 4 | 60 |
| Parse valid | 8 (100%) | 60 (100%) | 0 (0%) | 60 (100%) |
| Schema valid | 4 (50%) | 60 (100%) | 0 (0%) | 60 (100%) |
| Authorized | 4 (50%) | 60 (100%) | 0 (0%) | 60 (100%) |
| Applicable | 0 (0%) | 60 (100%) | 0 (0%) | 60 (100%) |
| Executed | 0 (0%) | 60 (100%) | 0 (0%) | 60 (100%) |
| Checkpoint created | 0 | 0 | 0 | 0 |
| Public verification reached | 0 | 0 | 0 | 0 |
| Public verification passed | 0 | 0 | 0 | 0 |
| Hidden evaluation passed | 0 | 0 | 0 | 0 |

Rates above use decisions as denominator. Verification task rates are separately
0/4 in every condition. Final hidden task passes are 0/4 each (initial unsubmitted
checkpoint scored only after termination), not measurements of repaired candidates.
Unknown/no-denominator conversions remain null, not zero or inferred success.

| Conversion | A | B | C | D |
| --- | --- | --- | --- | --- |
| Parse -> schema | 50% | 100% | n/a | 100% |
| Schema -> authorized | 100% | 100% | n/a | 100% |
| Authorized -> applicable | 0% | 100% | n/a | 100% |
| Applicable -> verification | n/a | 0% | n/a | 0% |
| Verification -> public pass | n/a | n/a | n/a | n/a |

Invalid-action metric is explicitly **decisions that did not reach authorization**:
A 4/8 (50%), B 0/60, C 4/4 (100%), D 0/60. Separately A has 4 authorized but
inapplicable context edits, giving 8/8 nonexecutable decisions. C has 4/4
nonexecutable decisions. B/D have none, but all 120 executed actions are read_file,
including 112 consecutive repeated reads. No live E1 replacement was requested.
Thus E1's independent benefit is unmeasured; it cannot be credited or blamed for
code correctness. Unit fixtures verify that E1 can edit and pass public/hidden
checks without weakening authorization. DSL evaluation outputs were three
incomplete `EDIT path` commands and one invalid ` Fin` fragment, not silently
repaired. Failure families remain format vs tool-contract
vs coding vs backend/control; no live candidate reached a coding test failure.

## Gates and Selection

Gate A: >=75% decisions authorized. B and D pass; A and C fail.
Gate B: >=50% evaluation tasks reach public verification. All fail (0%).
Therefore no protocol is selected for scaling; M0.3 is a negative result.

For D only, P1 ranked above P2: equal 0% verification reach, then 100% vs 0%
applicable rate. Later tie-breakers were not needed. Hidden scores did not select
the output protocol or E1. Public-only selection queries do not read hidden
columns/events. Selection was saved before aggregated hidden results were read;
see protocol-selection.json and the frozen run script. Normal final hidden scoring
still occurs after each Runner termination, never as Runner feedback.

Budgets 3/5 and three-repeat selected-protocol trials were deliberately not run,
because no alternate passed both gates. There is no M0.3 repetition variance or
determinism claim; identical in-run rereads are not independent repeated trials.

## Costs

| Evaluation condition | Input tokens | Output tokens | Total tokens | Inference seconds | End-to-end seconds |
| --- | --- | --- | --- | --- | --- |
| A | 3,903 | 854 | 4,757 | 12.822 | 14.985 |
| B | 41,205 | 960 | 42,165 | 25.967 | 34.875 |
| C | 1,761 | 20 | 1,781 | 0.384 | 1.906 |
| D | 41,625 | 960 | 42,585 | 24.775 | 33.843 |
| Total | 88,494 | 2,794 | 91,288 | 63.949 | 85.609 |

Inference means backend prompt processing plus generation. Request/load time is
separate in JSON; total wall includes control-plane and final evaluator work.
Calibration: 12 trials, 71 decisions, 44,715 tokens, 40.560 inference seconds,
56.734 end-to-end seconds. Combined comparisons: 28 trials, 203 decisions,
136,003 tokens, 104.509 inference seconds, 142.343 per-trial wall seconds.
Single non-task backend probe: 42 input + 16 output tokens; 0.615 inference seconds,
5.957 backend total seconds including a 5.320s load. It is not a benchmark trial.
All model usage is measured; unknown totals are not imputed. Fixed condition order,
cache residency and contention prevent latency-causality or statistical claims.


[Private task-level/operational evidence retained in the research repository.]

## Supported and Unsupported Conclusions

Supported: native schema generation materially improves envelope/action validity
here; this DSL does not; repeated-read behavior blocks environment interaction;
E0 context construction was independently problematic in M0.2; live E1 efficacy
remains unresolved because no replacement action was emitted. The fixed model
can produce executable read actions, not demonstrated complete coding workflows.

Not supported: general coding incapability (no repaired candidates tested),
general test-time scaling, stronger-model parity, intelligence gain from easier
serialization, self-improvement, Planner efficacy, determinism, or Pi inference
adequacy. Unit reference solutions are infrastructure tests, not model successes.

## Raspberry Pi baseline

The separately saved earlier baseline is reproduced in evaluation-report.md.
No inventory was repeated or Pi modification made during M0.3. The user now
reports no camera/display/touchscreen/OLED peripherals connected. Historical
background processes are observations at the earlier timestamp, not current
peripheral state or M0.3 experimental factors.

Earlier measurements: Pi 3 Model B Rev 1.2 (a02082), Cortex-A53 4 cores/aarch64,
Linux RAM 905.04 MiB; Debian 13.7 trixie, kernel 6.18.50+rpt-rpi-v8; 64.02GB SD,
ext4 root 58.13 GiB, 51.34 GiB available; 53.692-54.768 C, throttled=0x0; 905MiB
zstd zram swap unused, SD-backed writeback; Ollama not detected (version/models
unavailable). Major historical consumers: Xorg 78.16MiB, lxsession 74.66MiB,
panel 38.03MiB, file manager 28.19MiB, unattended-upgrades ~28MiB, dashboard
24.43MiB, pi-health 22.39MiB RSS (shared pages can overlap). Old dashboard/OLED/
camera/media files are cleanup candidates only. Later preparation should preserve
SSH/network/boot/security, archive media/apps before cleanup, review headless
desktop/zram/memory-cgroup choices, then separately profile real model inference.
No cleanup, model installation or performance inference from this baseline.
