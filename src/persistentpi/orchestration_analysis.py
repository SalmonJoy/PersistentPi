"""Protocol-0.4 public gate and overhead metrics; hidden measurement comes later."""
from collections import defaultdict
import json

from .analysis import nullable_sum
from .artifacts import Artifacts
from .interfaces import parse_output


def ratio(numerator, denominator):
    return numerator / denominator if denominator and numerator is not None else None


def public_records(store):
    artifacts = Artifacts(store)
    result = []
    for run in store.db.execute("SELECT id,manifest_hash,task_id,status,stop_reason,usage_json FROM runs WHERE protocol_version='0.4' ORDER BY created_utc,id"):
        manifest = json.loads(store.db.execute('SELECT json FROM manifests WHERE hash=?', (run['manifest_hash'],)).fetchone()[0])
        if 'm07_condition' not in manifest:
            continue
        events = [(e['type'], json.loads(e['payload_json'])) for e in store.db.execute(
            "SELECT type,payload_json FROM events WHERE run_id=? AND actor != 'hidden_evaluator' ORDER BY sequence", (run['id'],))]
        calls = [p for k, p in events if k == 'model_call_completed']
        selections = []
        for call in calls:
            if call['valid_structured_output']:
                action, _, _, error = parse_output(artifacts.get(call['raw_output_artifact']).decode(),
                    manifest['interface']['output_protocol'], manifest['interface']['edit_primitive'])
                if action is None or error:
                    raise ValueError('Cannot reconstruct logged valid selection')
                selections.append(action)
        admitted = [p for k, p in events if k == 'decision_completed']
        admitted_edits = [p for p in admitted if json.loads(artifacts.get(p['action_artifact']))['tool'] == 'edit_file']
        edits = [p for k, p in events if k == 'candidate_edit_accepted']
        candidates = [p for k, p in events if k == 'candidate_checkpoint']
        verifications = [p for k, p in events if k == 'verification_started']
        completed = [p for k, p in events if k == 'candidate_attempt_completed']
        outcomes = [p['outcome'] for p in completed]
        usage = json.loads(run['usage_json'])
        telemetry = [p['telemetry'] for p in calls]
        seconds = lambda key: nullable_sum(t[key] / 1e9 if t.get(key) is not None else None for t in telemetry)
        row = {'run_id': run['id'], 'task': run['task_id'], 'condition': manifest['m07_condition'],
            'phase': manifest['m07_phase'], 'candidate_budget': manifest['candidate_attempt_budget'],
            'scaffold_hash': manifest['scaffold']['scaffold_hash'], 'status': run['status'], 'stop_reason': run['stop_reason'],
            'model_calls': usage['model_decisions'], 'tool_calls': usage['tool_calls'],
            'reads': sum(a.tool == 'read_file' for a in selections),
            'edit_proposals': sum(a.tool == 'edit_file' for a in selections),
            'accepted_edits': len(edits), 'rejected_edits': len(admitted_edits) - len(edits),
            'unadmitted_selections': len(selections) - len(admitted),
            'candidate_checkpoints': len(candidates), 'candidate_attempts': len(completed),
            'verification_count': len(verifications), 'verification_reached': bool(verifications),
            'verified_edit_occurrences': len({p['source_call_id'] for p in completed}),
            'unverified_edits': len(edits) - len({p['source_call_id'] for p in completed}),
            'give_up': sum(a.tool == 'finish' for a in selections),
            'control_decisions': sum(a.tool in ('finish', 'run_public_tests') for a in selections),
            'semantic_decisions': sum(a.tool in ('read_file', 'edit_file') for a in selections),
            'unclassified_decisions': usage['model_decisions'] - sum(a.tool in ('read_file', 'edit_file', 'finish', 'run_public_tests') for a in selections),
            'automatic_verifications': sum(k == 'automatic_public_verification' for k, _ in events),
            'public_outcomes': outcomes, 'public_pass': 'pass' in outcomes,
            'public_infrastructure_outcomes': [o for o in outcomes if o not in ('pass', 'fail')],
            'recovered_after_first_failure': bool(outcomes) and outcomes[0] == 'fail' and 'pass' in outcomes[1:],
            'input_tokens': nullable_sum(t.get('prompt_eval_count') for t in telemetry),
            'output_tokens': nullable_sum(t.get('eval_count') for t in telemetry),
            'inference_seconds': nullable_sum((seconds('prompt_eval_duration'), seconds('eval_duration'))),
            'wall_seconds': next((p['end_to_end_seconds'] for k, p in events if k == 'trial_completed'), None),
            'action_hashes': [p['action_artifact'] for p in admitted],
            'request_hashes': [p['request_artifact'] for k, p in events if k == 'model_request']}
        row['tokens'] = nullable_sum((row['input_tokens'], row['output_tokens']))
        row['control_action_fraction'] = ratio(row['control_decisions'], row['model_calls'])
        for numerator, prefix in (('model_calls', 'calls'), ('tokens', 'tokens')):
            row[prefix + '_per_candidate'] = ratio(row[numerator], row['accepted_edits'])
            row[prefix + '_per_verification'] = ratio(row[numerator], row['verification_count'])
        result.append(row)
    return result


