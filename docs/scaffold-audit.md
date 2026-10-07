# Partial scaffold audit

Inspected all 12 existing Python source files, migration 001, packaging, ignore
rules and PLANNING.md before adding runtime implementation. No prior research
database or executable CLI existed. Older Pi directories are out of scope.

| File | Decision | Reason |
| --- | --- | --- |
| `__init__.py` | Keep | Explicit package, protocol and contract versions |
| `__main__.py` | Keep | Small CLI entry point; complete its missing dependency |
| `contracts.py` | Modify | Keep canonical JSON/dataclasses; add bounded decision state and public-only feedback |
| `runner.py` | Modify | Keep adapter delegation; pass bounded decision state |
| `planner.py` | Keep | No-op and public-only summary; no optimization |
| `tools.py` | Keep | Exactly three fixed tools with argument validation |
| `adapters/__init__.py` | Keep | No runtime behavior |
| `adapters/scripted.py` | Modify | Keep fixture-owned scripts; accept future-compatible decision state |
| `adapters/platform.py` | Modify | Keep platform boundary; fail closed when Windows Job assignment fails rather than leak descendants through fallback |
| `artifacts.py` | Modify | Keep content addressing; atomic durable writes, validated paths and confined restore destinations |
| `telemetry.py` | Modify | Keep WAL/FK/migrations; serialize event sequence allocation and expose durable STOP |
| `config.py` | Modify | Keep TOML resolution; separate scaffold/harness hashes, content provenance and execution identity |
| `001_initial.sql` | Modify before first application | Restrict hidden records to terminated Runner; preserve minimal seven concepts |
| `pyproject.toml`, `.gitignore` | Keep | Standard-library package and ignored runtime state |

No duplicate implementations or obsolete source files need removal. New modules
complete missing responsibilities rather than introducing a second storage/tool
stack. The planned memory and real-model modules are deliberately not created.
