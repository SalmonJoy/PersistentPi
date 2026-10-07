"""Trusted protocol-0.6 writer and cumulative resource reservations."""
import json
from pathlib import Path
import time
import uuid
import hashlib

from ..artifacts import Artifacts
from ..contracts import canonical, digest
from ..telemetry import Store, utc
from . import PROTOCOL
from .cohorts import manifest, split_search
from .spec import compile_scaffold, interface_catalog, ScaffoldSpecV1

LIMITS = {'runner_calls': 5520, 'runner_tokens': 6000000, 'planner_requests': 8,
          'planner_tokens': 200000, 'physical_windows': 368, 'active_wall_seconds': 43200}
WINDOW = {'max_attempts':1,'max_model_decisions':15,'max_tool_calls':15,'max_tokens':16000,
          'max_wall_seconds':120,'test_timeout_seconds':5,'max_workspace_bytes':10485760,
          'max_output_bytes':4096,'max_edit_bytes':8192}


def execution_hash():
    root = Path(__file__).resolve().parents[3]
    paths = list((root/'src/persistentpi').rglob('*.py')) + list((root/'migrations').glob('*.sql'))
    return digest({p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)})


class OptimizationStore:
    def __init__(self, folder, config, search, qualification, campaign_id=None, clock=time.monotonic):
        try:
            self._initialize(folder, config, search, qualification, campaign_id, clock)
        except BaseException:
            if hasattr(self, 'store'):
                self.store.close()
            raise

    def _initialize(self, folder, config, search, qualification, campaign_id, clock):
        root = Path(__file__).resolve().parents[3]
        resolved = Path(folder).resolve()
        if resolved.is_relative_to(root) and not resolved.is_relative_to(root/'.local'):
            raise ValueError('Mutable stores must not open repository code or archived evidence; use .local')
        if config.get('protocol_version') != PROTOCOL or config.get('window') != WINDOW:
            raise ValueError('Immutable protocol/window resource configuration changed')
        fingerprint = execution_hash()
        self.store = Store(Path(folder))
        self.db, self.artifacts = self.store.db, Artifacts(self.store)
        self.clock, self.started = clock, clock()
        self.config = config
        self.search, self.qualification = tuple(search), tuple(qualification)
        if campaign_id is None:
            if self.db.execute('SELECT COUNT(*) FROM m09_campaigns').fetchone()[0]:
                raise ValueError('Existing campaign requires explicit resume identity')
            self.id = str(uuid.uuid4())
            mh = self.store.manifest('m09-preregistration', config)
            state = {'round': 1, 'slot': 1, 'active_wall_seconds': 0, 'stop_reason': None,
                     'execution_hash': fingerprint}
            with self.db:
                self.db.execute('INSERT INTO experiments VALUES(?,?,?,?)', (self.id, mh, PROTOCOL, utc()))
                self.db.execute('INSERT INTO m09_campaigns VALUES(?,?,?,?,?,?)',
                                (self.id, PROTOCOL, 'references', mh, canonical(state).decode(), utc()))
            for name, tasks in (('search', search), ('qualification', qualification)):
                m = manifest(tasks, name)
                artifact = self.put(m, 'cohort_manifest')
                screen_ids = {t.task_id for t in split_search(search)[0]}
                with self.db:
                    self.db.execute('INSERT INTO m09_cohorts VALUES(?,?,?,?)', (self.id, name, m['hash'], artifact))
                    for t in tasks:
                        subset = 'qualification' if name == 'qualification' else ('screen' if t.task_id in screen_ids else 'remaining')
                        self.db.execute('INSERT INTO m09_members VALUES(?,?,?,?,?,?,?)',
                                        (self.id, m['hash'], t.task_id, t.task_hash, t.family, t.template, subset))
        else:
            self.id = campaign_id
            row = self.campaign()
            if row['config_hash'] != digest(config):
                raise ValueError('Resume preregistration drift')
            if self.state().get('execution_hash') != fingerprint:
                raise ValueError('Resume trusted execution code drift')
            for name, tasks in (('search', search), ('qualification', qualification)):
                old = self.db.execute('SELECT hash FROM m09_cohorts WHERE campaign=? AND name=?', (self.id, name)).fetchone()
                if not old or old[0] != manifest(tasks, name)['hash']:
                    raise ValueError('Resume cohort drift')
            self.recover()
        self.wall_base = self.state()['active_wall_seconds']

    def put(self, value, kind='m09_record'):
        return self.artifacts.put(canonical(value), kind, 'research')

    def get(self, identity):
        return json.loads(self.artifacts.get(identity))

    def campaign(self):
        row = self.db.execute('SELECT * FROM m09_campaigns WHERE id=?', (self.id,)).fetchone()
        if not row:
            raise ValueError('Unknown optimization campaign')
        return dict(row)

    def state(self):
        return json.loads(self.campaign()['state_json'])

    def update(self, phase=None, **changes):
        state = {**self.state(), **changes}
        state['active_wall_seconds'] = self.active_wall()
        phase = phase or self.campaign()['phase']
        artifact = self.put({'phase': phase, 'state': state}, 'phase_state')
        with self.db:
            self.db.execute('UPDATE m09_campaigns SET phase=?,state_json=? WHERE id=?', (phase, canonical(state).decode(), self.id))
            seq = self.db.execute('SELECT COALESCE(MAX(sequence),0)+1 FROM m09_phase_events WHERE campaign=?', (self.id,)).fetchone()[0]
            self.db.execute('INSERT INTO m09_phase_events VALUES(?,?,?,?,?)', (self.id, seq, phase, artifact, utc()))

    def stop(self, reason):
        self.update('stopped', stop_reason=reason)

    def totals(self):
        totals = {k: 0 for k in LIMITS}
        for row in self.db.execute('SELECT * FROM m09_operations WHERE campaign=?', (self.id,)):
            usage = json.loads(row['usage_json'] or row['reservation_json'])
            for key, val in usage.items():
                if key in totals:
                    totals[key] += val
        totals['active_wall_seconds'] = self.active_wall()
        return totals

    def cost_report(self):
        buckets = {'completed_actual': {}, 'reserved_unstarted': {}, 'started_unresolved': {}, 'indeterminate_upper_bound': {}}
        starts = 0
        for row in self.db.execute('SELECT * FROM m09_operations WHERE campaign=?',(self.id,)):
            name = {'completed':'completed_actual','reserved':'reserved_unstarted',
                    'started':'started_unresolved','indeterminate':'indeterminate_upper_bound'}[row['state']]
            values = json.loads(row['usage_json'] or row['reservation_json'])
            for key,value in values.items():
                buckets[name][key] = buckets[name].get(key,0)+value
            starts += row['kind']=='runner' and row['started_utc'] is not None
        return {**buckets, 'budget_committed_upper_bound':self.totals(),
                'physical_window_starts':starts, 'active_wall_seconds':self.active_wall(),
                'unresolved_usage_is_not_measured_expenditure':True}

    def active_wall(self):
        state = self.state()
        if state.get('paused') or self.campaign()['phase'] in ('finished', 'stopped'):
            return state['active_wall_seconds']
        return self.wall_base + max(0, self.clock()-self.started)

    def pause(self):
        if self.state().get('paused') or self.campaign()['phase'] in ('finished', 'stopped'):
            raise RuntimeError('Only active campaigns may pause')
        if self.db.execute("SELECT 1 FROM m09_operations WHERE campaign=? AND state='started'", (self.id,)).fetchone():
            raise RuntimeError('Cannot pause in-flight work')
        self.update(paused=True, pause_utc=utc(), pause_epoch=time.time())
        self.decision('idle_pause', {'active_wall_seconds': self.active_wall(), 'utc': self.state()['pause_utc']})

    def resume_pause(self):
        state = self.state()
        if not state.get('paused') or self.campaign()['phase'] in ('finished', 'stopped'):
            raise RuntimeError('No resumable planned idle pause')
        self.decision('idle_resume', {'idle_seconds': max(0, time.time()-state['pause_epoch']),
                                     'pause_utc': state['pause_utc'], 'resume_utc': utc()})
        self.wall_base, self.started = state['active_wall_seconds'], self.clock()
        self.update(paused=False)

    def reserve(self, kind, key, reservation):
        if (self.store.state / 'STOP').exists() and self.campaign()['phase'] not in ('finished','stopped'):
            self.stop('manual_STOP')
        if self.campaign()['phase'] in ('finished', 'stopped'):
            raise RuntimeError('Campaign stopped')
        allowed = {'planner': {'planner_requests', 'planner_tokens'},
                   'runner': {'runner_calls', 'runner_tokens', 'physical_windows'}}
        if kind not in allowed or set(reservation) - allowed[kind]:
            raise ValueError('Invalid ledger reservation')
        if self.state().get('paused'):
            raise RuntimeError('Campaign is in a planned idle pause')
        if any(type(v) is not int or v < 0 for v in reservation.values()):
            raise ValueError('Invalid resource count')
        totals = self.totals()
        for name, maximum in LIMITS.items():
            extra = 0
            if self.campaign()['phase'] in ('references', 'search'):
                extra = {'runner_tokens': 2304000, 'physical_windows': 144, 'runner_calls': 2160}.get(name, 0)
            if totals[name] + reservation.get(name, 0) + extra > maximum:
                self.stop('resource_ceiling:' + name)
                raise RuntimeError('Resource ceiling: ' + name)
        with self.db:
            self.db.execute('INSERT INTO m09_operations VALUES(?,?,?,?,?,?,?,?,?)',
                            (key, self.id, kind, 'reserved', canonical(reservation).decode(), None, utc(), None, None))
        return key

    def start(self, key):
        row = self.db.execute('SELECT * FROM m09_operations WHERE id=? AND campaign=?', (key, self.id)).fetchone()
        if (not row or row['state'] != 'reserved' or self.state().get('paused')
                or self.campaign()['phase'] in ('finished', 'stopped')
                or (self.store.state / 'STOP').exists()):
            raise RuntimeError('Only durably unstarted operations may start')
        if self.totals()['active_wall_seconds'] >= LIMITS['active_wall_seconds']:
            self.stop('active_wall_ceiling')
            raise RuntimeError('Active wall ceiling')
        with self.db:
            self.db.execute("UPDATE m09_operations SET state='started',started_utc=? WHERE id=?", (utc(), key))
        self.update()

    def complete(self, key, usage):
        row = self.db.execute('SELECT * FROM m09_operations WHERE id=? AND campaign=?', (key, self.id)).fetchone()
        if not row or row['state'] != 'started':
            raise RuntimeError('Receipt requires started operation')
        reservation = json.loads(row['reservation_json'])
        if set(usage) != set(reservation) or any(type(v) is not int or v < 0 or v > reservation[k] for k, v in usage.items()):
            self.indeterminate(key, 'usage_bound_violation')
            raise RuntimeError('Usage exceeds authoritative reservation')
        with self.db:
            self.db.execute("UPDATE m09_operations SET state='completed',usage_json=?,ended_utc=? WHERE id=?",
                            (canonical(usage).decode(), utc(), key))
        self.update()
        if self.totals()['active_wall_seconds'] >= LIMITS['active_wall_seconds']:
            self.stop('active_wall_ceiling')
            raise RuntimeError('Active wall ceiling')

    def indeterminate(self, key, reason):
        with self.db:
            self.db.execute("UPDATE m09_operations SET state='indeterminate',ended_utc=? WHERE id=? AND state IN ('reserved','started')", (utc(), key))
        self.stop(reason)

    def recover(self):
        rows = list(self.db.execute("SELECT id FROM m09_operations WHERE campaign=? AND state='started'", (self.id,)))
        if rows:
            with self.db:
                self.db.execute("UPDATE m09_operations SET state='indeterminate' WHERE campaign=? AND state='started'", (self.id,))
                state = self.state()
                state['stop_reason'] = 'indeterminate_operation_after_restart'
                self.db.execute("UPDATE m09_campaigns SET phase='stopped',state_json=? WHERE id=?", (canonical(state).decode(), self.id))
        incomplete = self.db.execute("SELECT 1 FROM m09_operations o JOIN m09_jobs j ON o.id=j.id WHERE o.campaign=? AND o.state='completed' AND j.result_hash IS NULL", (self.id,)).fetchone()
        incomplete_request = self.db.execute("SELECT 1 FROM m09_operations o JOIN m09_planner_requests q ON o.id=q.id LEFT JOIN m09_proposals p ON p.request_id=q.id WHERE o.campaign=? AND o.state='completed' AND p.id IS NULL", (self.id,)).fetchone()
        if incomplete or incomplete_request:
            state = self.state()
            state['stop_reason'] = 'completed_receipt_without_durable_result'
            with self.db:
                self.db.execute("UPDATE m09_campaigns SET phase='stopped',state_json=? WHERE id=?", (canonical(state).decode(), self.id))

    def scaffold(self, configuration):
        cat = self.put(interface_catalog(), 'interface_catalog')
        spec = self.put(configuration.spec.to_dict(), 'scaffold_spec')
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO m09_scaffolds VALUES(?,?,?,?,?,?)',
                            (configuration.scaffold_id, spec, configuration.compiler, configuration.renderer, cat, PROTOCOL))
        return configuration.scaffold_id

    def configuration(self, key):
        row = self.db.execute('SELECT * FROM m09_scaffolds WHERE id=?', (key,)).fetchone()
        if not row:
            raise ValueError('Unknown scaffold')
        result = compile_scaffold(ScaffoldSpecV1.from_dict(self.get(row['specification'])))
        if result.scaffold_id != key:
            raise ValueError('Stored compiler/scaffold identity drift')
        return result

    def decision(self, kind, value):
        artifact = self.put(value, 'decision:' + kind)
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO m09_decisions VALUES(?,?,?,?)', (artifact, self.id, kind, utc()))
        return artifact

    def close(self):
        self.store.close()


def forecast(samples, windows=368, replicates=2000, seed=9005):
    if not samples or any(s.get('tokens', -1) < 0 or s.get('wall_seconds', -1) < 0 for s in samples):
        raise ValueError('Forecast requires measured development samples')
    import random
    rng = random.Random(seed)
    totals = [(sum(s['tokens'] for s in draw), sum(s['wall_seconds'] for s in draw) + 8*180)
              for draw in (rng.choices(samples, k=windows) for _ in range(replicates))]
    tokens = sorted(t[0] for t in totals)[int((replicates-1)*.9)]
    seconds = sorted(t[1] for t in totals)[int((replicates-1)*.9)]
    return {'runner_tokens': tokens, 'active_wall_seconds': seconds,
            'passed': tokens < 4500000 and seconds < 32400, 'method': 'development-window bootstrap P90 plus Planner deadlines',
            'seed': seed, 'replicates': replicates, 'forecast_not_guarantee': True}