def aggregate(records, plan):
    groups = defaultdict(list)
    for r in records:
        groups[(r['phase'], r['condition'], r['candidate_budget'])].append(r)
    result = []
    for (phase, condition, budget), runs in sorted(groups.items()):
        row = {'phase': phase, 'condition': condition, 'candidate_budget': budget, 'tasks': len(runs),
               'incomplete_runs': sum(r['status'] != 'finished' for r in runs)}
        for k in ('model_calls', 'tool_calls', 'reads', 'edit_proposals', 'accepted_edits', 'rejected_edits',
                  'candidate_checkpoints', 'candidate_attempts', 'verification_count', 'give_up', 'control_decisions',
                  'unadmitted_selections', 'unverified_edits', 'automatic_verifications',
                  'semantic_decisions', 'unclassified_decisions'):
            row[k] = sum(r[k] for r in runs)
        for k in ('input_tokens', 'output_tokens', 'tokens', 'inference_seconds', 'wall_seconds'):
            row[k] = nullable_sum(r[k] for r in runs)
        row.update(accepted_edit_tasks=sum(r['accepted_edits'] > 0 for r in runs),
                   verification_tasks=sum(r['verification_reached'] for r in runs),
                   public_passes=sum(r['public_pass'] for r in runs),
                   recovered_after_first_failure=[r['task'] for r in runs if r['recovered_after_first_failure']])
        row['accepted_edit_rate'] = row['accepted_edit_tasks'] / len(runs)
        row['verification_reach_rate'] = row['verification_tasks'] / len(runs)
        row['public_solve_rate'] = row['public_passes'] / len(runs)
        row['engineering_gate'] = (row['accepted_edit_rate'] >= plan['accepted_edit_threshold'] and
                                   row['verification_reach_rate'] >= plan['verification_threshold'] and
                                   row['incomplete_runs'] == 0)
        row['control_action_fraction'] = ratio(row['control_decisions'], row['model_calls'])
        for numerator, prefix in (('model_calls', 'calls'), ('tokens', 'tokens')):
            row[prefix + '_per_candidate'] = ratio(row[numerator], row['accepted_edits'])
            row[prefix + '_per_verification'] = ratio(row[numerator], row['verification_count'])
        result.append(row)
    return result


def scaling_gate(rows):
    primary = [r for r in rows if r['phase'] == 'primary']
    eligible = (len(primary) == 2 and {r['condition'] for r in primary} == {'V0', 'V1'}
                and all(r['tasks'] == 8 and r['incomplete_runs'] == 0 and r['candidate_budget'] == 1 for r in primary))
    v1 = next((r for r in primary if r['condition'] == 'V1' and r['candidate_budget'] == 1), None)
    return {'eligible': bool(eligible and v1 and v1['engineering_gate']),
            'reason': 'V1 requires >=4/8 accepted-edit tasks and >=4/8 verification tasks; public correctness and hidden results are not inputs.',
            'V1': v1}


def final_measurement(store, public, rows, gate):
    records = [dict(r) for r in public]
    measured = [dict(r) for r in rows]
    for r in records:
        outcome = store.db.execute('SELECT evaluation_status FROM runs WHERE id=?', (r['run_id'],)).fetchone()[0]
        r.update(hidden_outcome=outcome, hidden_pass=outcome == 'pass')
    for row in measured:
        matches = [r for r in records if (r['phase'], r['condition'], r['candidate_budget']) == (row['phase'], row['condition'], row['candidate_budget'])]
        row['hidden_passes'] = sum(r['hidden_pass'] for r in matches)
        row['hidden_solve_rate'] = row['hidden_passes'] / row['tasks']
    curve = sorted((r for r in measured if r['condition'] == 'V1' and r['phase'] != 'calibration'), key=lambda r: r['candidate_budget'])
    if curve:
        baseline = curve[0]
        b_runs = [r for r in records if r['phase'] == 'primary' and r['condition'] == 'V1']
        for row in curve:
            current = [r for r in records if r['phase'] == row['phase'] and r['condition'] == 'V1' and r['candidate_budget'] == row['candidate_budget']]
            for kind in ('public', 'hidden'):
                baseline_solves = {r['task'] for r in b_runs if r[kind + '_pass']}
                solves = {r['task'] for r in current if r[kind + '_pass']}
                new = sorted(solves - baseline_solves)
                row['new_' + kind + '_solves_vs_1'] = new
                for cost in ('tokens', 'inference_seconds', 'wall_seconds'):
                    incremental = row[cost] - baseline[cost] if row[cost] is not None and baseline[cost] is not None else None
                    row['incremental_' + cost + '_vs_1'] = incremental
                    row[cost + '_per_new_' + kind + '_solve'] = ratio(incremental, len(new))
    return {'protocol_version': '0.4', 'gate': gate, 'aggregates': measured, 'runs': records,
            'scaling_curve': curve, 'scaling_skipped': not gate['eligible']}
