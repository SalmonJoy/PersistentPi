# M0.10A/1 - Same-Planner Interface Feasibility Study

Status: final revised preregistration; planning only. This revision makes only
the four requested methodological corrections. It authorizes no implementation,
capability probe, Planner inference, Runner call, or scaffold-search launch.
Existing implementation work and historical artifacts are not modified.

## 1. Question and Historical Boundary

Can the same admitted GPT-OSS 120B Planner express legal scaffold-search decisions
reliably when mechanical ScaffoldSpec construction is externalized?

This measures Planner-to-search-space acquisition, not Runner performance,
optimization efficacy, scenario comprehension, or benchmark correctness.

The immutable M0.9C primary result remains:

> 0/8 valid GPT-OSS 120B proposals under the preregistered
> Planner-to-ScaffoldSpec contract; no generated scaffold reached Runner evaluation.

Its forensic classification remains two empty final answers, two truncated JSON
documents, three invalid category lists, and one wrong field type. Syntax-only
cleanup recovered zero valid proposals. This study does not repair, relabel, or
supersede those historical outcomes.

Search32 is neither inspected nor executed. Qualification48, Final96, hidden
tests, reference solutions, expected outputs, and source-bearing historical
Runner traces remain unavailable. There are exactly zero Runner research calls.
Generated proposals are validated as data but never executed against a task.
No cross-task memory, generated tools, Planner model substitution, or Pi work.

## 2. Frozen Planner and Transport

| Field | Preserved condition |
| --- | --- |
| CLI/app alias | `gpt-oss:120b-cloud` |
| Direct API model | `gpt-oss:120b` |
| Endpoint | `https://ollama.com/api/chat` |
| Sampling | `temperature=0` |
| Thinking | `think="high"` |
| Generation ceiling | `num_predict=4096` in every arm and the operational probe |
| Streaming | `stream=false` |
| Seed | Omit unless already authoritatively supported under the admitted contract; do not introduce a new sampling condition |
| Request cap | 16,384 canonical UTF-8 bytes |
| Response/submission cap | 65,536 bytes each |
| Request timeout | 180 seconds |

Retain the admitted endpoint/account/adapter identity contract. Freeze API
identifier, alias, catalog/tag identity, available digest/version metadata,
endpoint, and adapter mapping from authoritative metadata. These are observable
cloud provenance, not proof of immutable backend weights. Do not treat a
previous catalog digest as an independently authoritative immutable weight ID.
Identity or provider-contract drift blocks admission or stops a running study.

No `format`, `response_format`, JSON-schema response enforcement, forced tool
choice, undocumented provider option, or local-to-cloud capability assumption.
Native function parameter schemas in F2 describe arguments; they are not an
assumption of cloud Structured Outputs enforcement.

## 3. Immutable Contracts and Parents

Historical protocol `0.6`, `ScaffoldSpecV1`, `scaffold-compiler-1`,
`scaffold-renderer-1`, and the historical interface catalog remain unchanged.
The authoritative F0 contract is the completed M0.9 implementation, not a new
stricter approximation. Its relevant source anchors are:

| Historical file | SHA-256 |
| --- | --- |
| `src/persistentpi/m09/spec.py` | `f12c7fb774a0a4dbf4ae753c94907f00f2eb30654bb488df751bda694233dd7d` |
| `src/persistentpi/m09/manager.py` | `d70d5a328c00339acca1cb9d64aef5dee700262437a3c606e944e21e138fb434` |
| `src/persistentpi/m09/disclosure.py` | `d5cc1787715281f79a6d2b790723ebd506d67f0562135e518a658f3c37e88a70` |
| `src/persistentpi/interfaces.py` | `0e886cb4599b4aab4637a222bc34516430c921c440704b65407a632423f672ed` |

Freeze normalized B0/B1 parent specifications, parent IDs, specification hashes,
catalog hash, compiler/renderer identity, and protocol before feasibility.

| Parent | Historical behavioral scaffold ID |
| --- | --- |
| B0 / E0 | `3523ba5db8fee37ed9465947970b20ef61a336ee08527c3c9abdf9cda2cf8413` |
| B1 / E1 | `816fe91c71baad3187fa4168f2d5f450c512a14477843d642f0d435992476640` |

The scenario's supplied parent is the only permitted acquisition parent for
that scenario. The operational F2 probe uses a literal all-zero placeholder
parent instead and is never compiled as a research proposal.

