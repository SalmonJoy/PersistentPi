# M0.9C-L: Admission-Bound Search-Only Launcher

Protocol remains 0.6. This is an additive implementation milestone, not a new
scientific condition or a research campaign. Historical implementations and
evidence remain byte-for-byte unchanged.

## Permission And Identity

The earlier launch stopped because the frozen manager/executor rejected live
adapters, the renderer emitted the historical GLM model, and the manager's
successful-search path proceeded directly to qualification.

The new launcher requires explicit SEARCH_ONLY authorization, an anchored
ADMITTED M0.9C-R2 record, its exact resolved scientific configuration, and the
new launcher freeze. Admission artifacts, prices, rotation attestation and
parent preregistration are anchored to commit 0ceb6ea. There is no CLI model,
provider, adapter, arbitrary patch or qualification-continuation option.

The direct API identifier, endpoint and supported parameter mapping come from
the admitted identity. Observable cloud identity is checked before each new
proposal is constructed; it does not prove immutable cloud weights. The frozen
laptop Runner is checked non-generatively during preflight and before each
Runner call. No fallback, SDK retry or extra admission probe exists.

The parent configuration's historical offline-only/authorization fields are
preserved as historical fields. Only the separately frozen operational_launch
record grants the new narrow capability. Validation configurations cannot use a
network transport, and real configurations cannot accept a test transport.

## Search Boundary

Legal phases: references -> search -> finished, or any active phase -> stopped.
Finished and stopped cannot reopen. Search termination is one of:

- SEARCH_STOPPED
- SEARCH_COMPLETE_NO_FINALIST
- SEARCH_COMPLETE_FINALIST_FROZEN

SearchAccess exposes only Search32, Screen8 and Remaining24. Qualification is
an identity-only manifest; its task material is not loaded, stored as members,
or supplied to an executor. Non-search evaluation/result requests are denied.
There is no final/hidden loader or scoring capability. Exit persists a barrier
asserting zero qualification, final and hidden executions. A later qualification
launcher requires separate implementation and authorization.

The historical reference definitions, compiler/catalog, disclosure projector,
screen selection, full-score union, ranking, gates and resource reservations
are reused. Screen8 receipts are reused, never rerun to form the full score.
Only complete, identical Search32 results enter the full archive.

## Minimal Kernel Changes

New modules preserve the historical kernel rather than modifying frozen files.
The candidate executor's copied evaluation method differs only at the admitted
backend permission/usage-kind check and the enforced remaining-time deadline. An AST
parity test and an executable synthetic edit/verify test cover that distinction.
The copied proposal method changes only request/permission binding and native
provenance accounting; scheduling, validation, deduplication and selection use
the existing methods. There is no generated code execution or dynamic rewrite.

## Accounting And Recovery

Every proposal slot is reserved durably, then marked started before the single
transport send. Sent malformed, invalid and duplicate proposals consume slots.
Unresolved sends and started windows stop, never automatically retry. Only
durably unstarted work can resume with the exact campaign/configuration/source
identity. Reservations and cumulative costs are not reset on resume.

Planner tokens = prompt_eval_count + eval_count. Cached prompt count is separate
and is not added twice. Thinking content is retained separately; unavailable
reasoning-token counts remain unknown. Provider-token/published-rate credit
calculations are distinguished from observed account debits. The earlier
127-token admission probe is not part of the research ledger.

The original 8-request/200,000-Planner-token, Runner, wall and qualification
reservation limits remain unchanged. The <9h/<4.5M-Runner-token forecast is
rechecked from frozen development measurements. Already purchased Pro access
and included allowance are preserved; additional purchased credits, automatic
reload, top-ups and fallback remain prohibited.

Preflight requires fresh operator-provided authoritative signed-in account
evidence, included balance sufficiency, reload off, additional balance zero,
and the admitted authoritative pricing record. API plan and cloud identity are
checked non-generatively. Operator evidence is not an automated measurement of
the billing UI; concurrent unrelated account consumption remains an operational
risk. Exhaustion/errors stop without retry or paid fallback.

The credential is loaded privately from <private-workspace> never put
into os.environ, persisted requests/artifacts or Runner context. It is used only
in the in-memory authentication header. Native transport errors
suppress diagnostic payloads; redaction and disclosure canaries are tested.

An exclusive process lock prevents concurrent launches. Recover-lock can remove
a stale lock only when the recorded owner PID is provably absent; PID reuse or
inability to prove absence blocks recovery. This never edits the experiment
ledger. STOP under .local/m09c-live/state is honored by the trusted runtime.

## Commands

These commands are available but were NOT executed for a research campaign.
The dry run uses only synthetic protocol-level observations and sends nothing.

```powershell
.\.venv\Scripts\python.exe -B scripts\m09cl.py request-dry-run --output .local\m09c-live\request-dry-run.json
.\.venv\Scripts\python.exe -B scripts\m09cl.py search-preflight --account-evidence .local\m09c-live\account-current.json --output .local\m09c-live\preflight.json
.\.venv\Scripts\python.exe -B scripts\m09cl.py search-live --account-evidence .local\m09c-live\account-current.json --authorize-primary-search
```

Account evidence must contain plan=Pro, authoritative=true,
auto_reload_enabled=false, additional_balance_zero=true,
current_operator_attestation=true, observed_at, source,
api_ui_account_match=true,
included_balance_lower_bound_usd (a decimal string), and pricing equal to the
anchored docs/research-records/m09cr2/pricing-observation.json. No credential or
account identifier belongs in this file. Missing evidence blocks launch.

For authorized recovery, use --resume-campaign-id with the existing identity;
--resume-idle-pause only resumes a recorded planned pause. Neither can cross
the search terminal boundary. Recover-lock is non-generating. An indeterminate
campaign remains stopped even after its process lock is recovered.

## Offline Validation

```powershell
.\.venv\Scripts\python.exe -B scripts\m09cl_tests.py --output .local\m09cl\launcher-validation-fresh
.\.venv\Scripts\python.exe -B scripts\m09cr2.py validate --output .local\m09cl\historical-validation-fresh
```

The new tests use namespaced synthetic tasks and the real admitted adapter,
with injected non-network transports. Historical tests replace benchmark
generators with existing synthetic fixtures, deny real prepared artifacts,
and use temporary synthetic repositories for operational checks. Qualification
fixtures are not the frozen Qualification48 cohort. No actual Search32
reference results, qualification results or research Planner proposals exist.
