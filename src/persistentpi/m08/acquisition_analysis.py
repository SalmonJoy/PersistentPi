"""Preregistered, public-only acquisition diagnostics; no model or verifier calls."""
import ast
from collections import Counter
import json

from ..contracts import canonical
from .analysis import COSTS, bootstrap_difference


def normalized_edit(action):
    args = action['arguments']
    try:
        return (args['path'], ast.dump(ast.parse(args['old']), include_attributes=False),
                ast.dump(ast.parse(args['new']), include_attributes=False))
    except (KeyError, TypeError, SyntaxError, ValueError, RecursionError):
        return None


def request_bytes(action):
    return canonical({'tool': action['tool'], 'arguments': action['arguments']})


def diagnostics(events, original):
    calls, tokens, noops, seen, streak, max_streak = 0, 0, 0, set(), 0, 0
    first, ast_first, first_tokens, preceding = None, None, None, None
    repetitions, rejected, pending, pending_streak = 0, 0, None, None
    eligible, changed, normalized_n, normalized_changed = 0, 0, 0, 0
    source = original
    for event in events:
        kind, payload = event['type'], event['payload']
        if kind == 'decision_started':
            calls += 1
            if pending is not None:
                eligible += 1
        elif kind == 'model_call_completed':
            telemetry = payload['telemetry']
            tokens += (telemetry.get('prompt_eval_count') or 0) + (telemetry.get('eval_count') or 0)
        elif kind == 'decision_completed':
            action = payload['action']
            if pending is not None:
                if action['tool'] == 'edit_file':
                    changed += request_bytes(action) != request_bytes(pending)
                    previous, following = normalized_edit(pending), normalized_edit(action)
                    if previous is not None and following is not None:
                        normalized_n += 1
                        normalized_changed += previous != following
                pending = None
        elif kind == 'action_completed':
            action, result = payload['action'], payload['result']
            if action['tool'] != 'edit_file':
                continue
            args = action['arguments']
            if not result['ok']:
                rejected += 1
            noop = not result['ok'] and args.get('old') == args.get('new')
            if noop:
                noops += 1
                key = request_bytes(action)
                repetitions += key in seen
                seen.add(key)
                streak = streak + 1 if pending_streak == key else 1
                pending_streak = key
                max_streak = max(max_streak, streak)
                pending = action
            else:
                streak = 0
                pending_streak = None
            if result['ok']:
                after = source.replace(args['old'], args['new'], 1)
                if after != source and first is None:
                    first, first_tokens, preceding = calls, tokens, noops
                if ast.dump(ast.parse(after)) != ast.dump(ast.parse(source)) and ast_first is None:
                    ast_first = calls
                source = after
    return {'decisions_to_first_changed_edit': first,
            'decisions_to_first_ast_changed_edit': ast_first,
            'tokens_to_first_changed_edit': first_tokens,
            'noop_count_before_first_changed_edit': preceding,
            'total_noops': noops, 'repeated_noops': repetitions,
            'max_consecutive_noops': max_streak, 'rejected_edits': rejected,
            'post_rejection': {'eligible': eligible, 'byte_changed': changed,
                              'normalized_supported': normalized_n,
                              'normalized_changed': normalized_changed}}


def gate(rows, thresholds):
    complete = len(rows) == 16 and all(r.get(a) is not None for r in rows for a in ('A', 'B'))
    a = sum(bool(r.get('A') and r['A']['formed']) for r in rows)
    b = sum(bool(r.get('B') and r['B']['formed']) for r in rows)
    families = {r['family'] for r in rows if r.get('B') and r['B']['formed']}
    failures = sum(bool(r.get('B') and r['B']['public'] == 'fail') for r in rows)
    checks = {'B_formations': b >= thresholds['B_formations'],
              'net_formations': b-a >= thresholds['net_formations'],
              'B_families': len(families) >= thresholds['B_families'],
              'B_public_failures': failures >= thresholds['B_public_failures']}
    return {'complete': complete, 'A_formations': a, 'B_formations': b,
            'net_formations': b-a, 'B_families': len(families), 'B_public_failures': failures,
            'checks': checks, 'qualifies': complete and all(checks.values())}


def analyze(rows, config, complete=True):
    result = {'gate': gate(rows, config['gate']), 'conditions': {}, 'paired': dict(Counter(
        'B_win' if r['B']['formed'] and not r['A']['formed'] else
        'A_win' if r['A']['formed'] and not r['B']['formed'] else
        'both_formed' if r['A']['formed'] else 'neither_formed'
        for r in rows if r.get('A') and r.get('B')))}
    result['gate']['qualifies'] &= complete
    for arm in ('A', 'B'):
        records = [r[arm] for r in rows if r.get(arm)]
        formed = sum(r['formed'] for r in records)
        usage = {k: sum(r['cost'].get(k, 0) for r in records) for k in COSTS}
        projection = {k: sum(r['diagnostics']['post_rejection'][k] for r in records)
                      for k in ('eligible', 'byte_changed', 'normalized_supported', 'normalized_changed')}
        projection['byte_change_rate'] = projection['byte_changed']/projection['eligible'] if projection['eligible'] else None
        projection['normalized_change_rate'] = (projection['normalized_changed']/projection['normalized_supported']
                                                if projection['normalized_supported'] else None)
        result['conditions'][arm] = {'completed_windows': len(records), 'formations': formed,
            'formation_rate': formed/16, 'formation_rate_denominator': '16_planned_tasks',
            'public': dict(Counter(r['public'] for r in records if r['formed'])),
            'families': dict(Counter(r['family'] for r in rows if r.get(arm) and r[arm]['formed'])),
            'noops': sum(r['diagnostics']['total_noops'] for r in records),
            'repeated_noops': sum(r['diagnostics']['repeated_noops'] for r in records),
            'ast_changed_candidates': sum(r['diagnostics']['decisions_to_first_ast_changed_edit'] is not None for r in records),
            'post_rejection': projection, 'window_cost': usage,
            'cost_per_formation': {k: v/formed if formed else None for k, v in usage.items()}}
    if complete and result['gate']['complete']:
        opts = config['bootstrap']
        result['paired_effect'] = (result['gate']['B_formations']-result['gate']['A_formations'])/16
        result['exploratory_95pct_ci'] = bootstrap_difference(rows, lambda r: int(r['B']['formed']),
            lambda r: int(r['A']['formed']), replicates=opts['replicates'], seed=opts['seed'])
    else:
        result['paired_effect'] = result['exploratory_95pct_ci'] = None
    return result