## 4. Interface Arms

### F0 - Historical Full-Spec Interface

Use the original M0.9 Planner system prompt, historical user shape
`parent / observation / archive / remaining / contract`, unchanged
`proposal_contract()`, strict duplicate-key JSON parser, `parse_proposal()`,
historical category normalization, ScaffoldSpec defaults, validator, and compiler.
Do not simplify the prompt, repair content, inherit omitted scaffold fields from
the parent, or require fields that the historical parser did not require.

Root required keys are `parents`, `scaffold`, `mutation`, `rationale`, and
`targeted_categories`; only `predicted_metrics` is optional. Unknown keys fail.
`parents` is a list of one or two unique allowed parent IDs; scenario-local parent
authorization still applies. `mutation` and `rationale` are strings of at most
1,024 UTF-8 bytes each. Categories must belong to the historical catalog;
historical sorting/deduplication and empty-list behavior are retained. Optional
predictions may contain only `public_passes`, `formations`, `runner_tokens`, and
`runner_calls`, with historical numeric-type handling.

Within `scaffold`, `system_text` is required. All other omitted fields receive
the historical ScaffoldSpec defaults, not parent inheritance. Those defaults are
E0 schema-JSON interface, empty tool descriptions, context order
`budget/control/observations/task/tools`, no source preload, C3, read allowance 2,
four recent observations, generic rejection feedback, stop retry, stagnation 0,
15 calls per phase, 512 output tokens per phase, and version 1.

Historical source definitions above are authoritative for exact bytes and edge
cases. Future offline parity must replay the eight saved historical final answers
without repair and reproduce their first rejection classes.

### F1 - MutationProposalV1 and Deterministic Expansion

Final content must be exactly one strict JSON object. No fences, prose extraction,
duplicate-key tolerance, coercion, aliases, repair, or additional model turn.

The closed root requires exactly:

```json
{
  "parent_id": "<64 lowercase hexadecimal characters>",
  "mutations": [{"field": "<allowed field>", "value": "<field-specific value>"}],
  "target_failures": ["<allowed category>"]
}
```

Only optional root key: `rationale`, a string of at most 256 UTF-8 bytes.
`mutations` contains 1-15 closed `{field, value}` objects. Each field appears at
most once, including operations with equal values. No executable operation,
nested path, field alias, or immutable-field mutation. `target_failures` contains
1-11 unique exact catalog strings:

`NO_OP`, `PATCH_MISMATCH`, `INVALID_SYNTAX`, `MALFORMED`, `UNAUTHORIZED`,
`OUTPUT_LIMIT`, `BUDGET`, `GIVE_UP`, `PUBLIC_FAIL`, `PUBLIC_PASS`, `OTHER`.

The semantic schema has a discriminated `oneOf` branch for each of the following
15 fields. JSON integers must be integers, not booleans or coerced strings.

| Mutable field | Exact domain |
| --- | --- |
| `system_text` | ASCII, NUL-free string; shared authored-text constraints below |
| `interface` | `E0` or `E1`, followed by `:` and one of `runner-dsl-1`, `runner-json-1`, `runner-json-schema-1` |
| `tool_descriptions` | Closed string-valued map with keys drawn from `read_file`, `edit_file`, `replace_file`, `finish` |
| `context_fields` | Unique ordered list from `task`, `tools`, `budget`, `control`, `observations`, `source`, `public_cases`; first four names mandatory |
| `source_preload` | Boolean |
| `controller` | `C0`, `C1`, `C2`, `C3` |
| `read_allowance` | Integer 0, 1, or 2 |
| `recent_observations` | Integer 0-4 |
| `rejection_feedback` | `generic` or `precise` |
| `retry` | `stop` or `retry` |
| `stagnation` | Integer 0, 2, or 3 |
| `inspect_calls` | Integer 1-15 |
| `act_calls` | Integer 1-15 |
| `inspect_output` | Integer 128, 256, 512, or 1024 |
| `act_output` | Integer 128, 256, 512, or 1024 |

`version=1` is immutable. Read allowance zero requires source preload true.
Combined system text and tool-description text must remain ASCII, NUL-free,
at most 4,096 bytes, and pass all historical prohibited-payload checks.
Historical global resource ceilings are not enlarged by phase allocations.
Controller meanings are unchanged: C0 autonomous bounded action selection;
C1 redundant-visible-read rejection; C2 successful-read gating; C3 INSPECT-to-ACT.

