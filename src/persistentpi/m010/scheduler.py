"""Paired temporal blocks; only recording transports admitted by this milestone."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextvars import copy_context
import threading
import time

from .classifier import classify
from .render import render, request_identity
from .boundary import access_audit
from .config import ROOT
from .frozen import ANCHORS, verify_anchors
from .frozen import parent_registry
from .scenarios import generate, schedule
from ..contracts import canonical


class Scheduler:
    def __init__(self, ledger, study, scenarios, completion_evidence=None):
        verify_anchors()
        self.ledger, self.study_id = ledger, study
        self.scenarios = {s['id']: s for s in scenarios}
        config = ledger.study(study)
        registry = ledger.get(config['registry'])
        if registry != parent_registry():
            raise ValueError('M010_REGISTRY_DRIFT')
        expected = {s['id']: s for s in generate(registry)}
        if canonical(self.scenarios) != canonical(expected):
            raise ValueError('M010_SCENARIO_DRIFT')
        if ledger.get(config['schedule']) != schedule(tuple(expected.values())):
            raise ValueError('M010_SCHEDULE_DRIFT')
        frozen = ledger.completion_catalog(study)
        if completion_evidence is not None and completion_evidence != frozen:
            raise ValueError('M010_COMPLETION_DRIFT')
        self.completion_evidence = frozen

    def run(self, transport):
        mode = self.ledger.study(self.study_id)['mode']
        from .freeze import trusted_sources
        reads = [ROOT / p for p in ANCHORS] + (trusted_sources() if mode == 'admitted-cloud' else [])
        with access_audit(reads=reads, writes=[self.ledger.folder], network=mode == 'admitted-cloud'):
            return self._run(transport)

    def _run(self, transport):
        import json
        config = self.ledger.study(self.study_id)
        arms = tuple(json.loads(config['arms']))
        if getattr(transport, 'kind', None) != config['mode']:
            raise PermissionError('M010_FEASIBILITY_INFERENCE_NOT_AUTHORIZED')
        if transport.concurrency < len(arms):
            raise ValueError('M010_CONCURRENCY_ADMISSION')
        order = self.ledger.get(config['schedule'])['scenario_order']
        registry = self.ledger.get(config['registry'])
        for ordinal, sid in enumerate(order):
            if self.ledger.study(self.study_id)['status'] in ('STOPPED', 'COMPLETE'):
                break
            if config['mode'] == 'admitted-cloud':
                from .freeze import verify_sources
                frozen = self.ledger.db.execute('SELECT value_hash FROM m010_admission WHERE id=?', (self.study_id + ':freeze',)).fetchone()
                try:
                    verify_sources(self.ledger.get(frozen[0]))
                except (ValueError, KeyError, TypeError):
                    self.ledger.stop(self.study_id, 'control_plane_integrity')
                    break
            scenario = self.scenarios[sid]
            payloads = {a: render(scenario, a) for a in arms}
            try:
                self.ledger.reserve_block(self.study_id, sid, ordinal, payloads)
            except ValueError as exc:
                self.ledger.stop(self.study_id, str(exc))
                break
            rows = {r['arm']: r for r in self.ledger.requests(self.study_id) if r['scenario'] == sid}
            pending = [a for a in arms if rows[a]['state'] == 'RESERVED']
            # Saved receipts are classified without another transmission.
            for arm, row in rows.items():
                if row['state'] == 'RESPONSE_SAVED' and row['account_hash']:
                    result = self._classify(row['id'], scenario, arm, registry)
                elif row['state'] == 'CLASSIFIED':
                    with self.ledger.transaction():
                        self.ledger.db.execute('UPDATE m010_requests SET state=? WHERE id=?', ('COMPLETE', row['id']))
            barrier = threading.Barrier(len(pending)) if pending else None
            began = time.monotonic()
            def execute(arm):
                qid = request_identity(self.study_id, sid, arm)
                started = time.monotonic()
                try:
                    self.ledger.start(qid)
                    barrier.wait(timeout=10)
                    response = transport.send(payloads[arm], {'scenario': sid, 'arm': arm, 'request_id': qid})
                    if hasattr(transport, 'receipts') and qid in transport.receipts:
                        with self.ledger.transaction():
                            self.ledger.put(transport.receipts[qid], 'wire-receipt')
                    self.ledger.capture(qid, response, time.monotonic() - started)
                    return self._classify(qid, scenario, arm, registry)
                except BaseException as exc:
                    if barrier:
                        barrier.abort()
                    with self.ledger.transaction():
                        if hasattr(transport, 'receipts') and qid in transport.receipts:
                            self.ledger.put(transport.receipts[qid], 'failed-wire-receipt')
                        self.ledger.db.execute('UPDATE m010_requests SET error=? WHERE id=?', (type(exc).__name__, qid))
                    self.ledger.stop(self.study_id, type(exc).__name__ + ':request_unresolved_or_invalid')
                    return None
            if pending:
                with ThreadPoolExecutor(max_workers=len(arms)) as pool:
                    futures = [pool.submit(copy_context().run, execute, a) for a in pending]
                    for future in as_completed(futures):
                        future.result()
            self.ledger.settle(self.study_id, sid, time.monotonic() - began)
        return self.ledger.study(self.study_id)

    def _classify(self, qid, scenario, arm, registry):
        row = next(r for r in self.ledger.requests(self.study_id) if r['id'] == qid)
        response = self.ledger.get(row['response_hash'])
        allowed = {scenario['parent_id']: registry[scenario['parent_id']]}
        result = classify(response, arm, allowed, self.completion_evidence)
        result.update(scenario_id=scenario['id'], family=scenario['family'], instance=scenario['instance'],
                      parent_id=scenario['parent_id'])
        self.ledger.classified(qid, result)
        failure = (result['first_failure'] or {}).get('reason', '')
        if failure in ('M010_PROVIDER_IDENTITY', 'M010_COMPLETION_UNESTABLISHED'):
            self.ledger.stop(self.study_id, failure)
        return result
