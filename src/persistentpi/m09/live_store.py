"""Search-only capabilities; qualification is metadata, never executable material."""
import json
from pathlib import Path
import time
import uuid

from ..artifacts import Artifacts
from ..contracts import canonical, digest
from ..telemetry import Store, utc
from .cohorts import manifest, split_search
from .storage import OptimizationStore, WINDOW, execution_hash


class SearchAccess:
    def __init__(self, search):
        self._search = tuple(search)

    def request(self, name, phase=None, frozen=False):
        if name == 'search':
            return self._search
        if name in ('screen', 'remaining'):
            return split_search(self._search)[name == 'remaining']
        raise PermissionError('Search-only capability denies non-search material')


class SearchStore(OptimizationStore):
    def __init__(self, folder, config, search, qualification_manifest, campaign_id=None, clock=time.monotonic):
        root = Path(__file__).resolve().parents[3]
        resolved = Path(folder).resolve()
        if resolved.is_relative_to(root) and not resolved.is_relative_to(root/'.local'):
            raise ValueError('Mutable state must be outside evidence/code')
        if config.get('protocol_version') != '0.6' or config.get('window') != WINDOW:
            raise ValueError('Frozen window/protocol changed')
        if config.get('operational_launch', {}).get('target') != 'SEARCH_ONLY':
            raise ValueError('Search-only launch required')
        q = qualification_manifest
        if (set(q) != {'cohort', 'rows', 'hash'} or q.get('cohort') != 'qualification' or len(q.get('rows', ())) != 48
                or any(set(r) != {'task_id', 'task_hash', 'public_hash', 'family', 'template', 'parameter'} for r in q['rows'])
                or digest({'cohort': q['cohort'], 'rows': q['rows']}) != q['hash']):
            raise ValueError('Qualification identity-only manifest mismatch')
        self.store = Store(resolved)
        self.db, self.artifacts = self.store.db, Artifacts(self.store)
        self.clock, self.started = clock, clock()
        self.config, self.search = config, tuple(search)
        self.qualification_manifest = json.loads(canonical(q))
        try:
            manifests = {'search': manifest(search, 'search'), 'qualification': q}
            fingerprint = execution_hash()
            if campaign_id is None:
                if self.db.execute('SELECT COUNT(*) FROM m09_campaigns').fetchone()[0]:
                    raise ValueError('Explicit resume identity required')
                self.id = str(uuid.uuid4())
                mh = self.store.manifest('m09-preregistration', config)
                state = {'round': 1, 'slot': 1, 'active_wall_seconds': 0, 'stop_reason': None,
                         'execution_hash': fingerprint, 'target': 'SEARCH_ONLY'}
                with self.db:
                    self.db.execute('INSERT INTO experiments VALUES(?,?,?,?)', (self.id, mh, '0.6', utc()))
                    self.db.execute('INSERT INTO m09_campaigns VALUES(?,?,?,?,?,?)',
                                    (self.id, '0.6', 'references', mh, canonical(state).decode(), utc()))
                screen_ids = {t.task_id for t in split_search(search)[0]}
                for name, m in manifests.items():
                    artifact = self.put(m, 'cohort_manifest')
                    with self.db:
                        self.db.execute('INSERT INTO m09_cohorts VALUES(?,?,?,?)', (self.id, name, m['hash'], artifact))
                        if name == 'search':
                            for t in search:
                                self.db.execute('INSERT INTO m09_members VALUES(?,?,?,?,?,?,?)',
                                                (self.id, m['hash'], t.task_id, t.task_hash, t.family, t.template,
                                                 'screen' if t.task_id in screen_ids else 'remaining'))
            else:
                self.id = campaign_id
                if self.campaign()['config_hash'] != digest(config) or self.state()['execution_hash'] != fingerprint:
                    raise ValueError('Resume configuration/execution drift')
                for name, m in manifests.items():
                    row = self.db.execute('SELECT hash FROM m09_cohorts WHERE campaign=? AND name=?', (self.id, name)).fetchone()
                    if not row or row[0] != m['hash']:
                        raise ValueError('Resume cohort drift')
                self.recover()
            self.wall_base = self.state()['active_wall_seconds']
        except BaseException:
            self.store.close()
            raise

    @property
    def qualification(self):
        raise PermissionError('No qualification material capability exists')

    def update(self, phase=None, **changes):
        if phase is not None and phase not in ('references', 'search', 'finished', 'stopped'):
            raise PermissionError('Search-only phase graph cannot enter qualification/final')
        current = self.campaign()['phase']
        if current in ('finished', 'stopped') and phase not in (None, current):
            raise PermissionError('Terminal search cannot reopen')
        return super().update(phase, **changes)

    def assert_barrier(self):
        search_hash = manifest(self.search, 'search')['hash']
        jobs = self.db.execute('SELECT COUNT(*) FROM m09_jobs WHERE campaign=? AND cohort_hash!=?',
                               (self.id, search_hash)).fetchone()[0]
        hidden = self.db.execute("SELECT COUNT(*) FROM evaluations WHERE split='hidden'").fetchone()[0]
        if jobs or hidden:
            raise RuntimeError('Search-only isolation violation')
        result = {'qualification_executions': 0, 'final_executions': 0, 'hidden_evaluations': 0,
                  'qualification_material_capability': False, 'target': 'SEARCH_ONLY', 'passed': True}
        self.decision('search_only_barrier', result)
        return result
