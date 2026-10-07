> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.6 Results

## Decision

**No provisional scaffold qualifies.** Every policy/model cohort reached public
verification on 0/8 tasks, below the required 2/8. C2 and C3 met the EDIT gate
(8/8 tasks), but that alone is insufficient. Selection used only the primary
model's public evaluation results; the independent replication did not rerank it.
The final delivery commit is reported in the completion message; the actual
experiment source commit is `451aa53501dcdf92ed1e8ada7a599c0b1e039652`.

## Provenance

The clean `15ec336f02ec8e1dc95d2aeaa71e4c6c7c606f96` baseline passed all 153
tests and the audited six-trial fixture matrix before the annotated `m0.5` tag
was created. Previous fixtures, evaluators, Supervisor, logger, and M0.2-M0.5
records are unchanged. M0.6 changes to the Experiment Manager only dispatch the
new scaffold; all edits still pass through the original Supervisor.

Twelve mechanically mutated, dependency-free Python tasks were constructed from
fixed recipes and cases. All twelve mutants failed public and hidden tests, and
all twelve reference fixes passed both through the existing engine: 24 scripted
trials, zero live model calls. Suite construction and validation were committed
at `c165309` before any M0.6 live generation. The suite envelope hash is
`1f2680cf9cb9371be83785454eeb9fd634df6d8c4dbcb04e7e542c704d09a92a`.

Calibration: `m06_01_span`, `m06_02_perimeter`, `m06_04_product`, `m06_06_last`.
Evaluation: `m06_00_above`, `m06_03_negative`, `m06_05_sum`, `m06_07_quotient`,
`m06_08_squares`, `m06_09_digits`, `m06_10_matches`, `m06_11_interval`.
The sorted-ID shuffle uses Python `Random(601)`, with four/eight fixed tasks.
All twelve task hashes are printed in [report.md](report.md) and frozen in
`configs/m06-suite.json`, along with every fixture file hash and recipe identity.
No task or policy was changed after live generation began.

## Model Identity

- Primary: `qwen2.5-coder:1.5b`, Q4_K_M, 1,543,714,304 parameters;
  digest `d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668`.
- Replication: `llama3.2:1b`, Q8_0, 1,235,814,432 parameters;
  digest `baf6a787fdffd633537aa2eb51cfd54cb93ff08e28040095462bb63daf552878`.

Both used Ollama `0.35.1`, temperature 0, seed 42, context 4096, output ceiling
512, explicit `think=false`, 30-second request timeout and five-minute keepalive.
The 512 ceiling matches actual M0.5 diagnostic conditions; `models.json` records
the difference from its preparation inventory's 256 ceiling. Digests, runtime,
templates and system hashes are unchanged. The observed profile is unchanged:
Windows release 10, AMD64, Python 3.11.4, 16 logical CPUs. RAM and temperature
were not measured by this profile; no Pi specification is inferred.

## Behavior

Counts below are per eight-task cohort. Every cohort used 120 model calls.
C2's ACT count denotes its exhausted-inspection action set, not an explicit phase.
C0/C1 have no ACT phase. GIVE_UP selections were zero in every cohort.

| Model | Policy | Reads / unique / repeated | Successful / redundant rejected | Mean reads | ACT tasks | EDIT | Accepted / rejected / token-denied edits | Edit generation | Useful efficiency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen | C0 | 120 / 8 / 112 | 120 / 0 | 15 | 0 | 0 | 0 / 0 / 0 | 0% | 0% |
| Qwen | C1 | 120 / 8 / 112 | 24 / 96 | 15 | 0 | 0 | 0 / 0 / 0 | 0% | 0% |
| Qwen | C2 | 16 / 8 / 8 | 16 / 0 | 2 | 8 | 104 | 5 / 99 / 0 | 62.5% | 4.17% |
| Qwen | C3 | 8 / 8 / 0 | 8 / 0 | 1 | 8 | 112 | 5 / 106 / 1 | 62.5% | 4.17% |
| Llama | C0 | 120 / 8 / 112 | 120 / 0 | 15 | 0 | 0 | 0 / 0 / 0 | 0% | 0% |
| Llama | C1 | 120 / 8 / 112 | 24 / 96 | 15 | 0 | 0 | 0 / 0 / 0 | 0% | 0% |
| Llama | C2 | 16 / 8 / 8 | 16 / 0 | 2 | 8 | 104 | 0 / 104 / 0 | 0% | 0% |
| Llama | C3 | 8 / 8 / 0 | 8 / 0 | 1 | 8 | 112 | 0 / 112 / 0 | 0% | 0% |

