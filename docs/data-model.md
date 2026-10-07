# Data dictionary

Authoritative DDL: `migrations/001_initial.sql`. WAL, foreign keys and FULL
synchronous commits are enabled. Numbered migration filename/checksum is immutable
after application; missing/newer/changed migrations are rejected. No future
memory/tool-evolution tables are created.

| Table | Contents |
| --- | --- |
| schema_migrations | Integer version, migration name and SHA-256 |
| manifests | Canonical JSON, hash PK, kind and schema version |
| experiments | UUID, manifest FK, protocol version, creation UTC |
| runs | UUID, experiment/manifest FK, deterministic trial key, development/formal mode, task/hash/version, seed/replicate, protocol/scaffold identity/version/parent, Git commit/dirty flag, budget/usage/platform JSON, owner PID/creation identity, stop flag, lifecycle/reason, initial/selected checkpoint FKs, private score/status, start/end UTC |
| attempts | UUID, run FK, unique ordinal, checkpoint/parent FKs, public outcome and result JSON |
| evaluations | UUID, run/optional attempt FKs, checkpoint FK, test hash, split, outcome, nullable binary score and bounded result metadata/output artifact |
| events | Integer ID, run FK, unique sequence per run, UTC, monotonic time, clock-session UUID, actor, type, payload version and JSON |
| artifacts | SHA-256 PK, kind, relative storage path, bytes and visibility classification |

Manifest records execution profile, canonical authored-config hash, task source/
public/hidden hashes, scaffold identity, distinct harness/code hashes, fixed model
and tool identities, seed/replicate, budgets and content-based Git provenance.
The authored TOML is also an artifact referenced by trial_reserved events.
Visibility labels are metadata, not filesystem ACLs or model-readable handles.

Budget JSON: maximum attempts/decisions/tool calls/simulated tokens/wall time,
subprocess timeout, workspace/output/edit byte limits and contract version.
Usage JSON: charged attempts/decisions/tools, input/output token units, usage kind
and monotonic Runner elapsed time. Crashed-run usage is the last durable lower
bound; time spent since the last receipt is not reconstructed as a measurement.
Platform JSON includes observed OS, release, architecture, Python and logical CPU
count; RAM/temperature are NULL. Unsupported enforcement flags are explicitly false.

Actors: runner, supervisor, public_verifier, hidden_evaluator, control_plane.
Decision/action events correlate via call_id; verification events include attempt_id
and checkpoint/test references. Requests/results/output are artifact-backed to
bound SQLite payloads. Starts without corresponding completions remain evidence
of uncertainty, never silently erased. Event sequence, not UTC alone, orders a run.
Monotonic values are comparable only within their clock session.

Private evaluator outcome pass scores 1, ordinary test fail scores 0. Timeout,
cancelled/error/incomplete/not-evaluated states have NULL score. Run status finished
does not imply hidden pass. Interrupted rows and pending attempts are retained.
The unique formal trial-key index protects only this database. A SQL trigger blocks
hidden records before normal Runner termination, including stopped/interrupted runs.

Artifacts reside at `<state>/artifacts/<sha256>`. A checkpoint is canonical JSON
mapping relative file names to blob hashes; ancestry is recorded separately so
identical content has identical identity. Artifact and edit writes are atomic and
file-fsynced; this is not a guarantee against media failure or every power-loss mode.

`export` reads one SQLite transaction and writes a deterministic ZIP containing
research.json, one CSV per table, all registered blobs and checksums.json. Entries
have fixed timestamps and ordering. JSON preserves NULL/type information; CSV
uses an empty field for NULL and JSON text for nested payloads. Join experiment ->
run -> attempts/events/evaluations using IDs, then selected checkpoint/artifact
references to reconstruct the complete recorded history. Same-snapshot bytes are
identical; separate runs intentionally have different IDs/timing-bearing artifacts.
Exports are currently in-memory and unbounded over total research history; use
small M0.1 databases. Streaming/selective export is deferred, not silently truncated.
