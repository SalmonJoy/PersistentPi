"""Pure synthetic observations; no task loader, trace reader or evaluator."""
from copy import deepcopy
import platform
import random

from ..contracts import digest
from .config import FAMILIES, BUCKETS
from .frozen import parent_registry

GENERATOR = 'M0.10A-synthetic-v1'
PROFILES = (
    (1, 0, 44, {'NO_OP': 32}), (0, 0, 40, {'MALFORMED': 28}),
    (0, 0, 44, {'UNAUTHORIZED': 32}), (1, 0, 36, {'PATCH_MISMATCH': 24}),
    (1, 0, 36, {'INVALID_SYNTAX': 24}), (0, 0, 36, {'OUTPUT_LIMIT': 24}),
    (2, 1, 48, {'NO_OP': 12}),
    (1, 0, 44, {'NO_OP': 8, 'PATCH_MISMATCH': 8, 'INVALID_SYNTAX': 8, 'OUTPUT_LIMIT': 8}))
REMAINING = {'runner_calls': 5520, 'runner_tokens': 6000000, 'planner_requests': 8,
             'planner_tokens': 200000, 'physical_windows': 368, 'active_wall_seconds': 43200}


def synthetic_hash(*parts):
    return digest((GENERATOR, *parts))


def generate(registry=None):
    registry = registry or parent_registry()
    parents = {row['name']: row for row in registry.values()}
    result = []
    for index, family in enumerate(FAMILIES):
        formed, passed, base_calls, base_counts = PROFILES[index]
        for j in range(3):
            sid = 'syn-' + synthetic_hash(family, j)[:24]
            calls = base_calls + 4 * j
            high = family == 'high_cost'
            input_per_call = (600 + 50 * j) if high else (320 + 40 * j)
            output_per_call = (192 + 32 * j) if high else (64 + 16 * j)
            inference = round(calls * ((2 + .25 * j) if high else (.5 + .1 * j)), 3)
            metric = {'tasks': 4, 'formations': formed, 'public_passes': passed,
                'formation_families': int(formed > 0), 'passing_families': int(passed > 0),
                'runner_calls': calls, 'runner_tokens': calls * (input_per_call + output_per_call),
                'inference_seconds': inference,
                'wall_seconds': round(inference + .1 * calls + .05 * formed, 3)}
            metrics = {name: deepcopy(metric) for name in BUCKETS}
            aggregate = {key: round(sum(m[key] for m in metrics.values()), 3)
                         if isinstance(value, float) else sum(m[key] for m in metrics.values())
                         for key, value in metric.items()}
            counts = dict(base_counts)
            dominant = 'NO_OP' if family == 'mixed_failures' else next(iter(counts))
            counts[dominant] += 2 * j
            counts['BUDGET'] = 4 - formed
            if formed > passed:
                counts['PUBLIC_FAIL'] = formed - passed
            totals = {k: v * 8 for k, v in counts.items() if v}
            chosen = sorted(totals, key=lambda k: (-totals[k], k))[:2]
            excerpts = []
            for k, category in enumerate(chosen):
                old = synthetic_hash(family, j, 'event', k, 'old')
                new = old if category == 'NO_OP' else synthetic_hash(family, j, 'event', k, 'new')
                event_calls = 10 + j + k
                excerpts.append({'action_category': 'READ' if family == 'excessive_read' else 'EDIT',
                    'rejection_category': category, 'repeat_count': 2 + j, 'content': '<source omitted>',
                    'task_hash': synthetic_hash(family, j, 'event', k), 'old_hash': old, 'new_hash': new,
                    'old_bytes': 256 + 64 * j, 'new_bytes': 256 + 64 * j,
                    'old_equals_new': old == new, 'before_phase': 'ACT', 'after_phase': 'ACT',
                    'calls': event_calls, 'input_tokens': event_calls * input_per_call,
                    'output_tokens': event_calls * output_per_call,
                    'inference_seconds': round(inference * event_calls / calls, 3),
                    'wall_seconds': round(metric['wall_seconds'] * event_calls / calls, 3), 'result_ok': False})
            parent = parents['B0' if (index + j) % 2 == 0 else 'B1']
            observation = {'policy': 'protocol-only-1', 'aggregate': aggregate, 'families': metrics,
                'failure_counts': dict(sorted(totals.items())), 'excerpts': excerpts, 'archive_decisions': []}
            payload = {'parent': {'id': parent['id'], 'spec': deepcopy(parent['spec'])},
                'observation': observation, 'archive': [{'id': parent['id'], 'metrics': aggregate, 'tasks': 32}],
                'remaining': deepcopy(REMAINING)}
            result.append({'id': sid, 'family': family, 'instance': j, 'parent_id': parent['id'],
                           'payload': payload, 'observation_hash': digest(observation)})
    if len(result) != 24 or len({r['id'] for r in result}) != 24:
        raise ValueError('M010_SCENARIO_COUNT')
    return tuple(result)


def schedule(scenarios):
    ids = sorted(s['id'] for s in scenarios)
    if len(ids) != 24 or len(set(ids)) != 24:
        raise ValueError('M010_SCHEDULE_SCENARIOS')
    random.Random(42).shuffle(ids)
    value = {'seed': 42, 'python_version': platform.python_version(), 'scenario_order': ids,
             'unit': 'paired temporal scenario block'}
    return {**value, 'hash': digest(value)}
