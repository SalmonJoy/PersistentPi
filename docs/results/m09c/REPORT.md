> Public scientific excerpt. Private account, task-level and raw evidence are withheld.
> Historical test counts describe the private checkout, not public test certification.

# M0.9C - Admission Stop

[Private account observation retained privately.]

[Private account observation retained privately.]

[Private account observation retained privately.]

## Forecast And Reservations
The frozen seed-9005, 2000-resample P90 forecast used all 64 measured M0.8C/D A/B exposed-development windows.
Projected Runner tokens: 3,637,275; projected active seconds: 9311.200 (2.586 hours).
Both <4.5M and <9h forecast gates pass. The design includes all 368 windows and eight Planner deadlines.
Keep 144 later qualification windows / 2160 Runner calls / 2,304,000 Runner tokens reserved, unspent.
Search upper bound 224 windows plus qualification reserve uses at most 5,888,000 Runner tokens / 5520 calls.
Planner remains separately bounded by eight requests / 200k accounted tokens; shared wall ceiling is 12 active hours.
Worst-case per-window times do not guarantee completing within that ceiling; the frozen wall stop takes precedence.
Forecast feasibility does not override failed Planner admission. No resource limits or task counts were changed.

## References, Proposals, Search, Archive And Finalist
Fresh B0/B1 references were **not run**. All eight proposal slots are **not run due to admission**, not invalid proposals.
Screen8, Remaining24 and FullSearchScore were not evaluated. No archive entry, generated scaffold, finalist or gate decision exists.
No Planner requests/responses/disclosures or Runner results exist; empty lists and explicit statuses are recorded in execution-status.json.
Search access was never opened and is closed for this terminal admission record. M0.9D remains separately authorized.
The status is not "No M0.9C finalist qualified for M0.9D": that wording would imply a search-entry gate was evaluated.

## Expenditure And Failure Modes
Live Runner inference calls/tokens: 0/0. Planner inference calls/tokens: 0/0. Search task windows: 0.
Reference/search/Planner inference seconds and active optimization-campaign wall time: zero; admission/test time is separate overhead.
There are no observed model acquisition, interface, repetition or proposal-quality failures in M0.9C.
The blocking failure is operational admission, not evidence about Planner or Runner capability.

## Validation And Integrity
Preflight: 487 total tests pass (479 historical/M0.9B plus 8 operational). Postflight: 487 tests pass.
The initial harness attempt had 145 setup errors because its guard also denied provenance-only checksums.
That failed run is preserved under pre-validation-attempt1; the operational guard was fixed, not the historical tests.
Frozen historical assertions were unchanged. Qualification-constructor tests use recipe parameters 12..16 and qfixture-m09c IDs.
The historical all-split tests retain synthetic 7..11 parameter fixtures and namespaced task IDs.
No real Qualification48 cases, final-task contents or benchmark hidden scores were consumed.
Protected Qualification48 content was streamed only for mandated SHA256 integrity verification, never parsed or executed.
SQLite integrity is ok; backup API export replays admission and checks byte-for-byte without inference.
admission.sqlite is an **admission-only evidence ledger**, not an optimization campaign database.
No optimization DB/proposal/result/finalist artifacts are fabricated for an unstarted campaign.
All M0.9B frozen sources/artifacts and historical evidence remain unchanged; operational additions are outside the frozen inventory.

## Conclusions And Limits
Outcome A demonstrates a safe admission stop under the frozen requirements; it does not measure scaffold optimization.
There is no basis for claims about qualification transfer, unseen templates, hidden generalization, repeated-campaign reliability,
matched-budget random/human superiority or universal optimization effectiveness.
Any future launch needs separately verified rotation, approved-model free access, authoritative allowance/accounting and live identity admission.
No search, qualification or paid access is automatically resumed from this record.
