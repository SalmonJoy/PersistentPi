"""One semantic vocabulary for JSON and native tool arguments."""
from copy import deepcopy
from dataclasses import dataclass
import re

from ..contracts import canonical
from ..interfaces import decode_json
from .config import CATEGORIES
from .frozen import ScaffoldSpecV1, compile_scaffold, parent_spec

FIELDS = ('system_text', 'interface', 'tool_descriptions', 'context_fields', 'source_preload',
          'controller', 'read_allowance', 'recent_observations', 'rejection_feedback', 'retry',
          'stagnation', 'inspect_calls', 'act_calls', 'inspect_output', 'act_output')
CONTEXT = ('task', 'tools', 'budget', 'control', 'observations', 'source', 'public_cases')
MANDATORY = {'task', 'tools', 'budget', 'control'}
TOOLS = ('read_file', 'edit_file', 'replace_file', 'finish')
INTERFACES = tuple(e + ':' + p for e in ('E0', 'E1')
                   for p in ('runner-dsl-1', 'runner-json-1', 'runner-json-schema-1'))
ENUMS = {'interface': INTERFACES, 'controller': ('C0', 'C1', 'C2', 'C3'),
         'read_allowance': (0, 1, 2), 'recent_observations': tuple(range(5)),
         'rejection_feedback': ('generic', 'precise'), 'retry': ('stop', 'retry'),
         'stagnation': (0, 2, 3), 'inspect_output': (128, 256, 512, 1024),
         'act_output': (128, 256, 512, 1024)}
TEXT_SCHEMA = {'type': 'string', 'maxLength': 4096, 'pattern': '^[\\u0001-\\u007f]*$'}


def value_schema(field):
    if field == 'system_text':
        return deepcopy(TEXT_SCHEMA)
    if field == 'tool_descriptions':
        return {'type': 'object', 'additionalProperties': False,
                'properties': {k: deepcopy(TEXT_SCHEMA) for k in TOOLS}}
    if field == 'context_fields':
        return {'type': 'array', 'minItems': 4, 'maxItems': 7, 'uniqueItems': True,
                'items': {'type': 'string', 'enum': list(CONTEXT)}}
    if field == 'source_preload':
        return {'type': 'boolean'}
    if field in ('inspect_calls', 'act_calls'):
        return {'type': 'integer', 'minimum': 1, 'maximum': 15}
    values = ENUMS[field]
    return {'type': 'integer' if type(values[0]) is int else 'string', 'enum': list(values)}


def mutation_schema():
    return {'type': 'object', 'additionalProperties': False,
        'required': ['parent_id', 'mutations', 'target_failures'], 'properties': {
            'parent_id': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'},
            'mutations': {'type': 'array', 'minItems': 1, 'maxItems': 15, 'items': {'oneOf': [
                {'type': 'object', 'additionalProperties': False, 'required': ['field', 'value'],
                 'properties': {'field': {'type': 'string', 'enum': [f]}, 'value': value_schema(f)}}
                for f in FIELDS]}},
            'target_failures': {'type': 'array', 'minItems': 1, 'maxItems': 11, 'uniqueItems': True,
                                'items': {'type': 'string', 'enum': list(CATEGORIES)}},
            'rationale': {'type': 'string', 'description': 'At most 256 UTF-8 bytes.'}}}


def shared_rules():
    return {'version': 'MutationProposalV1', 'submission_bytes': 65536, 'rationale_bytes': 256,
        'authored_text_combined_bytes': 4096, 'authored_text': 'ASCII and NUL-free; historical payload restrictions',
        'duplicate_field': 'reject even when equal', 'replacement': 'whole field; unchanged fields inherit parent',
        'dependencies': ['read_allowance zero requires source_preload true',
                         'context_fields unique and include task/tools/budget/control'],
        'version_field': 'immutable 1', 'global_decisions': 15, 'compiler': 'scaffold-compiler-1',
        'controller_meanings': {'C0': 'autonomous selection subject to global limits',
          'C1': 'reject already visible redundant reads', 'C2': 'gate READ after successful-read budget',
          'C3': 'INSPECT then ACT after successful inspection'},
        'forbidden': ['aliases', 'coercion', 'silent repair', 'executables', 'task lookup', 'resource ceiling changes']}


