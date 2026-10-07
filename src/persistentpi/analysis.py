"""Research-only deterministic summaries; never a source of Runner feedback."""
from collections import Counter, defaultdict
import json

from .contracts import digest


def controlled_factors(manifest):
    keys = ('protocol_version', 'execution_mode', 'seed', 'scaffold', 'model',
            'harness_test_limits', 'harness_hash', 'tools', 'toolset_version',
            'planner', 'memory_snapshot')
    return {key: manifest.get(key) for key in keys}


def validate_comparisons(records):
    scaling = [r for r in records if r['phase'] == 'scaling']
    if len({r['controlled_factors_hash'] for r in scaling}) > 1:
        raise ValueError('Scaling comparison changes factors other than attempt budget')
    cohorts = defaultdict(list)
    for run in scaling:
        cohorts[run['attempt_budget']].append((run['task'], run['task_hash'], run['replicate']))
    if any(len(rows) != len(set(rows)) for rows in cohorts.values()):
        raise ValueError('Duplicate trial in scaling comparison')
    if len({tuple(sorted(rows)) for rows in cohorts.values()}) > 1:
        raise ValueError('Scaling comparison requires identical task/replicate cohorts')
    repeats = defaultdict(set)
    for run in records:
        if run['phase'] == 'repeat':
            repeats[run['task']].add((run['controlled_factors_hash'], run['task_hash'], run['attempt_budget']))
    if any(len(factors) != 1 for factors in repeats.values()):
        raise ValueError('Repeated configurations must have identical controlled factors')


def nullable_sum(values):
    values = list(values)
    return None if any(value is None for value in values) else sum(values)


