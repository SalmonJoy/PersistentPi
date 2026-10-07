> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.9C-R Admission Revalidation

Final state: **BLOCKED**. The operational admission probe remains unused.
No Planner search, Runner research inference, qualification execution, final
evaluation or hidden scoring occurred. This is an additive revalidation, not a
rewrite of the historical M0.9C or M0.9C-R outcome.

Starting commit: `bbae363c84afb702ca5018f65012d31140502297`.
Historical M0.9C commit: `ae2267768c9e4301681cda474c09b231b0ddd268`;
tag: `m0.9c`. Protocol remains `0.6`.


[Private task-level/operational evidence retained in the research repository.]

## Admission Decision

Unmet prerequisites:

- `newly_rotated_environment_credential_not_established`
- `bounded_probe_allowance_not_established`

The existing checker returned BLOCKED; SQLite replay reproduced that result with
integrity `ok` and zero probe rows. Neither READY_FOR_ADMISSION_PROBE nor ADMITTED
is justified. A probe is unnecessary to establish this prerequisite stop and is
not permitted while these prerequisites remain unmet.

Requested alias: `gpt-oss:120b-cloud`. Intended provider: Ollama Cloud.
Intended generation endpoint: `https://ollama.com/api/chat`.
Frozen adapter version: `m09cr-admission-1`.
Direct API identifier, catalog/tag identity, digest and version were not resolved
or frozen during this revalidation because admission prerequisites failed before
the authenticated model-resolution stage. No historical digest was substituted.
No claim of immutable cloud backend weights is made.

Thinking remains intended `high`; temperature remains `0`; seed remains `42` only
if supported. Support is not established. Model-specific temperature, output-cap,
thinking, usage and termination contracts remain unresolved; generic account
authentication is not evidence of model-specific behavior.

## Execution And Accounting

Probe needed for this prerequisite decision: **no**. Probe sent: **no**.
Probe HTTP status, response size, latency, thinking/final response, done reason,
prompt/evaluation/cache counts and operational token cost: **not applicable**.
No missing counts or reasoning tokens were estimated. Purchased credits consumed:
**0**. Proposal requests/tokens: **0/0**; Runner research calls: **0**.

If a future authorized admission can pass all prerequisites, accounting remains
`provider_accounted_tokens = prompt_eval_count + eval_count`, with cached input
recorded separately, never added again. The eight proposal slots and 200,000-token
proposal ceiling remain untouched. No probe reservation was created and no
single-use opportunity was consumed.

The offline `admission/admission.json` records zero authentication requests made
by its status command. The separate `credential-safety.json` records the two
explicit non-generating authentication checks performed beforehand. These scopes
must not be conflated. Previous key-validation requests are not repeated model
probes or research inference.

An initial offline helper import failed before loading the dotenv key or making
network requests. Its import-path ordering was corrected in the ephemeral command;
no frozen source or transport was changed and no inference retry occurred.


[Private task-level/operational evidence retained in the research repository.]
