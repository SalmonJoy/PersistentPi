"""Public-only M0.6 selection, followed by separately requested hidden measurement."""
from collections import defaultdict
import json

from .analysis import nullable_sum
from .artifacts import Artifacts
from .interfaces import parse_output


def public_records(store):
    records = []
    artifacts = Artifacts(store)
    query = ("SELECT id,manifest_hash,task_id,status,stop_reason,usage_json FROM runs "
             "WHERE protocol_version='0.3' ORDER BY created_utc,id")
    for run in store.db.execute(query):
        manifest = json.loads(store.db.execute('SELECT json FROM manifests WHERE hash=?',
                                             (run['manifest_hash'],)).fetchone()[0])
        if 'm06_policy' not in manifest:
            continue
        events = [(r['type'], json.loads(r['payload_json'])) for r in store.db.execute(
            "SELECT type,payload_json FROM events WHERE run_id=? AND actor != 'hidden_evaluator' ORDER BY sequence",
            (run['id'],))]
        admitted = [p for k, p in events if k == 'decision_completed']
        decisions = []
        inspected = False
        edit_after_inspection = False
        for kind, payload in events:
            if kind == 'model_call_completed' and payload['valid_structured_output']:
                raw = artifacts.get(payload['raw_output_artifact']).decode('utf-8')
                action, stages, _, error = parse_output(raw, manifest['interface']['output_protocol'],
                                                       manifest['interface']['edit_primitive'])
                if action is None or not stages['schema_valid'] or error:
                    raise ValueError('Stored schema-valid action cannot be reconstructed')
                decisions.append(action.to_dict())
                edit_after_inspection |= action.tool == 'edit_file' and inspected
            elif kind == 'control_action' and payload['tool'] == 'read_file' and payload['accepted']:
                inspected = True
        controls = [p for k, p in events if k == 'control_action']
        calls = [p['telemetry'] for k, p in events if k == 'model_call_completed']
        public = [r[0] for r in store.db.execute(
            "SELECT outcome FROM evaluations WHERE run_id=? AND split='public'", (run['id'],))]
        usage = json.loads(run['usage_json'])
        reads = [a['arguments'].get('path') for a in decisions if a['tool'] == 'read_file']
        edits = [a for a in decisions if a['tool'] == 'edit_file']
        accepted = [p for p in controls if p['tool'] == 'edit_file' and p['accepted']]
        rejects = [p for p in controls if p['tool'] == 'edit_file' and not p['accepted']]
        verification = [p for k, p in events if k == 'verification_started']
        seconds = lambda key: nullable_sum(t[key] / 1e9 if t.get(key) is not None else None for t in calls)
        initialized = next(p for k, p in events if k == 'control_initialized')
        final = next(p for k, p in events if k == 'control_final')
        act = (final['phase'] == 'ACT' or
               (final['policy'] == 'C2' and final['successful_reads'] >= final['read_budget']))
        records.append({'run_id': run['id'], 'model': manifest['m06_model'],
            'policy': manifest['m06_policy'], 'phase': manifest['m06_phase'], 'task': run['task_id'],
            'scaffold_hash': manifest['scaffold']['scaffold_hash'], 'status': run['status'],
            'stop_reason': run['stop_reason'], 'reads': len(reads), 'unique_reads': len(set(reads)),
            'repeated_reads': len(reads) - len(set(reads)),
            'successful_reads': sum(p['accepted'] for p in controls if p['tool'] == 'read_file'),
            'rejected_redundant_reads': sum(p['rejection'] == 'redundant_read' for p in controls),
            'rejected_unavailable_actions': sum(p['rejection'] == 'unavailable_action' for p in controls),
            'ACT': act, 'edit_selections': len(edits),
            'give_up_selections': sum(a['tool'] == 'finish' for a in decisions),
            'edit_after_inspection': edit_after_inspection,
            'schema_valid_selections': len(decisions), 'admitted_selections': len(admitted),
            'unadmitted_selections': len(decisions) - len(admitted),
            'edit_attempt': bool(edits), 'edit_generated': bool(accepted),
            'accepted_edits': len(accepted), 'rejected_edits': len(rejects),
            'candidate_checkpoints': len(verification), 'verification_reached': bool(verification),
            'public_pass': 'pass' in public, 'public_outcomes': public,
            'public_infrastructure_outcomes': [p for p in public if p not in ('pass', 'fail')],
            'useful_actions': len(accepted) + len(verification),
            'model_calls': usage.get('model_decisions', 0), 'tool_calls': usage.get('tool_calls', 0),
            'input_tokens': nullable_sum(t.get('prompt_eval_count') for t in calls),
            'output_tokens': nullable_sum(t.get('eval_count') for t in calls),
            'inference_seconds': nullable_sum((seconds('prompt_eval_duration'), seconds('eval_duration'))),
            'request_wall_seconds': nullable_sum(t.get('wall_seconds') for t in calls),
            'wall_seconds': next((p['end_to_end_seconds'] for k, p in events if k == 'trial_completed'), None),
            'controller_initial': initialized, 'controller_final': final,
            'raw_output_hashes': [p['raw_output_artifact'] for k, p in events if k == 'model_call_completed']})
    return records


