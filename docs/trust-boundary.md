# Trust and visibility

M0.1 is not an OS security sandbox. All components run under the current account.
Only reviewed fixture scripts and programs may be executed. Do not substitute
LLM-generated code, arbitrary tools, shell commands or external Planner patches.

Runner delegates to ScriptedModel and returns typed actions. Only Supervisor reads,
edits or invokes public verification. Registry permits read_file, edit_file and
run_public_tests; no generic exec/import/shell interface exists. Reads/edits must
name declared files; only editable source is writable. Absolute/traversal paths,
symlinks and Windows reparse points are rejected. Restoration is restricted to
Supervisor-owned workspaces/evaluations and validates blobs before replacing files.

TaskView contains no private TaskSpec, manifests, database or hidden-test references.
PublicVerifier has no hidden-suite input. PublicFeedback is an explicit allowlist,
not an arbitrary serialization of EvaluationResult. A private result accidentally
returned through public verification interrupts the trial before observation delivery.
HiddenEvaluator requires a terminated Runner. Hidden outputs/scores are written
to research records only. NoOpPlanner consumes public summaries; optimization
and final-test feedback channels are absent.

Supervisor, evaluator/tests, logger, registry, protocol and scoring criteria are
trusted and fixed. The only fixture mutations are bounded reviewed source edits.
Scaffold hash identifies Runner/scripted strategy code; harness hash separately
identifies the control plane. No component can promote or rewrite itself through
supported tools. SQL constraints and interface tests are defense-in-depth, not
protection against an attacker with direct same-account access.

Tests demonstrate current Windows supported-action confinement, real symlink and
junction rejection, cancellation, Job Object descendant cleanup and controller
crash recovery. Job assignment failure is an explicit execution error. There is
a short spawn-to-job-assignment interval; this is not a containment guarantee for
hostile programs. POSIX process groups are a lifetime mechanism, not a sandbox,
and a hostile child can detach. Linux behavior is not certified by Windows tests.

Not enforced: network access, hard RAM/disk quotas, arbitrary-code filesystem
access, concurrent host tampering/TOCTOU attacks, isolation from user credentials
or cryptographic log immutability. The Runner receives no environment dump, but
reviewed subprocess code could still access host resources. Fixture review is
the safety prerequisite. Unexpected process/cleanup errors are not scored as pass.

Exports include hidden evidence and full research provenance; treat them as
researcher-only files. They are not redacted public datasets. No credentials are
requested/stored, but a fixture author must not put secrets in source/output.
CLI state/export destinations are researcher-controlled, never Runner arguments.

Before enabling arbitrary generated code/tools, implement and test OS-level
isolation, private asset protection, resource enforcement and permission tiers.
No Raspberry Pi access, obsolete-service cleanup or hardware stressing belongs
to M0.1. Later measurements distinguish declared, observed and inferred limits.
