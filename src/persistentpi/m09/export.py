"""Consistent backup plus deterministic archive/replay, including protocol 0.6 tables."""
import csv
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import zipfile

from ..artifacts import atomic_write
from ..contracts import canonical, digest
from .analysis import Result, best, entry_gate, full_search, metrics, qualification_gate
from .cohorts import PublicTask
from .spec import compile_scaffold
from .spec import parse_proposal
from .disclosure import validate_projection
from .screening import validate_candidate


def export(store, output):
    output = Path(output)
    if output.exists():
        raise ValueError('Export path exists')
    snapshot = sqlite3.connect(':memory:')
    store.db.backup(snapshot)
    snapshot.row_factory = sqlite3.Row
    try:
        tables = [r[0] for r in snapshot.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        data = {name: sorted([dict(r) for r in snapshot.execute('SELECT * FROM ' + name)], key=canonical) for name in tables}
        files = {'research.json': canonical({'version': 'm09-export-1', 'tables': data})}
        for table, rows in data.items():
            text = io.StringIO(newline='')
            columns = [r[1] for r in snapshot.execute('PRAGMA table_info(' + table + ')')]
            writer = csv.DictWriter(text, fieldnames=columns, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
            files[table + '.csv'] = text.getvalue().encode()
        for r in data['artifacts']:
            files['artifacts/' + r['hash']] = store.artifacts.get(r['hash'])
    finally:
        snapshot.close()
    files['checksums.json'] = canonical({n: hashlib.sha256(raw).hexdigest() for n, raw in files.items()})
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_STORED) as archive:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o600 << 16
            archive.writestr(info, raw)
    atomic_write(output, buffer.getvalue())
    return {'sha256': hashlib.sha256(buffer.getvalue()).hexdigest(), 'bytes': len(buffer.getvalue())}


def replay(path, search, qualification, reference_configs):
    with zipfile.ZipFile(path) as archive:
        checks = json.loads(archive.read('checksums.json'))
        if set(archive.namelist()) != set(checks) | {'checksums.json'} or len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError('Archive file inventory mismatch')
        for name, key in checks.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != key:
                raise ValueError('Archive checksum mismatch')
        data = json.loads(archive.read('research.json'))['tables']
        def artifact(key):
            raw = archive.read('artifacts/' + key)
            if hashlib.sha256(raw).hexdigest() != key:
                raise ValueError('Artifact identity mismatch')
            return json.loads(raw)
        configurations = {row['id']: compile_scaffold(artifact(row['specification'])) for row in data['m09_scaffolds']}
        if any(key != configuration.scaffold_id for key, configuration in configurations.items()):
            raise ValueError('Scaffold reconstruction mismatch')
        operations = {r['id']: r for r in data['m09_operations']}
        results = {r['id']: Result(**artifact(r['result_hash'])) for r in data['m09_jobs'] if r['result_hash']}
        if len(data['m09_campaigns']) != 1 or any(r['split'] == 'hidden' for r in data['evaluations']):
            raise ValueError('Unexpected campaign or hidden result in M0.9 replay')
        campaign = data['m09_campaigns'][0]
        config_row = next(r for r in data['manifests'] if r['hash'] == campaign['config_hash'])
        config = json.loads(config_row['json'])
        if digest(config) != campaign['config_hash']:
            raise ValueError('Preregistration reconstruction mismatch')
        disclosures = {r['id']: r for r in data['m09_disclosures']}
        responses = {r['request_id']: r for r in data['m09_planner_responses']}
        proposals = {r['request_id']: r for r in data['m09_proposals']}
        seen = {c.scaffold_id for c in reference_configs.values()}
        replayed_slots = {}
        for row in sorted(data['m09_planner_requests'], key=lambda r: (r['round'], r['slot'])):
            payload = artifact(row['request_hash'])
            body = json.loads(payload['messages'][1]['content'])
            disclosure_row = disclosures[row['disclosure_id']]
            disclosure = artifact(disclosure_row['id'])
            observation = validate_projection(artifact(disclosure_row['observation_hash']))
            if (body['observation'] != observation or disclosure['request'] != digest(payload)
                    or disclosure['observation'] != disclosure_row['observation_hash']):
                raise ValueError('Exact Planner disclosure reconstruction mismatch')
            proposal = proposals.get(row['id'])
            response = responses.get(row['id'])
            if proposal is None:
                if operations[row['id']]['state'] not in ('reserved', 'indeterminate') and campaign['phase'] != 'stopped':
                    raise ValueError('Unresolved Planner proposal')
                continue
            if response is None or operations[row['id']]['state'] != 'completed':
                raise ValueError('Proposal has no completed response receipt')
            raw = artifact(response['response_hash'])
            allowed = {a['scaffold_id'] for a in data['m09_archive']
                       if any(d['kind'] == 'archive' and d['created_utc'] <= operations[row['id']]['started_utc']
                              and artifact(d['id'])['scaffold'] == a['scaffold_id'] for d in data['m09_decisions'])}
            candidate, envelope, status = None, None, 'invalid'
            try:
                envelope = parse_proposal(raw['message']['content'], allowed)
                candidate = compile_scaffold(envelope.scaffold)
                validate_candidate(candidate, config['runner'])
                status = 'duplicate' if candidate.scaffold_id in seen else 'valid'
            except (ValueError, TypeError, KeyError, RecursionError):
                candidate, envelope = None, None
            if status != proposal['validation']:
                raise ValueError('Proposal validation reconstruction mismatch')
            if candidate is not None:
                if candidate.scaffold_id != proposal['scaffold_id'] or artifact(proposal['envelope_hash']) != envelope.to_dict():
                    raise ValueError('Proposal identity/envelope reconstruction mismatch')
                parents = sorted(p['scaffold_id'] for p in data['m09_parents'] if p['proposal_id'] == proposal['id'])
                if parents != list(envelope.parents):
                    raise ValueError('Parent lineage reconstruction mismatch')
                seen.add(candidate.scaffold_id)
            else:
                if proposal['scaffold_id'] is not None:
                    raise ValueError('Invalid proposal unexpectedly carries scaffold identity')
            validations = [artifact(v['id']) for v in data['m09_validations'] if v['proposal_id'] == proposal['id']]
            if validations != [{'proposal': proposal['id'], 'state': status, 'reason': proposal['reason']}]:
                raise ValueError('Validation receipt reconstruction mismatch')
            usage = artifact(response['usage_hash'])
            total = usage['input_tokens'] + usage['output_tokens'] + (0 if usage['reasoning_in_output'] else usage['reasoning_tokens'])
            if json.loads(operations[row['id']]['usage_json']) != {'planner_requests': 1, 'planner_tokens': total}:
                raise ValueError('Planner physical cost reconstruction mismatch')
            replayed_slots[(row['round'], row['slot'])] = candidate if status == 'valid' else None
        from .cohorts import manifest, split_search
        search_hash = manifest(search, 'search')['hash']
        screen_ids = {t.task_id for t in split_search(search)[0]}
        entries = []
        for job in data['m09_jobs']:
            if job['result_hash']:
                result = results[job['id']]
                if (result.receipt_id != job['id'] or result.scaffold_id != job['scaffold_id']
                        or result.task_id != job['task_id'] or result.cohort_hash != job['cohort_hash']):
                    raise ValueError('Job/physical result identity mismatch')
                expected = {'runner_calls': result.calls, 'runner_tokens': result.input_tokens+result.output_tokens, 'physical_windows': 1}
                if operations[job['id']]['state'] != 'completed' or json.loads(operations[job['id']]['usage_json']) != expected:
                    raise ValueError('Runner physical cost reconstruction mismatch')
        for row in data['m09_archive']:
            config = configurations[row['scaffold_id']]
            rs = [r for r in results.values() if r.scaffold_id == config.scaffold_id and r.cohort_hash == search_hash]
            full = full_search([r for r in rs if r.task_id in screen_ids], [r for r in rs if r.task_id not in screen_ids], search, config.scaffold_id)
            saved = artifact(row['score_hash'])
            if saved['metrics'] != metrics(full) or saved['results'] != [r.to_dict() for r in full]:
                raise ValueError('Archived full score differs from receipt union')
            if row['generated']:
                entries.append((config, full))
        for decision in data['m09_decisions']:
            if decision['kind'] == 'round':
                saved = artifact(decision['id'])
                comparable = [(c, [r for r in results.values() if r.scaffold_id == c.scaffold_id
                                   and r.cohort_hash == search_hash and r.task_id in screen_ids])
                              for slot in (1, 2) if (c := replayed_slots.get((saved['round'], slot))) is not None]
                winner = best(comparable)
                if saved['winner'] != (winner[0].scaffold_id if winner else None):
                    raise ValueError('Screen ranking reconstruction mismatch')
        finalist = best(entries)
        frozen = data['m09_finalists']
        gate = None
        if frozen:
            if len(frozen) != 1 or not finalist or frozen[0]['scaffold_id'] != finalist[0].scaffold_id:
                raise ValueError('Finalist selection reconstruction mismatch')
            reference_results = [[r for r in results.values() if r.scaffold_id == config.scaffold_id and r.cohort_hash == search_hash]
                                 for config in reference_configs.values()]
            if not entry_gate(finalist[1], *reference_results)['passed']:
                raise ValueError('Finalist entry gate reconstruction failed')
            qhash = manifest(qualification, 'qualification')['hash']
            qresults = [[r for r in results.values() if r.scaffold_id == config.scaffold_id and r.cohort_hash == qhash]
                        for config in (finalist[0], *reference_configs.values())]
            if all(len(rs) == 48 for rs in qresults):
                gate = qualification_gate(*qresults)
                saved_gates = [artifact(d['id']) for d in data['m09_decisions'] if d['kind'] == 'qualification_gate']
                if saved_gates != [gate]:
                    raise ValueError('Qualification decision reconstruction mismatch')
        cost, committed = {}, {}
        for op in operations.values():
            for name, val in json.loads(op['usage_json'] or op['reservation_json']).items():
                committed[name] = committed.get(name,0)+val
                if op['state']=='completed':
                    cost[name] = cost.get(name, 0) + val
        if len(results) != len({r.receipt_id for r in results.values()}):
            raise ValueError('Physical receipt duplicated in replay')
        state = json.loads(campaign['state_json'])
        cost['active_wall_seconds'] = state['active_wall_seconds']
        return {'passed': True, 'full_entries': len(data['m09_archive']),
                'physical_windows': len(results), 'physical_cost': cost,
                'qualification': gate, 'proposals': len(data['m09_proposals']),
                'disclosures': len(data['m09_disclosures']), 'inference': False,
                'termination': state['stop_reason'], 'phase': campaign['phase'],
                'logical_full_search_tasks': len(data['m09_archive'])*32,
                'budget_committed_upper_bound': committed,
                'physical_window_starts':sum(o['kind']=='runner' and o['started_utc'] is not None for o in operations.values()),
                'unresolved_usage_is_not_measured_expenditure':True}
