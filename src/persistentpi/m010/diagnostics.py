"""Passive category/type diagnostics; never repair or replace primary parser labels."""
from .config import CATEGORIES
from .mutation import FIELDS, ENUMS


def field_type(field, value):
    if field == 'source_preload':
        return type(value) is bool
    if field in ('inspect_calls', 'act_calls', 'read_allowance', 'recent_observations',
                 'stagnation', 'inspect_output', 'act_output', 'version'):
        return type(value) is int
    if field == 'context_fields':
        return isinstance(value, list) and all(isinstance(x, str) for x in value)
    if field == 'tool_descriptions':
        return isinstance(value, dict) and all(isinstance(x, str) for x in value.values())
    return isinstance(value, str)


def assess(value, arm):
    result = {'category_valid': None, 'field_types_valid': None}
    if not isinstance(value, dict):
        return result
    cats = value.get('targeted_categories' if arm == 'F0' else 'target_failures')
    if cats is not None:
        result['category_valid'] = isinstance(cats, list) and all(isinstance(c, str) and c in CATEGORIES for c in cats)
        if arm != 'F0' and result['category_valid']:
            result['category_valid'] = 1 <= len(cats) <= 11 and len(set(cats)) == len(cats)
    if arm == 'F0':
        spec = value.get('scaffold')
        if isinstance(spec, dict):
            result['field_types_valid'] = (all(field_type(k, v) for k, v in spec.items() if k in (*FIELDS, 'version'))
                and isinstance(value.get('parents'), list) and all(isinstance(p, str) for p in value['parents'])
                and isinstance(value.get('mutation'), str) and isinstance(value.get('rationale'), str)
                and isinstance(cats, list) and all(isinstance(c, str) for c in cats))
    else:
        ops = value.get('mutations')
        if isinstance(ops, list):
            result['field_types_valid'] = (all(isinstance(o, dict) and isinstance(o.get('field'), str)
                and 'value' in o and field_type(o['field'], o['value']) for o in ops)
                and isinstance(value.get('parent_id'), str) and isinstance(cats, list)
                and all(isinstance(c, str) for c in cats)
                and ('rationale' not in value or isinstance(value['rationale'], str)))
    return result
