# M0.3 continuation status (superseded)

The missing specification was supplied on 2026-10-05. See [M0.3 protocol](m03.md)
and `configs/m03-preregistered.json`. The text below preserves the earlier
dependency audit; it is not the current implementation status.

The 2026-10-05 goal addendum authorizes a separate read-only Pi inventory and then
refers to a previously specified M0.3 Agent-Tool Interface Calibration. The
inventory and conservative cleanup proposal are complete in the standalone
[Private evidence retained separately].
Its report contains a `Raspberry Pi baseline` section ready to reference in the
eventual M0.3 report. No cleanup was executed.

## Laptop controls retained

M0.2's actual live development run used `llama3.2:1b` Q8_0, digest
`baf6a787fdffd633537aa2eb51cfd54cb93ff08e28040095462bb63daf552878`, on this Windows
laptop (i5-13500H, RTX 3050 Laptop GPU, Python 3.11.4). Its recorded runtime is
Ollama API 0.35.1. Read-only API checks during this task returned that same version
and installed model digest. Preset settings remain temperature 0, seed 42,
num_ctx 4096, num_predict 256, timeout 30 seconds and keep_alive 5m.

Qwen2.5-coder:0.5b is now also visible in the laptop's model list. It was not used
or substituted in this task; its presence does not change the recorded M0.2
comparison model. No model was pulled or installed by this task.

The experiment source, configurations, migrations, fixtures, tests and package
metadata match M0.2 commit `e8cd17f`; only the independent inventory collector and
research documentation/records were added. No Pi observation has changed model,
hardware, runtime, task versions, tool protocol or acceptance criteria. No model
inference or new model-performance experiment was run in this task. M0.2's
database/export remain unchanged.

## Required specification

M0.3 itself is not complete. The available objective files specify M0.1, M0.2 and
the Pi inventory addendum; the repository has no M0.3 specification, interface
variants, evaluation matrix, calibration split or acceptance gates. Those details
cannot be reconstructed from the phase title or the failed M0.2 smoke results.

A clarification asking for that specification was sent while inventory work
continued. Implementation and live M0.3 trials depend on receiving it. Keep the
full goal open; do not label this inventory or an invented comparison as completion
of Agent-Tool Interface Calibration. The goal addendum's original intent remains:
calibrate the interface on the same laptop/model/runtime while separately recording
the Pi baseline and deferring Pi cleanup.