def structure(value):
    required = {'parent_id', 'mutations', 'target_failures'}
    if not isinstance(value, dict) or not required <= set(value) or set(value) - required - {'rationale'}:
        raise ValueError('MUTATION_FIELDS')
    if not isinstance(value['parent_id'], str) or not re.fullmatch('[0-9a-f]{64}', value['parent_id']):
        raise ValueError('MUTATION_PARENT_FORMAT')
    if not isinstance(value['mutations'], list) or not 1 <= len(value['mutations']) <= 15:
        raise ValueError('MUTATION_OPERATIONS')
    seen = set()
    for op in value['mutations']:
        if not isinstance(op, dict) or set(op) != {'field', 'value'} or not isinstance(op['field'], str):
            raise ValueError('MUTATION_OPERATION_FIELDS')
        if op['field'] in seen:
            raise ValueError('MUTATION_DUPLICATE_FIELD')
        seen.add(op['field'])
    if not isinstance(value['target_failures'], list) or not 1 <= len(value['target_failures']) <= 11:
        raise ValueError('MUTATION_CATEGORIES_TYPE')
    if any(not isinstance(c, str) for c in value['target_failures']):
        raise ValueError('MUTATION_CATEGORIES_TYPE')
    if len(set(value['target_failures'])) != len(value['target_failures']):
        raise ValueError('MUTATION_CATEGORIES_DUPLICATE')
    if 'rationale' in value and (not isinstance(value['rationale'], str) or len(value['rationale'].encode()) > 256):
        raise ValueError('MUTATION_RATIONALE')
    return value


def vocabulary(value):
    for op in value['mutations']:
        f, v = op['field'], op['value']
        if f not in FIELDS:
            raise ValueError('MUTATION_FIELD')
        if f == 'source_preload':
            valid = type(v) is bool
        elif f in ('inspect_calls', 'act_calls'):
            valid = type(v) is int and 1 <= v <= 15
        elif f in ENUMS:
            valid = type(v) is type(ENUMS[f][0]) and v in ENUMS[f]
        elif f == 'context_fields':
            valid = (isinstance(v, list) and all(isinstance(x, str) for x in v)
                     and len(set(v)) == len(v) and not set(v) - set(CONTEXT) and MANDATORY <= set(v))
        elif f == 'system_text':
            valid = isinstance(v, str) and v.isascii() and '\x00' not in v
        else:
            valid = (isinstance(v, dict) and not set(v) - set(TOOLS)
                     and all(isinstance(x, str) and x.isascii() and '\x00' not in x for x in v.values()))
        if not valid:
            raise ValueError('MUTATION_VALUE_' + f.upper())
    if any(c not in CATEGORIES for c in value['target_failures']):
        raise ValueError('MUTATION_CATEGORY')
    return value


@dataclass(frozen=True)
class MutationProposalV1:
    payload: bytes

    def to_dict(self):
        return decode_json(self.payload.decode())


def parse_f1(raw):
    if not isinstance(raw, str) or len(raw.encode()) > 65536:
        raise ValueError('MUTATION_SIZE')
    value = vocabulary(structure(decode_json(raw)))
    return MutationProposalV1(canonical(value))


def expand(proposal, registry):
    value = proposal.to_dict() if isinstance(proposal, MutationProposalV1) else deepcopy(proposal)
    vocabulary(structure(value))
    parent = parent_spec(registry, value['parent_id'])
    for operation in value['mutations']:
        parent[operation['field']] = deepcopy(operation['value'])
    return parent


def compile_mutation(proposal, registry):
    expanded = expand(proposal, registry)
    return compile_scaffold(ScaffoldSpecV1.from_dict(expanded))
