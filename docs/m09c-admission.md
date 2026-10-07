# M0.9C Admission Evidence

This milestone permits a safe admission stop before optimization. It does not
permit Qualification48, final-cohort content access, hidden scoring, paid fallback
or use of an unverified previously exposed credential.

The operational helper `scripts/m09c.py` deliberately has no live inference or
qualification launch command. It does not change any frozen M0.9B module,
ScaffoldSpec, benchmark, ranking objective or resource ceiling.

## Validation Isolation

The complete historical/M0.9B suite runs with its assertions unchanged. Its
historical all-split fixtures retain the synthetic parameters 7..11 policy.
Qualification-constructor tests use the frozen constructor's code with recipe
parameters 12..16 and namespaced IDs, never the real Qualification48 cases.

A scoped file guard denies parsing the actual qualification payload. It permits
only the frozen provenance function's direct checksum read. Frozen artifacts are
also streamed for mandated SHA256 validation, without loading their task content.

Eight additional operational tests cover credential metadata, rotation
attestation, secret-disclosure rejection, streaming hashes, qualification
non-parsing and the provenance-only exception. No real credential is used in
these tests. Before export, all artifact bytes are checked against environment
credential values transiently; those values are neither logged nor exported.

## Evidence Commands

Run from the repository using its existing virtual environment. Each output
directory is write-once; failed validation evidence is retained.

```powershell
.\.venv\Scripts\python.exe -B scripts/m09c.py verify --output .local/m09c/preflight-freeze.json
.\.venv\Scripts\python.exe -B scripts/m09c.py validate --output .local/m09c/pre-validation-confirmed
.\.venv\Scripts\python.exe -B scripts/m09c.py record-blocked-admission --output .local/m09c/admission
.\.venv\Scripts\python.exe -B scripts/m09c.py validate --output .local/m09c/post-validation
.\.venv\Scripts\python.exe -B scripts/m09c.py finalize-blocked --output docs/research-records/m09c
```

The final packaging command is specific to this recorded campaign attempt. It
expects the first failed harness attempt at `.local/m09c/pre-validation`, as well
as the subsequent passing preflight and postflight receipts. It is not a generic
live campaign admission service or a command to replay a new experiment.

## Outcome A Records

`docs/research-records/m09c/REPORT.md` distinguishes operational admission failure
from model/scaffold performance. The evidence includes a metadata-only admission
SQLite ledger, its backup-API export, byte-stable decision replay, checksums,
test logs and an export bundle. An optimization database, inference receipts and
finalist artifact are not fabricated when no optimization campaign was started.

The recorded Outcome A is terminal. Meeting missing admission requirements later
does not resume its closed search or authorize qualification automatically.