The trusted compiler performs exact parent lookup, deep copy, exact whole-field
replacements, combined-state validation, frozen ScaffoldSpec validation, frozen
compilation, canonical serialization, and historical behavioral hashing. It
neither selects alternatives nor repairs dependent constraints, clips numbers,
maps categories, rewrites text, or inserts new defaults. Distinct-field operations
are order-independent. A valid unchanged/duplicate result still counts as a valid
acquisition and is separately flagged as a duplicate.

### F2 - Native Tool Submission

F2 uses the identical MutationProposalV1 semantic schema and deterministic
compiler as F1. Generate its parameter schema from the shared definition, not a
second independently maintained vocabulary. Expose exactly one function:

```text
type: function
name: submit_scaffold_mutation
description: Submit one scaffold mutation proposal for deterministic validation.
parameters: the closed MutationProposalV1 schema, including all 15 oneOf branches
```

Accept exactly one native tool call with that name and object-valued arguments.
Reject zero/multiple/duplicate calls, other names, stringified arguments,
unknown/missing fields, illegal values, prose-only and reasoning-only submissions.
Accompanying text is provenance only, never an alternative submission. No tool
execution, tool-result message, second turn, repair call, or automatic retry.

## 5. Exact F1/F2 Prompt Contract

Common system text, unchanged:

```text
You optimize a frozen small coding Runner using protocol metrics only. Choose a legal scaffold mutation using the supplied parent and contract. Select semantic changes yourself. The trusted compiler copies the parent and replaces exactly the declared fields; it does not choose settings or repair proposals. Propose general scaffold changes, never task answers, lookup tables, executable programs, protected-component changes, or resource-ceiling changes. Unlisted keys and field aliases are forbidden.
```

Append one space and the appropriate suffix:

```text
F1: Return exactly one JSON MutationProposal in final content. No fences or surrounding prose.
F2: Submit exactly one submit_scaffold_mutation tool call with MutationProposal arguments. Do not invoke another tool or request a second turn.
```

Both receive canonical JSON with identical parent, synthetic observation, archive,
and remaining-resource fields. Both receive the same semantic rules. F1 includes
the shared schema in the user contract; F2 supplies that schema as the native
function parameters. No scenario-specific advice, recommended mutations, worked
solutions, source code, task specification, or hidden repair instruction.

F0 receives the unchanged historical system text and `proposal_contract()` in
the same historical-shaped user body. Representation differences are the
interface treatment, not an opportunity to alter observations between arms.

## 6. Synthetic Scenario Construction and Freeze

Exactly 24 scenarios: eight semantic families, three deterministic instances
`j=0,1,2` each. No real benchmark content or trace is used. Generator identity is
`M0.10A-synthetic-v1`.

| Family, in generator order | Formations per four-task bucket | Passes | Base calls | Base failure counts |
| --- | ---: | ---: | ---: | --- |
| `no_op_repetition` | 1 | 0 | 44 | `NO_OP:32` |
| `formation_failure` | 0 | 0 | 40 | `MALFORMED:28` |
| `excessive_read` | 0 | 0 | 44 | `UNAUTHORIZED:32` |
| `context_mismatch` | 1 | 0 | 36 | `PATCH_MISMATCH:24` |
| `syntax_rejection` | 1 | 0 | 36 | `INVALID_SYNTAX:24` |
| `output_truncation` | 0 | 0 | 36 | `OUTPUT_LIMIT:24` |
| `high_cost` | 2 | 1 | 48 | `NO_OP:12` |
| `mixed_failures` | 1 | 0 | 44 | `NO_OP:8`, `PATCH_MISMATCH:8`, `INVALID_SYNTAX:8`, `OUTPUT_LIMIT:8` |

Each observation has eight fictional reporting buckets named
`coupled_conditions`, `boundary_empty`, `initialization_accumulation`,
`early_returns`, `state_machine`, `parsing`, `two_functions`, `duplicates_order`.
These labels carry no task definitions. Every bucket contains four fictional
tasks and uses the same scenario profile. Aggregate counts sum the eight buckets;
formation/passing-family coverage is eight when the corresponding count is
positive and zero otherwise.

