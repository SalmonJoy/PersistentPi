# M0.9C-L2: Account Evidence Correction

Protocol 0.6 and every scientific condition remain unchanged. This is a new
implementation milestone, not an amendment of historical outcomes. The old
M0.9C-L freeze and the `50697cd` preflight-stop record remain intact.

## Independent Evidence

`AccountEvidence` establishes Pro, sufficient included credits, zero additional
balance, reload Off, provenance and freshness from an approved signed-in usage
observation. `ApiEvidence` establishes the admitted mapping and current accepted
authenticated metadata route, combined with the anchored R2 neutral probe for
request/response/thinking/usage compatibility. Neither evidence class substitutes
for the other. HTTP 200 alone is insufficient for admission.

The live native transport no longer requires any subscription-tier field in its
API responses. It retains the existing non-generating authentication route
`POST /api/me`, records only its status and a bounded optional `plan` projection,
and ignores unrelated/unknown fields without persisting user identifiers.
This route is an operational authentication check, not a documented billing API.
The prior successful keyed probe establishes authentication/access historically;
fresh metadata acceptance does not re-prove generation behavior or backend weights.
No new probe is permitted. Actual future responses must still contain valid
provider token counts, exact identity and completion fields; missing usage fails.

[Authentication](https://docs.ollama.com/api/authentication),
[cloud](https://docs.ollama.com/cloud),
[usage](https://docs.ollama.com/api/usage) and
[model listing](https://docs.ollama.com/api/tags) document key authentication,
catalog names and counters. None of these contracts defines a mandatory `plan`
response field. This is not a claim that all undocumented fields are forbidden.

## Approved Account Artifact

`configs/m09cl2-account-schema.json` defines the positive field allowlist and
observation hash. No keys, cookies, payment data or account identifiers belong in
the artifact. Credential values are checked privately before persistence.
Pro/balance/reload evidence comes from `https://ollama.com/settings`, independently
of `/api/me`. The signed-in observation and current operator attestation are
trusted operational inputs; the API is not used to infer an API/UI account match.
Concurrent external account spending remains a risk; exhaustion stops without
retry or paid fallback. The key is the same rotated credential used at admission.

The previous launcher required a fresh timestamp but did not implement a numeric
expiry. L2 makes that existing freshness requirement enforceable: at most 24 hours
old, timezone-aware UTC-comparable time, at most five minutes ahead of the clock.
Refresh immediately before the real preflight/search; 24 hours is a rejection
ceiling, not a recommendation to reuse old evidence. This operational safeguard
does not change model/search/task conditions.

Allowance retains the conservative original formula: 200,000 proposal tokens at
the highest authoritative GPT-OSS rate, with the original unused probe reserve
also retained as headroom. At USD0.60/million this is USD0.12 for proposals; no
budget increase is permitted. Pricing must equal the anchored authoritative R2
record. The historical 127-token probe is not counted as a proposal and is not
repeated. Its calculated USD0.000038548 charge is not an observed account debit.

## Freeze And Commands

New freeze: `docs/research-records/m09cl2/launcher-freeze.json`. It covers the
new evidence schema/validator, live launcher sources, unchanged adapter/renderer,
usage parser, phase graph, barriers, complete validation and synthetic replay.
Previous launcher/stop artifacts are anchored to `50697cd` and checked unchanged.
The research database remains empty; synthetic tests are not research results.

```powershell
.\.venv\Scripts\python.exe -B scripts\m09cl2.py validate --output .local\m09cl2\validation
.\.venv\Scripts\python.exe -B scripts\m09cl2.py freeze --output .local\m09cl2\validation
.\.venv\Scripts\python.exe -B scripts\m09cl2.py verify
.\.venv\Scripts\python.exe -B scripts\m09cl.py search-preflight --account-evidence .local\m09c-live\account-current.json --output .local\m09cl2\preflight.json
```

Preflight persists independent evidence or a secret-free blocking condition;
failure never authorizes a repair/retry or generation. No proposal slot is used.

The following command is for separately authorized future use. **Do not execute
it in M0.9C-L2**, even if preflight is ready:

```powershell
.\.venv\Scripts\python.exe -B scripts\m09cl.py search-live --account-evidence .local\m09c-live\account-current.json --authorize-primary-search
```

Search32 execution, qualification, final evaluation and hidden scoring remain
prohibited for this milestone. No Planner or Runner inference is authorized.
