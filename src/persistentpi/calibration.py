"""M0.3 public-only selection and separate final measurements."""
from collections import Counter, defaultdict
from dataclasses import replace
import json

from .analysis import nullable_sum
from .contracts import digest
from .interfaces import STAGES, registry


def split(task_ids):
    ordered = sorted(task_ids)
    if len(ordered) != 8 or len(set(ordered)) != 8:
        raise ValueError('M0.3 requires eight distinct immutable tasks')
    return ordered[:4], ordered[4:]


def condition(resolved, task_ids, protocol, edit, label, phase, prereg, budgets=(1,), replicate=0):
    if split([t.view.task_id for t in resolved.tasks]) != (prereg['calibration'], prereg['evaluation']):
        raise ValueError('Task split changed')
    if {t.view.task_id: t.hash for t in resolved.tasks} != prereg['task_hashes']:
        raise ValueError('Task versions changed since preregistration')
    tasks = tuple(t for t in resolved.tasks if t.view.task_id in task_ids)
    if {t.view.task_id for t in tasks} != set(task_ids):
        raise ValueError('Unknown task in condition')
    interface = {'output_protocol': protocol, 'edit_primitive': edit}
    model = {**resolved.manifest['model'], **interface,
             'prompt_version': protocol + ('-E1' if edit == 'E1' else '')}
    manifest = {**resolved.manifest, 'interface': interface, 'model': model, 'tools': registry(edit),
                'toolset_version': '0.3-' + edit, 'm03_phase': phase, 'm03_condition': label,
                'preregistration_hash': digest(prereg), 'attempt_budgets': list(budgets), 'replicate': replicate,
                'tasks': [t for t in resolved.manifest['tasks'] if t['task_id'] in task_ids]}
    return replace(resolved, manifest=manifest, tasks=tasks, attempt_budgets=budgets, replicate=replicate)


def public_records(store):
    """Does not query hidden evaluations, scores, or hidden result payloads."""
    records = []
    query = 'SELECT id,manifest_hash,task_id,status,stop_reason,budget_json,usage_json,replicate FROM runs WHERE protocol_version=\'0.3\' ORDER BY created_utc,id'
    for run in store.db.execute(query):
        manifest = json.loads(store.db.execute('SELECT json FROM manifests WHERE hash=?', (run['manifest_hash'],)).fetchone()[0])
        usage = json.loads(run['usage_json'])
        events = [(r['type'], json.loads(r['payload_json'])) for r in store.db.execute(
            "SELECT type,payload_json FROM events WHERE run_id=? AND actor != 'hidden_evaluator' ORDER BY sequence", (run['id'],))]
        funnels = [p for k, p in events if k == 'decision_funnel']
        calls = [p['telemetry'] for k,p in events if k == 'model_call_completed']
        if len(funnels) != usage.get('model_decisions', 0):
            raise ValueError('Incomplete decision funnel telemetry')
        counts = {s: sum(f['stages'][s] for f in funnels) for s in STAGES}
        public = [r[0] for r in store.db.execute("SELECT outcome FROM evaluations WHERE run_id=? AND split='public'", (run['id'],))]
        seconds = lambda key: nullable_sum(t[key] / 1e9 if t.get(key) is not None else None for t in calls)
        records.append({'run_id': run['id'], 'task': run['task_id'], 'phase': manifest['m03_phase'],
            'condition': manifest['m03_condition'], **manifest['interface'],
            'attempt_budget': json.loads(run['budget_json'])['max_attempts'], 'replicate': run['replicate'],
            'status': run['status'], 'stop_reason': run['stop_reason'], 'model_decisions': usage.get('model_decisions', 0),
            'tool_calls': usage.get('tool_calls', 0), 'attempts': usage.get('attempts', 0), 'counts': counts,
            'verification_reached': bool(public), 'public_pass': 'pass' in public,
            'invalid_actions': sum(not f['stages']['action_authorized'] for f in funnels),
            'exit_reasons': dict(Counter(f['reason'] for f in funnels)),
            'input_tokens': nullable_sum(t.get('prompt_eval_count') for t in calls),
            'output_tokens': nullable_sum(t.get('eval_count') for t in calls),
            'inference_seconds': nullable_sum((seconds('prompt_eval_duration'), seconds('eval_duration'))),
            'request_wall_seconds': nullable_sum(t.get('wall_seconds') for t in calls),
            'load_seconds': seconds('load_duration'),
            'wall_seconds': next((p['end_to_end_seconds'] for k,p in events if k == 'trial_completed'), None),
            'output_hashes': [p['raw_output_artifact'] for k,p in events if k == 'model_call_completed'],
            'action_hashes': [p['action_artifact'] for k,p in events if k == 'decision_completed'],
            'prompt_hashes': [t.get('context', {}).get('prompt_hash') for t in calls],
            'exit_families': dict(Counter(f['failure_family'] for f in funnels))})
    return records