Per bucket, calls equal base calls plus `4*j`. Input/output tokens per call are
`320+40*j` and `64+16*j`; high-cost uses `600+50*j` and `192+32*j`. Inference
seconds equal calls times `0.5+0.1*j`; high-cost uses `2+0.25*j`. Wall seconds
equal inference seconds plus `0.1*calls + 0.05*formations`. Times round to three
decimal places. Token totals equal calls times input-plus-output tokens.
These are fictional observation values, not actual Runner expenditure.

Increase the dominant failure count by `2*j`; mixed uses `NO_OP`. Add
`BUDGET=4-formations`, and `PUBLIC_FAIL=formations-passes` if positive. Multiply
counts by eight for aggregate failure counts. Include two safe excerpts selected
by descending aggregate failure count, lexical category tie-break. They contain
only source-omission placeholders, fictional hashes, equality indicators,
lengths, action categories, ACT-to-ACT transitions, rejection categories,
repeat counts `2+j`, and costs. Excessive-read excerpts use READ; others EDIT.
Excerpt index `k=0,1` uses `10+j+k` calls, byte lengths `256+64*j`, and costs
scaled from that scenario's per-call metrics. `result_ok=false`.

All fictional hashes are SHA-256 of canonical JSON tuples beginning with
`M0.10A-synthetic-v1`. Scenario ID is `syn-` plus the first 24 hexadecimal
characters of the hash of `(generator, family, j)`. Excerpt task hash uses
`(generator, family, j, "event", k)`; old/new hashes append `"old"`/`"new"`.
For NO_OP, new hash equals old hash; otherwise the two are distinct.

Parent is B0 when family-index plus `j` is even, otherwise B1: 12 scenarios each.
Archive has the supplied parent and that scenario's fictional aggregate metrics,
with 32 fictional tasks. Historical-shaped `remaining` is fixed at 5,520 Runner
calls, 6,000,000 Runner tokens, eight Planner requests, 200,000 Planner tokens,
368 physical windows, and 43,200 active-wall seconds. These fields are observation
fixtures, not authorization to spend historical budgets.

Use disclosure policy `protocol-only-1`, empty archive decisions, and no source
payloads. Do not send diagnostic scenario family/instance labels as extra hints.
Freeze generator, all scenario IDs/observations/excerpts, parent registry,
family assignments, request renderers, schemas, prompt text, and checksums before
any feasibility inference. No calibration, replacement, or outcome-driven edits.

## 7. Admission and F2 Decision

Admission remains operational, separate from feasibility outcomes. Credential
rotation, secret delivery through environment/secret mechanism, and redaction
checks must pass first. No credential enters requests saved as provenance,
repositories, databases, reports, or exports.

Require admitted identity, authoritative usage/cost accounting, current pricing,
context bound, and funding evidence: Pro included allowance of at least US$2,
zero additional purchased balance, and reload/top-up/upgrade disabled. No model
fallback, extra purchase, adaptive allowance expansion, or provider substitution.
Do not infer entitlement or concurrency from a successful unauthenticated listing.

Offline schema, parser, compiler/security, and request-size validation precede
any operational F2 probe. A request that cannot fit the unchanged 16,384-byte cap
is offline-infeasible; do not shrink the schema or enlarge the cap to admit it.

If required native tool behavior is not established by authenticated metadata,
at most one separately authorized, bounded non-research F2 capability probe may
be used. It has no PersistentPi task, search, qualification, final, hidden, or
reference information. Its literal argument object is:

```json
{"parent_id":"0000000000000000000000000000000000000000000000000000000000000000","mutations":[{"field":"recent_observations","value":1}],"target_failures":["OTHER"]}
```

Probe system text:

```text
Operational capability check. Submit exactly one native submit_scaffold_mutation call with the supplied literal arguments. Do not optimize, execute, or request another turn.
```

User content is canonical JSON of the literal arguments. It uses the same native
tool schema, intended model, temperature, thinking setting, generation ceiling,
request cap, and timeout as above. It is separately accounted, never a feasibility
observation or proposal slot, never shown to later Planner requests, and cannot
be repeated adaptively.

Probe success requires all of:

- `done == true`;
- exactly one correctly named native `submit_scaffold_mutation` call;
- object-valued arguments exactly matching the frozen probe specification;
- a complete, non-truncated response;
- required returned model identity and authoritative usage/accounting fields.

Record `done_reason` exactly as returned. Explicit output-limit or truncation
termination fails even if arguments happen to parse. Literal `done_reason="stop"`
is not required. An unfamiliar reason must be interpreted using documented
provider semantic meaning, recorded with its evidence; do not reject it merely
for being a different string, and do not guess that it means complete. An
unresolved semantic meaning cannot satisfy the completeness requirement.

