> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.10A-I Offline Implementation and Freeze

Release identity: annotated tag `m0.10a-i`. Resolve the final commit with
`git rev-parse m0.10a-i^{commit}`. The final response reports its concrete hash.

## Historical Outcome

M0.9C remains unchanged: **0/8 valid GPT-OSS 120B proposals under the historical
Planner-to-ScaffoldSpec contract; no generated scaffold reached Runner
evaluation**. Historical commits, tags, validators and primary artifacts were
not rewritten. The existing forensic `proposals.json` is included unchanged as
the read-only F0 parity dependency; other pre-existing forensic files remain
untouched.

This milestone implements M0.10A/1 only. It supplies no scientific feasibility
result, no scaffold-search outcome and no Runner-performance claim.

## Validation

- **59 new offline tests passed**, with no errors, failures or source drift.
  The tested source hashes are in `new-tests.json`.
- Historical regression attempted **619 tests**, with **225 explicit deferral
  records**, zero errors and zero failures. The exact discovery/attempt and
  deferral receipt is `historical-tests.json`. All permitted historical tests passed. Explicit
  protected-boundary deferrals are not passes and no full-suite pass is claimed.
- The two user-authorized regression exceptions and their exact gate are
  documented in `REGRESSION-SCOPE.md` and embedded in the freeze evidence.
- F0 reproduced all eight historical first rejection classes: four
  `MALFORMED`, three `PROPOSAL_CATEGORY`, one `PROPOSAL_TEXT`. No repair was
  applied. The original historical defaults, normalization and omitted-field
  behavior remain in force.
- Strict MutationProposalV1 compilation supports all 15 mutable fields through
  exact normalized-parent inheritance. Field domains, enum catalogs, numeric
  boundaries, bool/int separation, resource/dependent constraints, duplicate
  and conflicting operations, forbidden fields, canonicalization and
  order-independent behavioral hashes passed offline tests.
- F1 and F2 share one semantic schema. F2 requires exactly one named native
  call with object-valued arguments. No response-format enforcement, forced
  tool choice, repair call, second model turn or executable generated code is
  available.
- Two- and three-arm paired dispatch, completion-order independence, durable
  reservations, one-shot sends, unresolved-request blocking, saved-receipt
  recovery, redaction and protected-worker capability tests passed.
- All **nine A-I recording-HTTP campaigns** passed export/replay validation.
  `validation-final/final-source-replay.json` confirms replay under the final
  source snapshot. Campaign F is incomplete and has no readiness/improvement
  classification. Campaign G blocks readiness through systematic leakage.
  Campaign H rejects truncation. Campaign I preserves valid duplicates.

The requirement-by-requirement audit is `REQUIREMENTS.md`. Counts in the
historical receipt include subtests/class-setup deferrals; subtraction would
not produce a reliable passed-test count.

## Synthetic Freeze and Payloads

Exactly 24 synthetic scenarios, eight semantic families times three instances,
were generated without real benchmark contents or source-bearing Runner traces.
The exact scenarios, assignments, observations and requests are in `prepared/`.
`scenario-checksums.json` lists every individual canonical scenario checksum.

Python: **3.11.4**. Lexical scenario IDs were shuffled exactly once by
`random.Random(42)`. Schedule hash:

`5e460a67b3b298f73a4503ae9c1ea960527618ae2f48beaf10d9ae468180f768`

| Request | Largest Canonical UTF-8 Payload |
| --- | ---: |
| F0 | 7,411 bytes |
| F1 | 12,272 bytes |
| F2 | 11,782 bytes |
| Frozen operational F2 probe | 4,731 bytes |

All requests fit the unchanged **16,384-byte cap**, including the expanded F2
oneOf schema. These are exact maxima over the immutable 24-scenario/B0-B1
registry, not estimates. Offline payload feasibility is not proof of cloud
tool-call capability. The F2 probe is frozen but **unexecuted**.

## Analysis and Accounting

Readiness and comparative improvement are independently representable. F0 can
be operationally ready. An interface may improve materially yet remain not
ready, or be ready without improving over F0. No result automatically launches
scaffold search.

Bootstrap validation uses 100,000 whole-family paired resamples, seed 20261010,
and nearest-rank percentile intervals. All 256 family-level label assignments
are enumerated with the same 24-scenario mean-difference statistic, inclusive
absolute-tail ties, denominator 256, and no Monte Carlo +1. Conditional
three-arm Holm adjustment covers only F1/F0 and F2/F0; F2/F1 is descriptive.

Provider accounting is `prompt_eval_count + eval_count`. Cached tokens are
separate and never double-counted. Thinking bytes are not reasoning tokens.
Charges use Decimal arithmetic with authoritative counters/rates, not an
invented debit. Unknown accounting stops the study. Known counter overruns are
recorded without clipping before STOP.

| Future Mode | Feasibility Requests | Feasibility Token Ceiling |
| --- | ---: | ---: |
| F0/F1 | 48 | 6,488,064 |
| F0/F1/F2 | 72 | 9,732,096 |
| Separate one-shot operational probe | 1 | 135,168 |

The combined included-credit ceiling remains **US$2**. The operational probe
does not consume feasibility request slots. No purchased additional credits,
reload, top-up, upgrade, fallback, replacement request or adaptive expansion is
allowed. Planning rates do not establish current account entitlement or
authoritative launch pricing.

## Boundaries and Freeze

M0.10 Runner calls: **0**. Planner research inference: **0**. Actual operational
probes: **0**. Existing historical fake-Runner fixtures were permitted only by
the explicit regression exception. No M0.10 fake Runner was introduced.

Search32 contents, Qualification48, Final96, reference solutions and hidden
research scoring were not accessed or executed. The scenario generator and
scheduler have explicit capability audits; no arbitrary-code sandbox claim is
made. Historical tests attempting disallowed access were blocked and deferred.

The authoritative offline freeze is **`prepared/freeze.json`**. It contains
the manifest hash, preparation/artifact/source hashes, historical anchors and
full test-gate evidence. `freeze-summary.json` provides the hash/path and final
validation counts. Preparation is not live admission and freeze is not launch
authorization.

Verified freeze hash:

`ef28f186dc9e66d02a89c183b2293a8ec4778560cd3d69e49509e7e63a973f8e`


[Private task-level/operational evidence retained in the research repository.]

## Worktree

The final release commits the isolated M0.10 implementation, preregistration,
prepared freeze, recording-stub evidence and the unchanged historical parity
dependency. Pre-existing untracked M0.9C-F forensic files are preserved, not
removed or rewritten. Interim generated M0.10 validation is retained separately
under ignored `.local/m010a-i-interim-validation`. Final worktree status and
concrete release commit are reported in the final response.