def aggregate(records, plan):
    groups = defaultdict(list)
    for r in records:
        groups[(r['model'], r['policy'], r['phase'])].append(r)
    result = []
    for (model, policy, phase), runs in sorted(groups.items()):
        n = len(runs)
        row = {'model': model, 'policy': policy, 'phase': phase, 'tasks': n,
               'incomplete_runs': sum(r['status'] != 'finished' for r in runs),
               'scaffold_hashes': sorted({r['scaffold_hash'] for r in runs})}
        for name in ('reads', 'unique_reads', 'repeated_reads', 'successful_reads',
                     'rejected_redundant_reads', 'rejected_unavailable_actions', 'edit_selections',
                     'give_up_selections', 'accepted_edits', 'rejected_edits', 'candidate_checkpoints',
                     'useful_actions', 'model_calls', 'tool_calls', 'schema_valid_selections',
                     'admitted_selections', 'unadmitted_selections'):
            row[name] = sum(r[name] for r in runs)
        for name, key in (('ACT_tasks', 'ACT'), ('transition_tasks', 'edit_after_inspection'),
                          ('edit_attempt_tasks', 'edit_attempt'), ('edit_generation_tasks', 'edit_generated'),
                          ('verification_tasks', 'verification_reached'), ('public_passes', 'public_pass')):
            row[name] = sum(r[key] for r in runs)
        for rate, count in (('transition_rate', 'transition_tasks'), ('edit_attempt_rate', 'edit_attempt_tasks'),
                            ('edit_generation_rate', 'edit_generation_tasks'), ('verification_reach_rate', 'verification_tasks'),
                            ('public_solve_rate', 'public_passes')):
            row[rate] = row[count] / n
        row['mean_reads_per_task'] = row['reads'] / n
        row['useful_action_efficiency'] = row['useful_actions'] / row['model_calls'] if row['model_calls'] else 0
        for name in ('input_tokens', 'output_tokens', 'inference_seconds', 'request_wall_seconds', 'wall_seconds'):
            row[name] = nullable_sum(r[name] for r in runs)
        row['total_tokens'] = nullable_sum((row['input_tokens'], row['output_tokens']))
        row['operational_gate'] = (row['edit_attempt_rate'] >= plan['edit_attempt_threshold'] and
                                   row['verification_reach_rate'] >= plan['verification_threshold'])
        result.append(row)
    return result


def select(rows, plan):
    eligible = [r for r in rows if r['model'] == plan['primary_model'] and r['phase'] == 'evaluation'
                and r['operational_gate'] and r['incomplete_runs'] == 0]
    def rank(r):
        return (-r['public_passes'], -r['verification_reach_rate'], -r['edit_generation_rate'],
                -r['useful_action_efficiency'], r['model_calls'],
                r['total_tokens'] if r['total_tokens'] is not None else float('inf'),
                plan['conditions'].index(r['policy']))
    ordered = sorted(eligible, key=rank)
    return {'policy': ordered[0]['policy'] if ordered else None, 'model': plan['primary_model'],
            'rule': plan['selection'], 'ranked_eligible': [r['policy'] for r in ordered],
            'reason': 'First eligible policy by preregistered public-only ordering.' if ordered else
                      'No primary-model policy meets both operational thresholds.'}


def final_measurement(store, records, rows, selection):
    # Invoke only after public-only selection has been durably written.
    enriched = [dict(r) for r in records]
    for r in enriched:
        outcome = store.db.execute('SELECT evaluation_status FROM runs WHERE id=?', (r['run_id'],)).fetchone()[0]
        r.update(hidden_outcome=outcome, hidden_pass=outcome == 'pass')
    measured = [dict(r) for r in rows]
    for row in measured:
        matches = [r for r in enriched if (r['model'], r['policy'], r['phase']) == (row['model'], row['policy'], row['phase'])]
        row['hidden_passes'] = sum(r['hidden_pass'] for r in matches)
        row['hidden_solve_rate'] = row['hidden_passes'] / row['tasks']
    return {'selection': selection, 'aggregates': measured, 'runs': enriched}