Freeze the two-arm or three-arm decision before any feasibility outcomes.
Failure confined to required tool behavior excludes F2 before freeze, leaving
F0/F1 if all common prerequisites pass. Missing identity/account/funding/accounting
or an unresolvable sent probe blocks launch, not just F2. No result-driven arm
change or replacement interface.

Finally, authenticated launch admission must establish capacity for the frozen
arm count: two concurrent requests for F0/F1 or three for F0/F1/F2. Insufficient
capacity blocks launch; it does not authorize serialization or removal of an
otherwise admitted arm to accommodate capacity.

## 8. Paired Temporal-Block Schedule

Start with the 24 lexical scenario IDs. Shuffle this list exactly once using
`random.Random(42)` under the frozen Python version. Persist the exact order,
Python version, and schedule hash before launch. Do not shuffle a global list of
arm/scenario pairs or dispatch waves spanning different scenarios.

For each scenario in that fixed order:

1. Construct all admitted-arm requests from the identical frozen scenario state,
   without consuming a sibling response or incorporating previous observations.
2. Atomically reserve the whole block's resources and persist all independent
   request identities before any send.
3. Issue F0/F1 concurrently, or F0/F1/F2 concurrently when all three are admitted.
4. Wait until every started request reaches its permitted terminal/receipt state
   before dispatching the next scenario block.

Completion order must not affect assignment, prompts, classification, later
requests, or arm inclusion. A fast failure cannot silently replace, adapt, or
resend an unsent sibling. STOP prevents new dispatch; already-started siblings
may finish and have their receipts captured. An unresolved receipt blocks
subsequent scenarios rather than permitting overlapping blocks.

One request per scenario/arm, with no repair, retry, resampling, second turn,
rate-limit replacement, or compensation for missing observations. All original
durable receipt, timeout, accounting, STOP, and recovery rules apply unchanged.
Latency is reported under concurrency two or three; total study wall time is
separate from the sum of request latencies.

## 9. Acquisition and Security Classification

Record these stages for each response:

1. Provider response received.
2. Intended complete/non-truncated output or native submission present.
3. Transport representation parseable.
4. Interface structure and field types valid.
5. Semantic operation/category vocabulary valid.
6. Parent valid.
7. Deterministic construction succeeds.
8. Resulting ScaffoldSpecV1 validates.
9. Frozen compiler accepts.
10. Behavioral duplicate/unique classification.

`acquired_valid_proposal` means stages 1-9 all pass. Duplicates remain valid
acquisitions. Retain the first physical/parser failure separately; logical stage
reporting must not change F0's historical first-rejection ordering.

Explicit truncation fails stage 2 even when partial output is parseable. Empty
final answers do not become successes by extracting thinking. No syntax cleanup,
human repair, category mapping outside F0's existing normalization, or forensic
counterfactual is used in primary validity labels. Any optional post-primary
forensic analysis remains explicitly separate.

Record actual protected-boundary breaches separately from prohibited submission
field leakage and historical prohibited-payload violations. Frozen prohibited
keys/operation fields are `code`, `script`, `command`, `exec`, `eval`, `task_id`,
`task_lookup`, `reference_solution`, `hidden_tests`, `evaluator`, `logger`,
`supervisor`, `resource_limits`, `model`. These are not allowed mutation fields.
Ordinary explanatory prose mentioning a concept is not executable-field leakage.
Systematic leakage means such prohibited submission-key/mutation-field leakage
in at least two responses of the same arm. Any actual protected-boundary breach
is disqualifying independently of this recurrence threshold.

## 10. Endpoints: Readiness Is Not Comparative Improvement

For every admitted arm A, independently:

```text
INTERFACE_READY(A) =
    acquired_valid_count(A) >= 20 out of 24
    AND at least one valid acquisition in each of the eight semantic families
    AND all compiler/security invariants pass
    AND no protected-boundary breach
    AND no systematic prohibited-field leakage
```

F0, F1, and conditional F2 are all eligible for this classification. Readiness
has no F0-superiority requirement and no comparison p-value requirement.

Separately, for F1 versus F0 and, if admitted, F2 versus F0:

```text
INTERFACE_MEDIATED_IMPROVEMENT(A, F0) =
    acquired_valid_count(A) - acquired_valid_count(F0) >= 6
    AND applicable paired family-cluster bootstrap progression CI lower bound > 0
```