def analyse(store):
    manifests = {r['hash']: json.loads(r['json']) for r in store.db.execute('SELECT * FROM manifests')}
    records = []
    for run in store.db.execute("SELECT * FROM runs WHERE protocol_version='0.2' ORDER BY created_utc,id"):
        manifest = manifests[run['manifest_hash']]
        usage, budget = json.loads(run['usage_json']), json.loads(run['budget_json'])
        events = [dict(e) for e in store.db.execute('SELECT * FROM events WHERE run_id=? ORDER BY sequence', (run['id'],))]
        payloads = [(event['type'], json.loads(event['payload_json'])) for event in events]
        calls = [p for kind, p in payloads if kind == 'model_call_completed']
        requests = [p for kind, p in payloads if kind == 'model_request']
        telemetry = [call['telemetry'] for call in calls]
        if usage and usage.get('token_usage_kind') != 'measured':
            raise ValueError('Protocol 0.2 report cannot mix simulated usage into measured totals')
        categories = Counter(p['category'] for kind, p in payloads if kind == 'failure_classified')
        public = [r['outcome'] for r in store.db.execute("SELECT outcome FROM evaluations WHERE run_id=? AND split='public'", (run['id'],))]
        seconds = lambda key: nullable_sum(t.get(key) / 1e9 if t.get(key) is not None else None for t in telemetry)
        input_tokens, output_tokens = usage.get('input_tokens'), usage.get('output_tokens')
        generation = seconds('eval_duration')
        processing = seconds('prompt_eval_duration')
        end_to_end = next((p['end_to_end_seconds'] for kind, p in payloads if kind == 'trial_completed'), None)
        request_hashes = []
        for request in requests:
            # Full request receipts include the deadline; prompt hashes below do not.
            request_hashes.append(request['request_artifact'])
        records.append({'run_id': run['id'], 'experiment_id': run['experiment_id'],
            'task': run['task_id'], 'attempt_budget': budget['max_attempts'], 'replicate': run['replicate'],
            'phase': manifest.get('smoke_phase', 'scaling'), 'model': manifest['model']['identity'],
            'git_commit': manifest['git']['commit'], 'scaffold': manifest['scaffold'],
            'controlled_factors_hash': digest(controlled_factors(manifest)),
            'task_hash': next(t['task_hash'] for t in manifest['tasks'] if t['task_id'] == run['task_id']),
            'status': run['status'], 'stop_reason': run['stop_reason'], 'public_pass': 'pass' in public,
            'hidden_pass': run['evaluation_status'] == 'pass', 'hidden_outcome': run['evaluation_status'],
            'attempts_used': usage.get('attempts', 0), 'model_decisions': usage.get('model_decisions', 0),
            'tool_calls': usage.get('tool_calls', 0), 'valid_structured_outputs': usage.get('valid_structured_outputs', 0),
            'invalid_structured_outputs': usage.get('invalid_structured_outputs', 0),
            'backend_failures': usage.get('backend_failures', 0), 'input_tokens': input_tokens,
            'output_tokens': output_tokens, 'total_tokens': nullable_sum((input_tokens, output_tokens)),
            'known_input_tokens': sum(t['prompt_eval_count'] for t in telemetry if t.get('prompt_eval_count') is not None),
            'known_output_tokens': sum(t['eval_count'] for t in telemetry if t.get('eval_count') is not None),
            'calls_with_unknown_usage': sum(t.get('total_tokens') is None for t in telemetry),
            'runner_wall_seconds': usage.get('wall_seconds'), 'end_to_end_seconds': end_to_end,
            'request_wall_seconds': nullable_sum(t.get('wall_seconds') for t in telemetry),
            'backend_total_seconds': seconds('total_duration'), 'load_seconds': seconds('load_duration'),
            'prompt_processing_seconds': processing, 'generation_seconds': generation,
            'inference_seconds': nullable_sum((processing, generation)),
            'generation_tokens_per_second': output_tokens / generation if output_tokens is not None and generation else None,
            'failure_categories': dict(categories),
            'raw_output_hashes': [c['raw_output_artifact'] for c in calls],
            'prompt_hashes': [t.get('context', {}).get('prompt_hash') for t in telemetry],
            'request_artifacts': request_hashes})
    validate_comparisons(records)
    groups = defaultdict(list)
    for record in records:
        groups[(record['phase'], record['attempt_budget'])].append(record)
    aggregates = []
    additive = ('attempts_used', 'model_decisions', 'tool_calls', 'valid_structured_outputs',
                'invalid_structured_outputs', 'backend_failures', 'input_tokens', 'output_tokens',
                'total_tokens', 'known_input_tokens', 'known_output_tokens', 'calls_with_unknown_usage',
                'runner_wall_seconds', 'end_to_end_seconds', 'request_wall_seconds', 'backend_total_seconds',
                'load_seconds', 'prompt_processing_seconds', 'generation_seconds', 'inference_seconds')
    for (phase, budget), runs in sorted(groups.items()):
        identities = {json.dumps(r['model'], sort_keys=True) for r in runs}
        if len(identities) != 1:
            raise ValueError('Cannot aggregate different model/runtime/settings identities')
        row = {'phase': phase, 'attempt_budget': budget, 'tasks_attempted': len(runs),
               'public_pass_count': sum(r['public_pass'] for r in runs),
               'hidden_pass_count': sum(r['hidden_pass'] for r in runs),
               'success_rate': sum(r['hidden_pass'] for r in runs) / len(runs),
               'incomplete_runs': sum(r['status'] != 'finished' for r in runs)}
        row.update({key: nullable_sum(r[key] for r in runs) for key in additive})
        row['generation_tokens_per_second'] = row['output_tokens'] / row['generation_seconds'] if row['output_tokens'] is not None and row['generation_seconds'] else None
        categories = Counter()
        for run in runs:
            categories.update(run['failure_categories'])
        row['failure_categories'] = dict(categories)
        aggregates.append(row)
    scaling = sorted((row for row in aggregates if row['phase'] == 'scaling'), key=lambda row: row['attempt_budget'])
    comparisons = []
    for previous, current in zip(scaling, scaling[1:]):
        passed = lambda budget: {r['task'] for r in records if r['phase'] == 'scaling' and r['attempt_budget'] == budget and r['hidden_pass']}
        before, after = passed(previous['attempt_budget']), passed(current['attempt_budget'])
        delta = lambda key: current[key] - previous[key] if current[key] is not None and previous[key] is not None else None
        comparisons.append({'from_budget': previous['attempt_budget'], 'to_budget': current['attempt_budget'],
                            'recovered_tasks': sorted(after - before), 'lost_tasks': sorted(before - after),
                            'additional_tokens': delta('total_tokens'), 'additional_wall_seconds': delta('end_to_end_seconds')})
    repeats = defaultdict(list)
    for run in records:
        if run['phase'] == 'repeat':
            repeats[run['task']].append(run)
    repeated = []
    for task, runs in sorted(repeats.items()):
        repeated.append({'task': task, 'runs': len(runs), 'replicates': sorted(r['replicate'] for r in runs),
                         'distinct_output_traces': len({tuple(r['raw_output_hashes']) for r in runs}),
                         'distinct_prompt_traces': len({tuple(r['prompt_hashes']) for r in runs}),
                         'distinct_initial_prompts': len({r['prompt_hashes'][0] if r['prompt_hashes'] else None for r in runs}),
                         'distinct_results': len({(r['public_pass'], r['hidden_pass'], r['stop_reason']) for r in runs}),
                         'observed_output_variation': len({tuple(r['raw_output_hashes']) for r in runs}) > 1,
                         'determinism_guaranteed': False})
    return {'report_version': 1, 'label': 'M0.2 development smoke benchmark; non-baseline',
            'usage_kind': 'measured', 'aggregates': aggregates, 'comparisons': comparisons,
            'repeated_runs': repeated, 'runs': records,
            'interpretation': 'Development integration evidence only. No general scaling or model-capability conclusion.'}


def markdown(report):
    def cell(value):
        return 'unknown' if value is None else (f'{value:.3f}' if isinstance(value, float) else str(value))
    lines = ['# M0.2 development smoke benchmark', '', report['interpretation'], '',
             '| Phase | Budget | Tasks | Public pass | Hidden pass | Tokens | Wall seconds | Generation tok/s |',
             '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for row in report['aggregates']:
        values = [row[k] for k in ('phase', 'attempt_budget', 'tasks_attempted', 'public_pass_count',
                  'hidden_pass_count', 'total_tokens', 'end_to_end_seconds', 'generation_tokens_per_second')]
        lines.append('| ' + ' | '.join(map(cell, values)) + ' |')
    lines.extend(['', '## Attempt comparisons', '', '```json', json.dumps(report['comparisons'], indent=2),
                  '```', '', '## Repeated runs', '', '```json', json.dumps(report['repeated_runs'], indent=2),
                  '```', '', 'Full call counts, invalid outputs, timing components, failure categories and run identities are in summary.json.',
                  'Counts include interrupted runs. Unknown token/time totals remain null; known counts are lower bounds.',
                  'Repeated outputs are an observation from this subset, not a determinism guarantee.'])
    return '\n'.join(lines) + '\n'
