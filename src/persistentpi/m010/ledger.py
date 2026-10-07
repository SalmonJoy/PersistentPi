"""Separate SQLite ledger with atomic block reservations and immutable receipts."""
from contextlib import contextmanager
from copy import deepcopy
import datetime as dt
import hashlib
import json
from pathlib import Path
import sqlite3
import threading
import time

from ..artifacts import atomic_write
from ..contracts import canonical, digest
from .accounting import money, reservation, charge
from .config import ROOT, DEFAULT, budget
from .render import request_identity
from .boundary import isolated_output

SCHEMA = '''
CREATE TABLE IF NOT EXISTS m010_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS m010_study(id TEXT PRIMARY KEY,freeze_hash TEXT NOT NULL,arms TEXT NOT NULL,
 schedule TEXT NOT NULL,registry TEXT NOT NULL,pricing TEXT NOT NULL,mode TEXT NOT NULL,status TEXT NOT NULL,
 stop_reason TEXT,created_utc TEXT NOT NULL,active_seconds REAL NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS m010_blocks(study TEXT NOT NULL,scenario TEXT NOT NULL,ordinal INTEGER NOT NULL,
 state TEXT NOT NULL,PRIMARY KEY(study,scenario),UNIQUE(study,ordinal));
CREATE TABLE IF NOT EXISTS m010_requests(id TEXT PRIMARY KEY,study TEXT NOT NULL,scenario TEXT NOT NULL,
 arm TEXT NOT NULL,state TEXT NOT NULL,request_hash TEXT NOT NULL,response_hash TEXT,account_hash TEXT,
 classification_hash TEXT,reserved_tokens INTEGER NOT NULL,reserved_credit TEXT NOT NULL,
 sent_utc TEXT,received_utc TEXT,latency REAL,error TEXT,UNIQUE(study,scenario,arm));
CREATE TABLE IF NOT EXISTS m010_probe(id TEXT PRIMARY KEY,request_hash TEXT NOT NULL,state TEXT NOT NULL,
 response_hash TEXT,account_hash TEXT,result_hash TEXT,reserved_credit TEXT NOT NULL,error TEXT);
CREATE TABLE IF NOT EXISTS m010_events(id INTEGER PRIMARY KEY AUTOINCREMENT,study TEXT,kind TEXT NOT NULL,
 utc TEXT NOT NULL,payload_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS m010_artifacts(hash TEXT PRIMARY KEY,bytes INTEGER NOT NULL,kind TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS m010_admission(id TEXT PRIMARY KEY,value_hash TEXT NOT NULL);
'''


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


