# M0.8C: precise mechanical rejection feedback

This is a new development acquisition pilot. M0.8B at `038c370` remains a
calibration stop: no difficulty tier qualified, evaluation and hidden scoring
did not run. The pilot tests whether identifying an unchanged E0 edit improves
verified candidate formation on previously exposed L2 development tasks.

Select the lexicographically smaller opaque task ID in each of the 16 L2
development templates. Freeze the manifest, public-only task snapshots and
schedule before inference. The other 16 instances receive no pilot inference.
Task inputs come from archived M0.8B initial public checkpoints and TaskViews;
the loader never opens the frozen benchmark archive or original task files.

Run two fresh original-workspace acquisitions per task. Sort pairs by template;
alternate A/B, B/A, starting A/B. A uses the original M0.8B projection. B changes
only a failed E0 observation whose error is the original combined rejection,
whose old/new are equal nonempty strings, and whose canonical arguments fit the
unchanged edit limit. Its error is exactly:

`Edit is unchanged: old and new are identical.`

This identifies the sole failing predicate of the combined E0 rejection guard.
Authorization, path checks, edit acceptance and every other error stay in the
existing supervisor. Both conditions call the original prompt packer, tokenizer,
model adapter, Window and public verifier. The new projection is applied to
Runner-visible history only; raw supervisor observations remain unchanged and
are available for an independent projection audit. Nothing instructs a semantic
repair. Message length and resulting context/token admission are part of the
feedback treatment and will be measured.

The Runner is the exact M0.8B identity including digest, quantization, runtime,
chat template, system hash and settings. The original model/window configuration
is copied verbatim. E0, temperature 0, seed 42, context 4096, output 512,
15 decisions, 15 tools, 16,000 measured tokens, 120 seconds, existing edit and
workspace limits, inspection and verification reservation all remain fixed.
There is no warmup inference. Identity mismatch prevents inference.

The campaign has 32 windows, 480 model calls, 512,000 measured tokens and 4,800
execution seconds including overhead. Each window ends at its first verified
candidate or the existing termination conditions. Infrastructure failure,
manual STOP, changed freeze or a campaign ceiling ends the pilot incomplete;
there is no automatic resume or selective rerun. Public verification is performed
once after an accepted edit. It is never followed by a repair decision.

Primary outcome: verified candidate formation, with checkpoint and automatic
public verification evidence. Report 16 paired rows, wins/losses/ties, family
coverage, public pass/fail, byte- and AST-changing candidates, no-op repetition,
model calls, input/output tokens, inference, verification and wall cost. Gate B
only if all hold: formations >=13, net additional formations >=4, formation
families >=6, verified public failures >=8. Incomplete pilots cannot qualify.
Public pass is diagnostic and does not replace any criterion.

Secondary diagnostics are fixed before inference:

- `decisions_to_first_changed_edit`: first accepted byte-changing edit's model
  decision index; null when absent. Also report first AST-changing edit separately.
- `tokens_to_first_changed_edit`: measured cumulative input+output tokens through
  that decision, including inspection and rejected actions; null when absent.
[Source-bearing example withheld.]
  null without a changed edit, with total no-ops reported independently.
[Source-bearing example withheld.]
  decision. A following non-EDIT or malformed response counts zero change.
  Byte numerator compares canonical tool/arguments, excluding contract metadata.
  Normalized numerator compares path plus AST dumps of old and new, excluding
  source positions. Report its supported denominator separately; unparseable
  old/new pairs remain unsupported rather than receiving an inferred meaning.
  These are syntactic normalizations, not proof of different behavior or correctness.
- Repeated no-ops: repeated canonical no-op requests within a window after their
  first occurrence, with maximum consecutive streak recorded separately.

Analysis is paired and descriptive. Report the effect B formation rate minus A
and an exploratory percentile 95% interval from 10,000 whole-template resamples
within the eight fixed families, seed 8006. No p-value, outcome-dependent
analysis selection or significance-driven promotion. The small, exposed
development sample limits generalization.

Before inference, freeze a clean implementation commit, all code/tests and
preregistrations, public-only task inputs, manifest, schedule, identical A/B model
configs, projection policies, model/tokenizer identities and initial prompt
hashes. Unit tests use temporary harness fixtures. Validate the existing suite
and new projection/isolation/accounting/gate/diagnostic tests. Pilot DB triggers
deny hidden evaluation, scores, cohort retirement and formal runs even after seal.

After inference, audit schedule and original checkpoint pairing, prompt replay
from raw observations, unchanged model options and budgets, receipts versus run
usage, token/call ceilings, SQLite integrity, public-only evaluations, source
history checksums and independent exports. Preserve all outcomes and missing rows.

Passing the gate supports consideration of a separately preregistered
confirmation. Behavioral improvement below the gate does not advance
automatically. Little/no effect can motivate a later E0/E1 experiment. This pilot
does not measure repair, final benchmark performance or hidden generalization.
Stop after reporting and archiving the pilot; no confirmation/evaluation/E1,
Planner, memory, new model or Raspberry Pi work follows automatically.