Six net additional acquisitions equal a 25-percentage-point material effect.
Use the 95% progression interval in a two-arm study and the preserved 97.5%
progression intervals for both F0 comparisons in a three-arm study. Report
ordinary 95% intervals in all cases. This improvement classification is distinct
from operational readiness; neither label alone authorizes scaffold search.

| Observed classification | Interpretation |
| --- | --- |
| F0 ready | The original contract is operationally usable in these synthetic conditions. Report variability relative to historical 0/8, without erasing that result. |
| F1 ready, no material F0 improvement | F1 is operationally usable, but the preregistered comparative evidence for interface-mediated improvement is not established. This is not failure of readiness or evidence of equivalence. |
| F1 ready and material F0 improvement | F1 is operationally usable and provides evidence that externalizing construction improves acquisition over F0 in this study. It merits a separately authorized search study, not a Runner-capability claim. |
| No interface ready | None meets the frozen operational gate. Preserve failure-stage evidence; do not lower the threshold or infer that all possible interfaces must fail. |
| Material improvement but not ready | Relative improvement is possible without adequate reliability/security. Record both labels; do not treat this as an operationally ready interface. |

Apply the analogous interpretations to F2 if admitted. Failure to satisfy the
comparative rule may reflect small effects or uncertainty, not demonstrated
equivalence. No readiness/improvement classification is issued for an incomplete
campaign; report valid, invalid, and unobserved separately.

## 11. Paired Analysis

Let `Y[A,i]` be 1 for an acquired-valid proposal and 0 otherwise on paired scenario
`i`. For a complete arm, primary rate is `sum_i(Y[A,i])/24`. Report raw counts,
per-family counts, paired discordant counts, and effect sizes.

For each A versus F0 comparison, the effect is exactly:

```text
T_obs = (1/24) * sum_i (Y[A,i] - Y[F0,i])
```

### Family-Cluster Bootstrap

Resample eight whole semantic families with replacement, retaining all three
paired instances and both arm outcomes for each sampled family. Use 100,000
replicates, seed `20261010`, the frozen Python version, percentile intervals, and
nearest-rank quantiles. Report 95% CI from quantiles 0.025/0.975. In a three-arm
study, progression uses 97.5% CI from quantiles 0.0125/0.9875 for both F0
comparisons. Every replicate recomputes the same 24-observation mean difference.
Retain complete resampling provenance, including deterministic family order.

These quantify uncertainty across the synthetic family clusters, not general
benchmark performance. Eight clusters limit precision. Degenerate intervals
must be reported as such, not treated as proof of broad generalization.

### Exact Family-Level Permutation Statistic

Enumerate all `2^8 = 256` family-level label assignments. For each selected
semantic family, swap A and F0 jointly for all three instances. For each
assignment compute the same 24-scenario mean difference `T_perm`.

```text
p = count(abs(T_perm) >= abs(T_obs)) / 256
```

Include equality/ties. This is complete enumeration: no Monte-Carlo `+1`
correction. Distinct assignments may yield equal statistics and each still
counts. Report all assignments or their reproducible enumeration and tail count.

With F0/F1 only, this is the sole inferential comparison. With F2 admitted,
retain Holm adjustment across exactly F1-versus-F0 and F2-versus-F0. Sort the two
p-values; adjusted smaller is `min(1,2*p_small)`, adjusted larger is
`min(1,max(2*p_small,p_large))`. F2-versus-F1 remains descriptive only.
P-values supplement effect sizes and intervals; they do not add an undeclared
readiness or improvement gate. Family swaps provide a cluster-aware paired
comparison under the label-exchangeability null, not a claim that interface
assignment itself was randomized.

## 12. Secondary Metrics and Interpretation Limits

Per arm, report non-empty completion, truncation, representation parse,
interface-schema validity, category validity, field-type validity, illegal
settings, ScaffoldSpec validation, compiler acceptance, and duplicate rates.
Show explicit denominators and not-assessable downstream stages after an earlier
failure; do not turn missing stages into observed successes.

Record prompt/evaluation/cached token counts, provider-accounted tokens, request
latency, thinking/final/tool-argument UTF-8 lengths, authoritative included-credit
charge or charge calculation, and cost per valid proposal. If no valid proposals,
cost per valid proposal is undefined, not zero.