Transition rate and EDIT-attempt rate were 100% for C2/C3 and zero for C0/C1
for both models. Candidate checkpoints, public verification, public passes and
hidden passes were all zero. Hidden scoring therefore evaluated the initial buggy
checkpoint, not the unsubmitted accepted changes. This does **not** demonstrate
that Qwen's accepted edits failed hidden tests; their correctness was unmeasured.
Qwen accepted one edit in each of above, negative, sum, squares and matches under
both C2 and C3, then kept selecting edits rather than verification.

Public rejection evidence across C2/C3: Qwen had 138 non-unique/unmatched patches,
40 empty/unchanged/oversized edits, and 27 unsupported-method edits. Llama had
107 non-unique/unmatched patches, 68 empty/unchanged/oversized edits, 27 syntax
rejections, and 14 module-scope policy rejections. No smart repair was applied.

## Cost

Inference sums backend prompt-evaluation and output-evaluation durations. Wall
seconds sum end-to-end trial durations, including final hidden measurement but
excluding cohort export/audit overhead. Fixed sequential order and warm caches
mean latency differences are descriptive, not controlled speed benchmarks.

| Model | Policy | Input tokens | Output tokens | Inference seconds | Wall seconds |
| --- | --- | --- | --- | --- | --- |
| Qwen | C0 | 80,858 | 1,920 | 56.719 | 78.109 |
| Qwen | C1 | 80,337 | 1,920 | 55.684 | 76.938 |
| Qwen | C2 | 97,473 | 8,394 | 128.631 | 152.516 |
| Qwen | C3 | 97,968 | 8,906 | 131.830 | 154.266 |
| Llama | C0 | 81,300 | 1,920 | 54.568 | 78.266 |
| Llama | C1 | 80,782 | 1,920 | 55.249 | 76.719 |
| Llama | C2 | 80,182 | 3,233 | 66.673 | 88.892 |
| Llama | C3 | 86,234 | 5,449 | 97.835 | 120.032 |

Primary evaluation: 960 calls, 685,134 input + 33,662 output = 718,796 tokens,
647.189 inference seconds and 825.738 wall seconds. Calibration is separate:
32 trials, 480 calls, 337,680 input + 15,632 output = 353,312 tokens, 299.057
inference seconds and 391.920 wall seconds. Total live generation: 1,440 calls,
1,072,108 tokens. Scripted construction tests are not inference compute.

## Research Answers

1. Blocking redundant reads reduced successful reads (120 to 24), but both models
   kept choosing READ 120 times: rejection alone did not alter the action attractor.
2. A two-read budget induced EDIT on all eight tasks for both models. C2 is the
   least restrictive tested intervention that escaped read-only action selection.
3. C3 eliminated repeated reads and needed one source read, but did not improve
   accepted-edit task rate, verification reach or measured solving over C2.
4. Neither model reached public verification on any fresh evaluation task.
5. No policy produced a measured fresh-task solve. Unsubmitted changes are not solves.
6. C2 suffices for transition to editing, but no tested controller suffices for a
   productive autonomous coding-feedback loop or the operational engineering gate.
7. Calls remained 120 per cohort. Qwen's C2/C3 spent more tokens and roughly twice
   the inference time of C0; no verified-success or model-call amortization occurred.

H1's predefined material verification increase (2/8 tasks over C0) was not observed
for either model. These results are consistent with H0 on this small cohort, not
proof of a general null effect. All operational gates failed, so ranking tie-breakers
were not invoked. The public-only decision is `policy=null` with no eligible policies.

## Limits

Eight synthetic tasks, one replicate, one seed, fixed model/policy order, and the
existing literal E0 contract limit generalization. New artifacts do not establish
that elementary algorithms were unseen in pretraining. C3 confounds phase naming
with earlier READ removal; its superiority as an explicit state machine was not
isolated. C1's fixed context-eviction refresh exception permits recurring successful
reads. C2/C3 cannot reread after edits and can lose original source context as recent
observations rotate. Protocol/state text and native action schemas are interventions
in addition to Supervisor enforcement, without coding hints.

No automatic verification was used. This distinguishes M0.6 from M0.5 A2's complete
preload, one coding decision and trusted automatic verification; the earlier positive
signal cannot be attributed to READ removal alone. Accepted edits and repeated
rejections expose a new action attractor, not verified coding capability.

One Qwen C3 matches call consumed 16,216 measured tokens against a 16,000 limit;
the original Supervisor denied its valid EDIT before execution. The first extractor
counted admitted actions rather than all schema-valid selections, omitting this one
EDIT. The offline correction raises C3's selection count from 111 to 112 and records
one unadmitted action separately. It changes no policy, task, model call, acceptance
criterion, accepted/rejected edit count, score, or selection. Original summaries,
selection and raw export remain preserved; `completion-audit.json` documents the delta.


[Private task-level/operational evidence retained in the research repository.]
