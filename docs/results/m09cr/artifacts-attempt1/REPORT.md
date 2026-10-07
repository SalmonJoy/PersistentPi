> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.9C-R Admission Result

Final state: **BLOCKED**. No operational probe was transmitted. No optimization
campaign was created. Credential rotation and private environment delivery are
not established. The supplied chat credential was not used for authentication.

Parent commit: `ae2267768c9e4301681cda474c09b231b0ddd268`. Historical tag: `m0.9c`. Historical Outcome A and
all historical tracked files remain unchanged. Protocol: `0.6`.

Amendment hash: `f937358618a1af4c70b8e44855bb7cb9bd67a5d59c24ecc3e22db77c0f0b6b7d`.
Parent configuration hash: `b2519429efa4a90f82763ebd98c3075ed42a36d8b6815a634fb373fc46fd927a`.
Resolved configuration hash: `2ecdf403f7ec16a7419ff215cb513b3fb16832e7791bb4e3e84ec7a18fbccf6f`.

Tests passed: **540** (487 existing,
53 amendment tests). Live networking was disabled
during historical tests; amendment tests used only synthetic transports/account
evidence/credentials and temporary SQLite databases.

## Admission Evidence

Requested Planner alias: `gpt-oss:120b-cloud`, provider Ollama Cloud.
Direct API identifier, catalog/digest/version and live adapter mapping: **not
authenticated/frozen** because the credential gate failed. Planned endpoint:
`https://ollama.com/api/chat`; implemented adapter: `m09cr-admission-1`.
Thinking: intended `high`; temperature: `0`; seed: requested `42`, support not
established. No immutable backend-weight claim is made.

Credential metadata: dedicated environment key present
`False`; rotation attested
`False`. No credential value is retained.

[Private account observation retained privately.]

Unmet prerequisites:
- newly_rotated_environment_credential_not_established
- bounded_probe_allowance_not_established

API parameter/usage/termination contracts remain unresolved. No auth request
using the temporary API credential was sent. No probe was needed to reach this
prerequisite stop; its one opportunity remains unconsumed.

## Accounting And Integrity

Probe transmissions: **0**. Probe token usage: not applicable.
Planner proposals: **0**, proposal tokens: **0**, Runner research calls: **0**.
Qualification execution/content access: **0/false**. Final access and hidden
scoring: **false**. Purchased credits consumed by this task: **0**.

The provider-accounting adapter uses exactly `prompt_eval_count + eval_count`;
cached input is stored separately and thinking content is retained only as
provenance. A separate reasoning-token count is neither required nor estimated.
The original eight-proposal/200000-token ceilings and all other scientific
conditions are unchanged. Probe provenance is excluded from future search.

SQLite integrity is `ok`. Its backup-API export replays the BLOCKED decision
without inference. Source freezes, raw/canonical configuration hashes, test logs,
integrity audit and export bundle are provided. Exports and new source files are
checked for credential values and credential-shaped strings before packaging.

## Reproduce And Audit

From the repository, with its existing virtual environment:


[Source-bearing example or private reproduction procedure withheld.]


The last command identifies the final evidence commit containing this report.
Full offline tests can be reproduced with `scripts/m09cr.py validate --output`
and a fresh output directory. No search/probe launch is exposed by that command.