Report unique behavioral scaffold hashes, parent duplicates, B0/B1 reference
duplicates, cross-response duplicates, mutation-field frequencies, and number
of changed fields. These are descriptive, not an additional search-readiness
threshold and not evidence the Planner understood the scenario or selected a
better Runner scaffold.

## 13. Requests, Tokens, Cost, and Time

| Ledger | Request ceiling | Provider-token ceiling |
| --- | ---: | ---: |
| F0/F1 feasibility | 48 | 6,488,064 |
| F0/F1/F2 feasibility | 72 | 9,732,096 |
| Separate operational F2 probe, if needed | 1 | 135,168 |

Reserve at most 131,072 prompt tokens plus 4,096 generation tokens per request.
Both request and token ceilings apply; no adaptive extra requests. Feasibility
wall ceiling remains three hours; operational admission remains ten minutes.
Request timeout remains 180 seconds. Historical M0.9C eight-request/200k-token
budgets are not transferred, reused, or expanded.

```text
provider_accounted_tokens = prompt_eval_count + eval_count
```

Record `prompt_eval_cached_count` separately; it is already part of prompt count
and must not be added again. Preserve thinking content for provenance, but do
not infer a separate reasoning-token count or call thinking bytes reasoning
tokens. Use provider-exposed authoritative fields; missing mandatory accounting
blocks/stops execution rather than being silently estimated.

US$2 combined included-credit ceiling covers feasibility plus any operational
probe. Maintain separate ledgers and show the combined exposure. No purchased
additional credits, reload, top-up, subscription upgrade, budget expansion, or
model fallback. Freeze authoritative model-specific rates and use exact-decimal
charge calculation, distinguishing calculated charge from an actual provider
debit when both are available.

Preserved planning rates are US$0.15/million uncached input, US$0.014/million
cached input, and US$0.60/million output; these are not a claim of newly verified
current pricing. At those rates the uncached worst case is US$1.0616832 for two
arms, US$1.5925248 for three, and US$0.0221184 for the separate probe. Admission
must verify authoritative current rates and that the frozen maximum still fits
US$2. If not, block rather than adapt the experiment after outcomes.

For each paired block reserve the entire arm count, tokens, and maximum charge
atomically. Outstanding/unresolved requests retain conservative reservations;
do not release their allowance on the assumption that no charge occurred.

## 14. Provenance, STOP, and Recovery

Use a separate M0.10 study identity, ledger, and artifact tree. Never write M0.10
results into historical M0.9 optimization tables. Record preregistration and
schema hashes, scenario and schedule hashes, parent registry, arm decision,
admission evidence, Python/runtime identity, model/provenance metadata, complete
request and response, timestamps, latency, usage, thinking/final content, strict
validation stages, first failure, canonical compiler output, behavioral hash,
and exact-decimal accounting. Redact credentials, not scientific output.

Durable request state remains:

```text
PREPARED -> RESERVED -> STARTED -> RESPONSE_SAVED -> CLASSIFIED -> COMPLETE
```

Persist identity and reservation before send. A STARTED request with no resolvable
receipt is never resent. Recovery may classify an already-saved receipt offline;
it may not manufacture a replacement observation. Capture already-started sibling
responses after STOP. Do not dispatch another block while a started receipt is
unresolved, or after campaign STOP.

Stop on identity drift, accounting failure, unresolved sent request, resource
ceiling, security/disclosure failure, or provider-contract change. HTTP redirect,
connection failure, timeout, server error, partial response, and crash must not
trigger automatic inference retries. No later response changes another request.
Report an incomplete campaign transparently without readiness/improvement labels.
Deterministic export/replay must reconstruct analysis with zero inference.

## 15. Offline Requirements and Separate Authorization

Before any separately authorized launch, future implementation must validate all
mutable domains, numeric boundaries, duplicate/conflicting operations, invalid
parents, immutable fields, combined constraints, resource limits, canonicalization,
behavioral hashes, and no silent repair. F1/F2 must share one schema and compiler.
F2 tests include zero/multiple/duplicate/unknown calls, missing/extra fields,
invalid enums, stringified arguments, prose/reasoning-only responses, exact probe
arguments, complete-but-non-`stop` documented reasons, and explicit truncation.

