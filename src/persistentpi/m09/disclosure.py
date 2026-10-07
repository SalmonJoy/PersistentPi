"""Positive-allowlist protocol observations; raw task payloads never pass through."""
from collections import Counter
import hashlib
import math
import re

from ..contracts import canonical, digest
from ..m08.benchmark import FAMILIES
from .analysis import metrics

VERSION = 'protocol-only-1'
CATEGORIES = ('NO_OP', 'PATCH_MISMATCH', 'INVALID_SYNTAX', 'MALFORMED', 'UNAUTHORIZED',
              'OUTPUT_LIMIT', 'BUDGET', 'GIVE_UP', 'PUBLIC_FAIL', 'PUBLIC_PASS', 'OTHER')
ACTIONS = {'read_file': 'READ', 'edit_file': 'EDIT', 'replace_file': 'EDIT', 'finish': 'GIVE_UP'}
ERRORS = {'Edit is empty, unchanged or too large': 'NO_OP', 'Replacement is unchanged': 'NO_OP',
          'Edit requires exactly one matching occurrence': 'PATCH_MISMATCH',
          'Automatic verification tool reservation exhausted': 'BUDGET',
          'Automatic verification reservation exhausted': 'BUDGET',
          'Invalid Python syntax': 'INVALID_SYNTAX',
          'Replacement file size limit exceeded': 'OUTPUT_LIMIT',
          'Workspace byte budget exceeded': 'OUTPUT_LIMIT',
          'Action unavailable in current control state.': 'UNAUTHORIZED',
          'Verification is Supervisor-triggered': 'UNAUTHORIZED',
          'Protected or undeclared path': 'UNAUTHORIZED'}


def number(value, integer=False):
    if type(value) not in ((int,) if integer else (int, float)) or not math.isfinite(value) or value < 0:
        return 0
    return value


def excerpt(event):
    action = event.get('action', {})
    action = action if isinstance(action, dict) else {}
    arguments = action.get('arguments', {})
    arguments = arguments if isinstance(arguments, dict) else {}
    result = event.get('result', {})
    result = result if isinstance(result, dict) else {}
    category = event.get('category')
    if category not in CATEGORIES:
        category = ERRORS.get(result.get('error') if isinstance(result.get('error'), str) else '', 'OTHER')
    output = {'action_category': ACTIONS.get(action.get('tool') if isinstance(action.get('tool'), str) else '', 'OTHER'),
              'rejection_category': category, 'repeat_count': number(event.get('repeat_count'), True),
              'content': '<source omitted>', 'task_hash': digest(event.get('task_hash', ''))}
    if type(result.get('ok')) is bool:
        output['result_ok'] = result['ok']
    for name in ('old', 'new', 'content'):
        value = arguments.get(name)
        if isinstance(value, str):
            raw = value.encode()
            output[name + '_bytes'] = len(raw)
            output[name + '_hash'] = hashlib.sha256(raw).hexdigest()
    if all(isinstance(arguments.get(k), str) for k in ('old', 'new')):
        output['old_equals_new'] = arguments['old'] == arguments['new']
    for key in ('before_phase', 'after_phase'):
        if event.get(key) in ('INSPECT', 'ACT'):
            output[key] = event[key]
    for key in ('calls', 'input_tokens', 'output_tokens', 'inference_seconds', 'wall_seconds'):
        output[key] = number(event.get(key), key.endswith('tokens') or key == 'calls')
    if len(canonical(output)) > 2048:
        raise ValueError('Typed excerpt exceeds cap')
    return output


def project(results=(), events=(), archive_decisions=()):
    projected = [excerpt(e) for e in events if isinstance(e, dict)]
    counts = Counter(e['rejection_category'] for e in projected
                     if e.get('result_ok') is not True and e['rejection_category'] != 'PUBLIC_PASS')
    ordered = sorted(projected, key=lambda e: (-counts.get(e['rejection_category'],0), e['task_hash'], digest(e)))
    selected = []
    for item in ordered:
        if item not in selected:
            selected.append(item)
        if len(selected) == 2:
            break
    families = {f: metrics([r for r in results if r.family == f]) for f in FAMILIES}
    decisions = [d for d in archive_decisions if d in ('ACCEPTED', 'REJECTED', 'DUPLICATE', 'FULL', 'FINALIST', 'STOP')]
    return {'policy': VERSION, 'aggregate': metrics(results), 'families': families,
            'failure_counts': dict(sorted(counts.items())), 'excerpts': selected, 'archive_decisions': decisions}


