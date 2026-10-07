"""Single authoritative writer, durable receipts, and explicit migrations."""
import datetime as dt
import hashlib
from pathlib import Path
import sqlite3
import sys
import time
import uuid

from .contracts import canonical


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


class Store:
    def __init__(self, state: Path, migrations: Path | None = None):
        self.state = Path(state).resolve()
        self.state.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.state / 'experiments.sqlite', timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('PRAGMA busy_timeout=10000')
        self.session = str(uuid.uuid4())
        source = Path(__file__).resolve().parents[2] / 'migrations'
        self.migrate(migrations or (source if source.exists() else Path(sys.prefix) / 'share/persistentpi/migrations'))

    def migrate(self, directory):
        self.db.execute('CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, name TEXT NOT NULL, sha256 TEXT NOT NULL)')
        self.db.commit()
        files = sorted(Path(directory).glob('[0-9][0-9][0-9]_*.sql'))
        if not files:
            raise ValueError('No database migrations found')
        known = {r['version']: dict(r) for r in self.db.execute('SELECT * FROM schema_migrations')}
        available = {int(p.name.split('_')[0]): p for p in files}
        if set(known) - set(available):
            raise ValueError('Database schema is newer than this installation')
        for version, path in available.items():
            raw = path.read_bytes()
            checksum = hashlib.sha256(raw).hexdigest()
            if version in known:
                if known[version]['sha256'] != checksum or known[version]['name'] != path.name:
                    raise ValueError('Applied migration changed: ' + path.name)
                continue
            if version != len(known) + 1:
                raise ValueError('Non-contiguous migration sequence')
            try:
                self.db.executescript('BEGIN IMMEDIATE;\n' + raw.decode() + '\n')
                self.db.execute('INSERT INTO schema_migrations VALUES(?,?,?)', (version, path.name, checksum))
                self.db.commit()
                known[version] = {'name': path.name, 'sha256': checksum}
            except Exception:
                self.db.rollback()
                raise

    def manifest(self, kind, value):
        raw = canonical(value)
        key = hashlib.sha256(raw).hexdigest()
        self.db.execute('INSERT OR IGNORE INTO manifests VALUES(?,?,?,?)', (key, kind, 1, raw.decode()))
        self.db.commit()
        return key

    def event(self, run_id, actor, event_type, payload):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            sequence = self.db.execute('SELECT COALESCE(MAX(sequence),0)+1 FROM events WHERE run_id=?', (run_id,)).fetchone()[0]
            self.db.execute('INSERT INTO events(run_id,sequence,utc,monotonic,session_id,actor,type,payload_version,payload_json) VALUES(?,?,?,?,?,?,?,?,?)',
                            (run_id, sequence, utc(), time.monotonic(), self.session, actor, event_type, 1, canonical(payload).decode()))
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise

    def request_stop(self, run_id):
        self.row(run_id)
        with self.db:
            changed = self.db.execute("UPDATE runs SET stop_requested=1 WHERE id=? AND status='running'", (run_id,)).rowcount
        if not changed:
            return False
        self.event(run_id, 'control_plane', 'stop_requested', {})
        return True

    def update_run(self, run_id, **values):
        allowed = {'status', 'stop_reason', 'usage_json', 'selected_checkpoint', 'initial_checkpoint',
                   'benchmark_score', 'evaluation_status', 'ended_utc', 'stop_requested'}
        if not values or set(values) - allowed:
            raise ValueError('Invalid run update')
        with self.db:
            columns = ','.join(k + '=?' for k in values)
            self.db.execute('UPDATE runs SET ' + columns + ' WHERE id=?', (*values.values(), run_id))

    def row(self, run_id):
        row = self.db.execute('SELECT * FROM runs WHERE id=?', (run_id,)).fetchone()
        if row is None:
            raise KeyError('Unknown run: ' + run_id)
        return dict(row)

    def close(self):
        self.db.close()