def aggregate(records):
    if not records:
        raise ValueError('Empty comparison condition')
    counts = {s: sum(r['counts'][s] for r in records) for s in STAGES}
    n = sum(r['model_decisions'] for r in records)
    row = {'condition': records[0]['condition'], 'output_protocol': records[0]['output_protocol'],
        'edit_primitive': records[0]['edit_primitive'], 'tasks': len(records), 'model_decisions': n,
        'counts': counts, 'rates_per_decision': {s: counts[s] / n if n else 0 for s in counts},
        'verification_tasks': sum(r['verification_reached'] for r in records),
        'verification_task_rate': sum(r['verification_reached'] for r in records) / len(records),
        'public_pass_count': sum(r['public_pass'] for r in records),
        'authorized_rate': counts['action_authorized'] / n if n else 0,
        'applicable_rate': counts['action_applicable'] / n if n else 0,
        'invalid_count': sum(r['invalid_actions'] for r in records),
        'invalid_rate': sum(r['invalid_actions'] for r in records) / n if n else 0,
        'incomplete_runs': sum(r['status'] != 'finished' for r in records)}
    for key in ('input_tokens', 'output_tokens', 'inference_seconds', 'request_wall_seconds', 'wall_seconds', 'load_seconds', 'attempts', 'tool_calls'):
        row[key] = nullable_sum(r[key] for r in records)
    row['total_tokens'] = nullable_sum((row['input_tokens'], row['output_tokens']))
    pairs = [('parse_valid', 'schema_valid'), ('schema_valid', 'action_authorized'),
             ('action_authorized', 'action_applicable'), ('action_applicable', 'public_verification_reached'),
             ('public_verification_reached', 'public_verification_passed')]
    row['conversions'] = {a + ' -> ' + b: counts[b] / counts[a] if counts[a] else None for a,b in pairs}
    return row


def accepted(row, prereg):
    return (row['incomplete_runs'] == 0 and row['authorized_rate'] >= prereg['authorization_threshold']
            and row['verification_task_rate'] >= prereg['verification_task_threshold'])


def rank(row):
    return (-row['verification_task_rate'], -row['applicable_rate'], -row['public_pass_count'],
            row['invalid_rate'], row['total_tokens'] if row['total_tokens'] is not None else float('inf'),
            row['output_protocol'])


def select(rows, prereg):
    alternates = [r for r in rows if r['output_protocol'] != 'runner-json-1']
    eligible = sorted((r for r in alternates if accepted(r, prereg)), key=rank)
    return eligible[0] if eligible else None


def final_report(store, selection, prereg):
    # Call only AFTER selection has been durably recorded using public_records.
    records = public_records(store)
    for r in records:
        hidden = store.db.execute('SELECT evaluation_status FROM runs WHERE id=?', (r['run_id'],)).fetchone()[0]
        r['hidden_outcome'] = hidden
        r['hidden_pass'] = hidden == 'pass'
        measurement = store.db.execute("SELECT payload_json FROM events WHERE run_id=? AND type='hidden_funnel_result'", (r['run_id'],)).fetchone()
        if measurement:
            value = json.loads(measurement[0])
            r['counts']['hidden_evaluation_passed'] = int(bool(value['call_id']) and value['hidden_evaluation_passed'])
    groups = defaultdict(list)
    for r in records:
        groups[(r['phase'], r['condition'], r['attempt_budget'])].append(r)
    rows = []
    for (phase, label, budget), runs in sorted(groups.items()):
        row = aggregate(runs)
        row.update(phase=phase, attempt_budget=budget, hidden_pass_count=sum(r['hidden_pass'] for r in runs),
                   hidden_pass_rate=sum(r['hidden_pass'] for r in runs) / len(runs),
                   accepted=accepted(row, prereg))
        rows.append(row)
    repeats = []
    for task in prereg['evaluation'][:2]:
        runs = [r for r in records if r['phase'] == 'repeat' and r['task'] == task]
        if runs:
            repeats.append({'task': task, 'runs': len(runs),
                'distinct_outputs': len({tuple(r['output_hashes']) for r in runs}),
                'distinct_actions': len({tuple(r['action_hashes']) for r in runs}),
                'distinct_prompts': len({tuple(r['prompt_hashes']) for r in runs}),
                'distinct_outcomes': len({(r['public_pass'], r['hidden_outcome'], r['stop_reason']) for r in runs}),
                'input_tokens': [r['input_tokens'] for r in runs], 'output_tokens': [r['output_tokens'] for r in runs],
                'inference_seconds': [r['inference_seconds'] for r in runs], 'wall_seconds': [r['wall_seconds'] for r in runs],
                'determinism_guaranteed': False})
    scaling = {b: {r['task'] for r in records if r['phase'] == 'scaling' and r['attempt_budget'] == b and r['hidden_pass']} for b in (1,3,5)}
    return {'report_version': 1, 'preregistration': prereg, 'selection': selection, 'aggregates': rows,
        'runs': records, 'repeats': repeats, 'recovered': {'1_to_3': sorted(scaling[3] - scaling[1]), '3_to_5': sorted(scaling[5] - scaling[3])}}