Required scheduling tests cover both arm counts, whole-block reservation,
concurrent eligibility/send, sibling construction before response consumption,
arbitrary completion order, STOP, unresolved receipts, and no resend/retry.
Analysis tests include readiness independent of F0, F0 itself ready, comparative
improvement without readiness, readiness without improvement, incomplete studies,
family coverage, leakage, duplicate-valid results, bootstrap degeneracies, all
256 distinct swap assignments, ties, no `+1`, and conditional Holm adjustment.

Freeze rendered representative/maximum-sized requests and confirm all applicable
payload caps, scenario isolation, and no source-bearing disclosures. No dynamic
cap increase, schema redesign, prompt repair, or changed compiler is authorized
to make an otherwise infeasible arm fit.

Implementation, operational admission/probe, and feasibility execution are
separate later milestones requiring explicit authorization. This planning
revision performs none of them. Even INTERFACE_READY plus
INTERFACE_MEDIATED_IMPROVEMENT does not launch search. Any later optimization
study needs its own frozen design and authorization; no automatic progression.

## 16. Final Internal-Consistency Audit

| Audit item | Final specification |
| --- | --- |
| F0 historical fidelity | Original prompt, contract, parser, defaults, category normalization, first-failure behavior, and compiler; no artificial full-field requirement. |
| F1/F2 vocabulary | One MutationProposalV1 schema, identical 15 fields/domains/categories, identical parent inheritance and compiler; only transport/prompt suffix differ. |
| Readiness versus improvement | Independent absolute readiness gate for every arm; separate six-acquisition/positive-progression-CI comparative label. F0 can be ready. |
| F2 admission timing | Offline/capability checks and arm freeze precede all feasibility outcomes. Common admission failure blocks launch; no adaptive F2 substitution. |
| Paired scheduling | One seed-42 scenario shuffle; same-scenario concurrent arm block, capacity two/three established at launch, full receipt settlement before next block. |
| Completion semantics | `done=true`, exact one native call/arguments, complete response, identity and accounting; literal `stop` not required, documented meaning mandatory. |
| Statistical procedure | Paired whole-family bootstrap; exact 24-scenario difference under all 256 joint-family swaps; inclusive tails/no +1; conditional Holm for the two F0 comparisons only. |
| Request/token/cost ceilings | 48 or 72 feasibility requests, separate one-shot operational probe, distinct token ledgers, combined US$2 included-credit exposure, no retries or budget expansion. |
| Protected cohort isolation | No Search32 content/execution, Qualification48, Final96, hidden tests/results, reference answers, or source-bearing traces. |
| Runner calls | Zero; neither real nor fake Runner evaluation is part of feasibility. Compiler acceptance is not Runner execution. |
| Progression | Readiness and comparative evidence are reported, never an automatic search authorization. |
| Outcome independence | Arm admission, scenario cohort, prompts, limits, schedule, classification, intervals, permutation statistic, and interpretation gates are fixed before feasibility outcomes. |

This is a specification audit, not a claim that future machinery/admission checks
have been executed or passed. No protected benchmark contents were needed.

## 17. Concise Changelog

1. Separated INTERFACE_READY from INTERFACE_MEDIATED_IMPROVEMENT. Operational
   reliability is now classified independently for F0/F1/F2; comparative evidence
   retains the six-net-acquisition and positive progression-interval thresholds.
   Added explicit interpretations for the requested readiness/improvement cases.
2. Removed the undocumented literal `done_reason="stop"` probe gate. Kept every
   native-call, exact-argument, completeness, identity, and accounting requirement;
   unfamiliar reasons require documented semantic interpretation and truncation
   still fails.
3. Replaced global arm/scenario shuffling and waves of two with one seed-42
   scenario shuffle and concurrent paired blocks of two or three. Required
   authenticated capacity and all-started-receipt settlement now explicitly gate
   launch and next-block dispatch; completion order never changes the experiment.
4. Specified the exact permutation statistic and inclusive two-sided tail over
   all 256 joint-family swaps, with no Monte-Carlo correction. Conditional Holm
   across F1/F0 and F2/F0 remains; F2/F1 remains descriptive.

Unchanged: same Planner/endpoint/accounting identity contract and principal
sampling/thinking condition; historical F0 and M0.9 result; shared mutation
vocabulary/compiler; 24 synthetic scenarios/eight families; F2 pre-outcome
admission; equal generation ceilings; no repair/retry; bootstrap settings;
request/token/cost/time limits; disclosure/security boundaries; cohort isolation;
zero Runner calls; separate authorization and no automatic scaffold search.