class Ledger:
    def __init__(self, folder, secrets=()):
        self.folder = isolated_output(folder)
        if 'm09' in self.folder.name or self.folder.is_relative_to(ROOT / 'docs/research-records/m09c-primary-no-finalist'):
            raise ValueError('M010_NAMESPACE')
        self.folder.mkdir(parents=True, exist_ok=True)
        self.secrets = tuple(secrets)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(self.folder / 'm010.sqlite', check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        old = [r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        if any(not name.startswith(('m010_', 'sqlite_')) for name in old):
            self.db.close()
            raise ValueError('M010_FOREIGN_NAMESPACE')
        self.db.executescript(SCHEMA)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO m010_meta VALUES('schema','M0.10A/1')")
        if self.db.execute("SELECT value FROM m010_meta WHERE key='schema'").fetchone()[0] != 'M0.10A/1':
            raise ValueError('M010_LEDGER_VERSION')

    def close(self):
        self.db.close()

    @contextmanager
    def transaction(self):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                yield
                self.db.commit()
            except BaseException:
                self.db.rollback()
                raise

    def put(self, value, kind):
        raw = canonical(value)
        for secret in self.secrets:
            if secret and (secret.encode() in raw or json.dumps(secret)[1:-1].encode() in raw):
                raise ValueError('M010_SECRET_DISCLOSURE')
        key = hashlib.sha256(raw).hexdigest()
        path = self.folder / 'artifacts' / key
        if path.exists() and path.read_bytes() != raw:
            raise ValueError('M010_ARTIFACT_CORRUPT')
        if not path.exists():
            atomic_write(path, raw)
        self.db.execute('INSERT OR IGNORE INTO m010_artifacts VALUES(?,?,?)', (key, len(raw), kind))
        return key

    def get(self, key):
        if not isinstance(key, str) or len(key) != 64 or any(c not in '0123456789abcdef' for c in key):
            raise ValueError('M010_ARTIFACT_ID')
        raw = (self.folder / 'artifacts' / key).read_bytes()
        if hashlib.sha256(raw).hexdigest() != key:
            raise ValueError('M010_ARTIFACT_HASH')
        return json.loads(raw)

    def event(self, study, kind, payload):
        self.db.execute('INSERT INTO m010_events(study,kind,utc,payload_hash) VALUES(?,?,?,?)',
                        (study, kind, utc(), self.put(payload, 'event')))

    def create(self, study, freeze_hash, arms, schedule, registry, pricing, mode='recording-stub', completion_evidence=None,
               authorization=None, admission_evidence=None, freeze_manifest=None):
        budget(arms)
        if mode != 'recording-stub':
            from .admission import prerequisites
            admitted = prerequisites(admission_evidence or {}, arms)
            if (mode != 'admitted-cloud' or authorization != 'separately-authorized-feasibility' or not admitted['passed']
                    or not isinstance(freeze_manifest, dict) or freeze_manifest.get('hash') != freeze_hash):
                raise ValueError('M010_FEASIBILITY_NOT_AUTHORIZED')
            if (freeze_manifest.get('format') != 'm010-freeze-1'
                    or digest({k: v for k, v in freeze_manifest.items() if k != 'hash'}) != freeze_hash
                    or not freeze_manifest.get('source_files')):
                raise ValueError('M010_FREEZE_REQUIRED')
            from .freeze import verify_sources
            verify_sources(freeze_manifest)
            probe = self.probe()
            if probe and probe['state'] in ('STARTED', 'RESPONSE_SAVED'):
                raise ValueError('M010_OPERATIONAL_PROBE_UNRESOLVED')
            if probe and probe['state'] == 'COMPLETE':
                result = self.get(probe['result_hash'])
                if result.get('reason') in ('M010_PROVIDER_IDENTITY', 'M010_ACCOUNTING_MISSING',
                                            'M010_ACCOUNTING_LIMIT', 'M010_COMPLETION_UNESTABLISHED'):
                    raise ValueError('M010_COMMON_ADMISSION_FAILED')
            if len(arms) == 3 and (not self.probe() or self.probe()['state'] != 'COMPLETE'
                    or not self.get(self.probe()['result_hash'])['passed']):
                raise ValueError('M010_F2_NOT_ADMITTED')
        if len(schedule['scenario_order']) != 24:
            raise ValueError('M010_SCENARIO_ORDER')
        hashes = [digest(schedule), digest(registry), digest(pricing)]
        completion_evidence = completion_evidence or DEFAULT['completion']
        with self.transaction():
            existing = self.db.execute('SELECT * FROM m010_study WHERE id=?', (study,)).fetchone()
            if existing:
                expected = (freeze_hash, canonical(list(arms)).decode(), *hashes, mode)
                actual = tuple(existing[k] for k in ('freeze_hash', 'arms', 'schedule', 'registry', 'pricing', 'mode'))
                if expected != actual:
                    raise ValueError('M010_STUDY_DRIFT')
                frozen = self.db.execute('SELECT value_hash FROM m010_admission WHERE id=?', (study + ':completion',)).fetchone()
                if frozen is None or frozen[0] != digest(completion_evidence):
                    raise ValueError('M010_COMPLETION_DRIFT')
                return
            self.put(schedule, 'schedule'); self.put(registry, 'registry'); self.put(pricing, 'pricing')
            self.db.execute('INSERT INTO m010_study VALUES(?,?,?,?,?,?,?,?,?,?,0)',
                (study, freeze_hash, canonical(list(arms)).decode(), *hashes, mode, 'PREPARED', None, utc()))
            self.event(study, 'created', {'freeze_hash': freeze_hash, 'research_inference_authorized': False})
            self.db.execute('INSERT INTO m010_admission VALUES(?,?)',
                            (study + ':completion', self.put(completion_evidence, 'completion-catalog')))
            if freeze_manifest is not None:
                self.db.execute('INSERT INTO m010_admission VALUES(?,?)',
                                (study + ':freeze', self.put(freeze_manifest, 'study-freeze')))
            if admission_evidence is not None:
                self.db.execute('INSERT INTO m010_admission VALUES(?,?)',
                                (study + ':admission', self.put(admission_evidence, 'launch-admission')))

    def completion_catalog(self, study):
        row = self.db.execute('SELECT value_hash FROM m010_admission WHERE id=?', (study + ':completion',)).fetchone()
        if row is None:
            raise ValueError('M010_COMPLETION_CATALOG_MISSING')
        return self.get(row[0])

    def study(self, study):
        row = self.db.execute('SELECT * FROM m010_study WHERE id=?', (study,)).fetchone()
        if row is None:
            raise ValueError('M010_STUDY_MISSING')
        return dict(row)

    def requests(self, study):
        return [dict(r) for r in self.db.execute('SELECT * FROM m010_requests WHERE study=? ORDER BY scenario,arm', (study,))]

    def exposure(self, study):
        tokens = 0
        credit = money('0')
        for row in self.requests(study):
            if row['account_hash']:
                accounted = self.get(row['account_hash'])
                tokens += accounted['provider_accounted_tokens']
                credit += money(accounted['calculated_charge_usd'])
            else:
                tokens += row['reserved_tokens']
                credit += money(row['reserved_credit'])
        for row in self.db.execute('SELECT * FROM m010_probe'):
            credit += money(self.get(row['account_hash'])['calculated_charge_usd']) if row['account_hash'] else money(row['reserved_credit'])
        return {'requests': len(self.requests(study)), 'tokens': tokens, 'credit': credit}

    def reserve_block(self, study, scenario, ordinal, payloads):
        config = self.study(study)
        arms = tuple(json.loads(config['arms']))
        if set(payloads) != set(arms):
            raise ValueError('M010_BLOCK_ARMS')
        unit = reservation(self.get(config['pricing']))
        with self.transaction():
            if self.study(study)['status'] == 'STOPPED':
                raise ValueError('M010_STOPPED')
            if self.study(study)['active_seconds'] >= 10800:
                raise ValueError('M010_WALL_CEILING')
            old = self.db.execute('SELECT * FROM m010_blocks WHERE study=? AND scenario=?', (study, scenario)).fetchone()
            if old:
                for arm, payload in payloads.items():
                    row = self.db.execute('SELECT * FROM m010_requests WHERE id=?', (request_identity(study, scenario, arm),)).fetchone()
                    if row is None or row['request_hash'] != digest(payload):
                        raise ValueError('M010_REQUEST_DRIFT')
                    if row['state'] == 'STARTED':
                        raise ValueError('M010_SENT_UNRESOLVED')
                return
            order = self.get(config['schedule'])['scenario_order']
            if order[ordinal] != scenario:
                raise ValueError('M010_ORDER')
            prior = self.db.execute('SELECT COUNT(*) FROM m010_blocks WHERE study=? AND state=?', (study, 'COMPLETE')).fetchone()[0]
            if prior != ordinal:
                raise ValueError('M010_PRIOR_BLOCK_UNSETTLED')
            totals, cap = self.exposure(study), budget(arms)
            if (totals['requests'] + len(arms) > cap['requests']
                    or totals['tokens'] + len(arms) * unit['provider_tokens'] > cap['provider_tokens']
                    or totals['credit'] + len(arms) * money(unit['included_credit_usd']) > money('2.00')):
                raise ValueError('M010_RESOURCE_CEILING')
            self.db.execute('INSERT INTO m010_blocks VALUES(?,?,?,?)', (study, scenario, ordinal, 'RESERVED'))
            for arm, payload in payloads.items():
                qid = request_identity(study, scenario, arm)
                key = self.put(payload, 'request')
                self.db.execute('INSERT INTO m010_requests VALUES(?,?,?,?,?,?,NULL,NULL,NULL,?,?,NULL,NULL,NULL,NULL)',
                    (qid, study, scenario, arm, 'RESERVED', key, unit['provider_tokens'], unit['included_credit_usd']))
            self.event(study, 'block_reserved', {'scenario': scenario, 'arms': list(arms)})

    def start(self, qid):
        with self.transaction():
            row = self.db.execute('SELECT * FROM m010_requests WHERE id=?', (qid,)).fetchone()
            if row is None or row['state'] != 'RESERVED':
                raise ValueError('M010_NO_RESEND')
            self.db.execute('UPDATE m010_requests SET state=?,sent_utc=? WHERE id=?', ('STARTED', utc(), qid))
            self.event(row['study'], 'request_started', {'id': qid})

    def capture(self, qid, response, latency):
        with self.transaction():
            row = self.db.execute('SELECT * FROM m010_requests WHERE id=?', (qid,)).fetchone()
            if row is None or row['state'] != 'STARTED':
                raise ValueError('M010_RECEIPT_STATE')
            response_hash = self.put(response, 'response')
            self.db.execute('UPDATE m010_requests SET state=?,response_hash=?,received_utc=?,latency=? WHERE id=?',
                            ('RESPONSE_SAVED', response_hash, utc(), latency, qid))
        try:
            account = charge(response, self.get(self.study(row['study'])['pricing']))
        except (ValueError, KeyError) as exc:
            self.stop(row['study'], 'accounting_failure')
            raise ValueError('M010_ACCOUNTING_STOP') from exc
        with self.transaction():
            self.db.execute('UPDATE m010_requests SET account_hash=? WHERE id=?', (self.put(account, 'accounting'), qid))
        if account['ceiling_violations']:
            self.stop(row['study'], 'provider_resource_overrun')
            raise ValueError('M010_PROVIDER_RESOURCE_OVERRUN')
        return account

    def reserve_probe(self, payload, pricing, evidence):
        """Reservation alone never transmits; a single immutable slot per ledger."""
        unit = reservation(pricing)
        with self.transaction():
            row = self.db.execute('SELECT * FROM m010_probe').fetchone()
            if row:
                if row['request_hash'] != digest(payload):
                    raise ValueError('M010_PROBE_DRIFT')
                return dict(row)
            if money(unit['included_credit_usd']) > money('2.00'):
                raise ValueError('M010_PROBE_CEILING')
            key = self.put(payload, 'operational-probe-request')
            self.put(pricing, 'operational-probe-pricing')
            self.db.execute('INSERT INTO m010_admission VALUES(?,?)', ('probe-pricing', digest(pricing)))
            self.db.execute('INSERT INTO m010_admission VALUES(?,?)', ('probe-evidence', self.put(evidence, 'admission')))
            self.db.execute('INSERT INTO m010_probe VALUES(?,?,?,NULL,NULL,NULL,?,NULL)',
                            ('operational-f2', key, 'RESERVED', unit['included_credit_usd']))
            self.event(None, 'probe_reserved', {'id': 'operational-f2', 'provider_tokens': 135168})
        return self.probe()

    def probe(self):
        row = self.db.execute('SELECT * FROM m010_probe').fetchone()
        return dict(row) if row else None

    def start_probe(self):
        with self.transaction():
            row = self.probe()
            if not row or row['state'] != 'RESERVED':
                raise ValueError('M010_PROBE_NO_RESEND')
            self.db.execute('UPDATE m010_probe SET state=?', ('STARTED',))
            self.event(None, 'probe_started', {'id': row['id']})

    def capture_probe(self, response, receipt):
        with self.transaction():
            if self.probe()['state'] != 'STARTED':
                raise ValueError('M010_PROBE_RECEIPT_STATE')
            self.put(receipt, 'operational-probe-wire-receipt')
            self.db.execute('UPDATE m010_probe SET state=?,response_hash=?',
                            ('RESPONSE_SAVED', self.put(response, 'operational-probe-response')))
        return self.finalize_probe()

    def finalize_probe(self):
        row = self.probe()
        if not row or row['state'] != 'RESPONSE_SAVED' or not row['response_hash']:
            raise ValueError('M010_PROBE_RECOVERY_STATE')
        response = self.get(row['response_hash'])
        from .admission import probe_result
        evidence_key = self.db.execute("SELECT value_hash FROM m010_admission WHERE id='probe-evidence'").fetchone()[0]
        completion = self.get(evidence_key).get('api', {}).get('completion_reasons')
        result = probe_result(response, completion)
        key = self.db.execute("SELECT value_hash FROM m010_admission WHERE id='probe-pricing'").fetchone()[0]
        try:
            account = charge(response, self.get(key))
        except (ValueError, KeyError) as exc:
            with self.transaction():
                self.db.execute('UPDATE m010_probe SET error=?', ('accounting_failure',))
            raise ValueError('M010_PROBE_ACCOUNTING_STOP') from exc
        with self.transaction():
            self.db.execute('UPDATE m010_probe SET state=?,account_hash=?,result_hash=?',
                            ('COMPLETE', self.put(account, 'operational-probe-account'), self.put(result, 'operational-probe-result')))
        return result

    def classified(self, qid, result):
        with self.transaction():
            row = self.db.execute('SELECT * FROM m010_requests WHERE id=?', (qid,)).fetchone()
            if row is None or row['state'] != 'RESPONSE_SAVED' or not row['account_hash']:
                raise ValueError('M010_CLASSIFICATION_STATE')
            if result['arm'] != row['arm'] or result['scenario_id'] != row['scenario']:
                raise ValueError('M010_CLASSIFICATION_IDENTITY')
            self.db.execute('UPDATE m010_requests SET state=?,classification_hash=? WHERE id=?',
                            ('CLASSIFIED', self.put(result, 'classification'), qid))
        with self.transaction():
            self.db.execute('UPDATE m010_requests SET state=? WHERE id=?', ('COMPLETE', qid))

    def stop(self, study, reason):
        with self.transaction():
            self.db.execute('UPDATE m010_study SET status=?,stop_reason=COALESCE(stop_reason,?) WHERE id=?',
                            ('STOPPED', reason, study))
            self.event(study, 'STOP', {'reason': reason})

    def settle(self, study, scenario, elapsed):
        with self.transaction():
            self.db.execute('UPDATE m010_study SET active_seconds=active_seconds+? WHERE id=?', (elapsed, study))
            row = self.study(study)
            if row['active_seconds'] > 10800:
                self.db.execute('UPDATE m010_study SET status=?,stop_reason=? WHERE id=?', ('STOPPED', 'wall_ceiling', study))
            states = [r['state'] for r in self.requests(study) if r['scenario'] == scenario]
            if states and all(s == 'COMPLETE' for s in states):
                self.db.execute('UPDATE m010_blocks SET state=? WHERE study=? AND scenario=?', ('COMPLETE', study, scenario))
            count = self.db.execute('SELECT COUNT(*) FROM m010_blocks WHERE study=? AND state=?', (study, 'COMPLETE')).fetchone()[0]
            if count == 24 and self.study(study)['status'] != 'STOPPED':
                self.db.execute('UPDATE m010_study SET status=? WHERE id=?', ('COMPLETE', study))

    def result_rows(self, study):
        values = []
        for row in self.requests(study):
            if row['classification_hash']:
                result = self.get(row['classification_hash'])
                account = self.get(row['account_hash'])
                result.update(account=account, latency_seconds=row['latency'], request_id=row['id'],
                              request_hash=row['request_hash'], response_hash=row['response_hash'], state=row['state'])
                values.append(result)
        return values

    def backup(self, destination):
        with self.lock:
            with sqlite3.connect(destination) as target:
                self.db.backup(target)

    def integrity(self):
        return self.db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
