"""Consistent SQLite exports and deterministic receipt replay; no model adapter."""
import hashlib
import json
from pathlib import Path
import zipfile

from ..artifacts import atomic_write
from ..contracts import canonical, digest
from .analysis import analyze
from .accounting import charge
from .boundary import isolated_output
from .classifier import classify
from .render import render, request_identity


def snapshot(ledger, study, scenarios, invariants=True, breach=False):
    config = ledger.study(study)
    registry = ledger.get(config['registry'])
    arms = json.loads(config['arms'])
    analysis = analyze(ledger.result_rows(study), scenarios, arms, registry,
                       invariants, breach, config['status'] == 'COMPLETE')
    metadata = {r['id']: ledger.get(r['value_hash']) for r in ledger.db.execute('SELECT * FROM m010_admission')}
    return {'format': 'm010-export-1', 'study': config, 'scenarios': list(scenarios), 'admission_and_freeze': metadata,
            'registry': registry, 'schedule': ledger.get(config['schedule']),
            'completion_catalog': ledger.completion_catalog(study),
            'pricing': ledger.get(config['pricing']), 'requests': ledger.requests(study),
            'probe': ledger.probe(), 'invariants': invariants, 'breach': breach, 'analysis': analysis}


def export(ledger, study, scenarios, destination, invariants=True, breach=False):
    destination = isolated_output(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with ledger.lock:
        value = snapshot(ledger, study, scenarios, invariants, breach)
        artifact_rows = list(ledger.db.execute('SELECT * FROM m010_artifacts ORDER BY hash'))
        artifacts = {r['hash']: canonical(ledger.get(r['hash'])) for r in artifact_rows}
        ledger.backup(destination / 'm010.sqlite')
    raw = canonical(value)
    atomic_write(destination / 'campaign.json', raw)
    with zipfile.ZipFile(destination / 'campaign.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, content in [('campaign.json', raw), *[('artifacts/' + k, v) for k, v in sorted(artifacts.items())]]:
            item = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(item, content)
    mode = value['study']['mode']
    description = ('Recording-stub study; zero research inference and Runner calls.' if mode == 'recording-stub'
                   else 'Separately authorized Planner feasibility study; zero Runner calls.')
    summary = ['# ' + study, '', description, '',
               '| Arm | Observed | Valid | Unobserved | Readiness |', '| --- | ---: | ---: | ---: | --- |']
    for arm, metrics in value['analysis']['arms'].items():
        summary.append('| {} | {} | {} | {} | {} |'.format(arm, metrics['observed'], metrics['valid'],
                       metrics['unobserved'], metrics['readiness']['classification']))
    atomic_write(destination / 'REPORT.md', ('\n'.join(summary) + '\n').encode())
    return {'campaign_hash': digest(value), 'archive_hash': hashlib.sha256((destination / 'campaign.zip').read_bytes()).hexdigest()}


def replay(archive_path):
    archive_path = isolated_output(archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        value = json.loads(archive.read('campaign.json'))
        if value.get('format') != 'm010-export-1':
            raise ValueError('M010_REPLAY_NAMESPACE')
        blobs = {}
        for name in archive.namelist():
            if name.startswith('artifacts/'):
                raw = archive.read(name)
                key = name.split('/')[1]
                if hashlib.sha256(raw).hexdigest() != key or len(name.split('/')) != 2:
                    raise ValueError('M010_REPLAY_ARTIFACT')
                blobs[key] = json.loads(raw)
    registry, scenarios, config = value['registry'], value['scenarios'], value['study']
    if digest(registry) != config['registry'] or digest(value['schedule']) != config['schedule'] or digest(value['pricing']) != config['pricing']:
        raise ValueError('M010_REPLAY_METADATA')
    lookup = {s['id']: s for s in scenarios}
    rows = []
    for q in value['requests']:
        s = lookup[q['scenario']]
        request = render(s, q['arm'])
        if q['id'] != request_identity(config['id'], s['id'], q['arm']) or digest(request) != q['request_hash'] or blobs[q['request_hash']] != request:
            raise ValueError('M010_REPLAY_REQUEST')
        response = blobs[q['response_hash']] if q['response_hash'] else None
        if q['account_hash']:
            account = charge(response, value['pricing'])
            if account != blobs[q['account_hash']]:
                raise ValueError('M010_REPLAY_ACCOUNTING')
        if not q['classification_hash']:
            continue
        result = classify(response, q['arm'], {s['parent_id']: registry[s['parent_id']]}, value['completion_catalog'])
        result.update(scenario_id=s['id'], family=s['family'], instance=s['instance'], parent_id=s['parent_id'])
        if result != blobs[q['classification_hash']]:
            raise ValueError('M010_REPLAY_CLASSIFICATION')
        result.update(account=account, latency_seconds=q['latency'], request_id=q['id'],
                      request_hash=q['request_hash'], response_hash=q['response_hash'], state=q['state'])
        rows.append(result)
    analysis = analyze(rows, scenarios, json.loads(config['arms']), registry,
                       value['invariants'], value['breach'], config['status'] == 'COMPLETE')
    if analysis != value['analysis']:
        raise ValueError('M010_REPLAY_ANALYSIS')
    return {'passed': True, 'campaign_hash': digest(value), 'analysis_hash': digest(analysis),
            'runner_calls': 0, 'research_inference': 0, 'requests': len(value['requests'])}