SYSTEM = ('You optimize a frozen small coding Runner using protocol metrics only. '
          'Return exactly one JSON ProposalEnvelope. No fences or executable code. '
          'Use only the supplied ScaffoldSpec fields/catalog and known parents. '
          'Propose general scaffold changes, never task answers, lookup tables or resource changes.')


def request(observation, parent, archive, remaining, contract):
    # This API consumes only output of project(), not arbitrary telemetry dictionaries.
    if set(observation) != {'policy', 'aggregate', 'families', 'failure_counts', 'excerpts', 'archive_decisions'}:
        raise ValueError('Disclosure contract mismatch')
    validate_projection(observation)
    from .manager import proposal_contract
    from .storage import LIMITS
    if contract != proposal_contract():
        raise ValueError('Unapproved proposal contract')
    if (set(remaining) - set(LIMITS)
            or any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in remaining.values())):
        raise ValueError('Invalid remaining-budget disclosure')
    for item in archive:
        if (not isinstance(item, dict) or set(item) != {'id', 'metrics', 'tasks'}
                or not isinstance(item['id'], str) or not re.fullmatch('[0-9a-f]{64}', item['id'])
                or item['tasks'] != 32):
            raise ValueError('Invalid archive disclosure')
        candidate = {**project(), 'aggregate': item['metrics']}
        validate_projection(candidate)
    value = {'parent': {'id': parent.scaffold_id, 'spec': parent.spec.to_dict()},
             'observation': observation, 'archive': archive, 'remaining': remaining, 'contract': contract}
    while True:
        payload = {'model': 'glm-5.3', 'messages': [{'role': 'system', 'content': SYSTEM},
                   {'role': 'user', 'content': canonical(value).decode()}], 'stream': False,
                   'options': {'temperature': 0, 'seed': 42, 'num_predict': 4096}, 'think': 'high'}
        if len(canonical(payload)) <= 16384:
            return payload
        if value['observation']['excerpts']:
            value['observation'] = {**value['observation'], 'excerpts': value['observation']['excerpts'][:-1]}
        elif value['archive']:
            value['archive'] = value['archive'][:-1]
        else:
            raise ValueError('Mandatory Planner request exceeds byte cap')


def validate_projection(value):
    keys = set(metrics(()))
    def safe_metrics(row):
        return (isinstance(row, dict) and set(row) == keys
                and all(type(x) in (int, float) and math.isfinite(x) and x >= 0 for x in row.values()))
    if value['policy'] != VERSION or not safe_metrics(value['aggregate']):
        raise ValueError('Disclosure aggregate invalid')
    if set(value['families']) != set(FAMILIES) or not all(safe_metrics(v) for v in value['families'].values()):
        raise ValueError('Disclosure families invalid')
    if (set(value['failure_counts']) - set(CATEGORIES)
            or any(type(v) is not int or v < 0 for v in value['failure_counts'].values())):
        raise ValueError('Disclosure taxonomy invalid')
    if len(value['excerpts']) > 2:
        raise ValueError('Disclosure excerpt count')
    for item in value['excerpts']:
        allowed = {'action_category', 'rejection_category', 'repeat_count', 'content', 'task_hash',
                   'old_bytes', 'old_hash', 'new_bytes', 'new_hash', 'content_bytes', 'content_hash',
                   'old_equals_new', 'before_phase', 'after_phase', 'calls', 'input_tokens', 'output_tokens',
                   'inference_seconds', 'wall_seconds', 'result_ok'}
        if set(item) - allowed or len(canonical(item)) > 2048:
            raise ValueError('Disclosure excerpt fields')
        for key, val in item.items():
            if key.endswith('_hash'):
                valid = isinstance(val, str) and re.fullmatch('[0-9a-f]{64}', val)
            elif key == 'content':
                valid = val == '<source omitted>'
            elif key == 'action_category':
                valid = val in ('READ', 'EDIT', 'GIVE_UP', 'OTHER')
            elif key == 'rejection_category':
                valid = val in CATEGORIES
            elif key.endswith('_phase'):
                valid = val in ('INSPECT', 'ACT')
            elif key in ('old_equals_new','result_ok'):
                valid = type(val) is bool
            else:
                valid = type(val) in (int, float) and math.isfinite(val) and val >= 0
            if not valid:
                raise ValueError('Disclosure excerpt value')
    if any(v not in ('ACCEPTED', 'REJECTED', 'DUPLICATE', 'FULL', 'FINALIST', 'STOP') for v in value['archive_decisions']):
        raise ValueError('Disclosure decisions invalid')
    return value
