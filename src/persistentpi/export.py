"""Deterministic research archive from one consistent SQLite read snapshot."""
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

from .artifacts import atomic_write
from .contracts import canonical

TABLES = ('schema_migrations', 'manifests', 'experiments', 'runs', 'attempts',
          'evaluations', 'events', 'artifacts', 'm08_campaigns', 'm08_windows',
          'm08_initial_prefixes', 'm08_branches', 'm08_receipts', 'm08_scores', 'm08_retired_cohorts', 'm08_overhead')


def export(manager, output):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('Export destination already exists')
    if output.is_relative_to(manager.artifacts.folder) or output.is_relative_to(manager.store.state / 'workspaces'):
        raise ValueError('Export destination overlaps protected state')
    db = manager.store.db
    db.execute('BEGIN')
    try:
        data = {table: [dict(row) for row in db.execute('SELECT * FROM ' + table + ' ORDER BY 1')]
                for table in TABLES}
        files = {'research.json': canonical({'export_version': 1, 'tables': data})}
        for table, rows in data.items():
            buffer = io.StringIO(newline='')
            columns = [row[1] for row in db.execute('PRAGMA table_info(' + table + ')')]
            writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
            files[table + '.csv'] = buffer.getvalue().encode('utf-8')
        for artifact in data['artifacts']:
            files['artifacts/' + artifact['hash']] = manager.artifacts.get(artifact['hash'])
    finally:
        db.rollback()
    files['checksums.json'] = canonical({name: hashlib.sha256(raw).hexdigest() for name, raw in files.items()})
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o600 << 16
            archive.writestr(info, raw)
    atomic_write(output, buffer.getvalue())
    return {'path': str(output), 'sha256': hashlib.sha256(buffer.getvalue()).hexdigest(),
            'runs': len(data['runs'])}
