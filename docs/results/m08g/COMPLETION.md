> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.8G Completion

Executed implementation: `80526098c899f242dd60c54051f03f59a4424d6a`.
Final evidence commit: annotated tag `m0.8g`; resolve with `git rev-parse m0.8g^{}`.
Starting evidence `5843da7` is preserved at annotated tag `m0.8f`.
Protocol 0.5. All 328 tests passed before inference; the post-run receipt is in
`post-validation/validation.json`. No historical source or evidence file changed.

## Final Status

- Completed exactly 32 fresh windows across the 16 exposed L2 development tasks.
- Exact pinned Qwen2.5-Coder 3B Q4_K_M / Ollama 0.35.1; identity unchanged at end.
- E0/E1 formed 8/16 each; public pass/fail 0/8 versus 7/1.
- Known context-mismatch subset: 0/2 E1 formations. No exact-old rescue confirmation.
- Paired: E0-only 2, E1-only 2, both 6, neither 6; net formation difference zero.
- E0: 106 EDITs, 62 unchanged, 44 changed; 24 context and 12 syntax rejections.
- E1: eight valid changed replacements, all accepted; zero submitted no-op/syntax
  rejections, but eight ACT outputs truncated at 512 tokens and failed JSON parsing.
- Calls/tokens: E0 122/126,320; E1 32/22,737; physical total 154/149,057.
- Inference 466.509s; receipt-accounted wall 564.468s; elapsed 566.078s.
- Calls/tokens per formation: E0 15.25/15,790; E1 4/2,842.125, failed windows included.

The negative formation/mechanism result and positive secondary public result are
distinct. `no_observed_benefit` is not a claim of no public-correctness difference.
The >=4 net-formation broader-benefit rule was not met. Neither E0 nor E1 is newly
promoted, no 13/16 gate applied, and no population/equivalence claim is made.
All public candidates were first candidates: repair scaling remains unmeasured.

Recommended next experiment: separately authorize/preregister **7B under the same
E0 development scaffold**, with the qualifications in `INTERPRETATION.md`. It was
not downloaded, loaded or run by G. E1 output-ceiling sensitivity is untested and
must not be silently changed in that control. No sampling or Planner work started.


[Private task-level/operational evidence retained in the research repository.]
