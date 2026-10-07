"""Strict action representations. No repair, inference retries, or semantic guessing."""
import json

from .contracts import ActionRequest
from .tools import TOOLS

PROTOCOLS = ('runner-json-1', 'runner-json-schema-1', 'runner-dsl-1')
REPLACE = {'arguments': ('path', 'content'), 'permission': 'edit_declared_source'}
STAGES = ('model_response_received', 'parse_valid', 'schema_valid', 'action_authorized',
          'action_applicable', 'action_executed', 'checkpoint_created',
          'public_verification_reached', 'public_verification_passed', 'hidden_evaluation_passed')


def registry(edit):
    if edit not in ('E0', 'E1'):
        raise ValueError('Unsupported edit primitive')
    return TOOLS if edit == 'E0' else {k: v for k, v in TOOLS.items() if k != 'edit_file'} | {'replace_file': REPLACE}


def action_schema(edit):
    branches = []
    for name, spec in {**registry(edit), 'finish': {'arguments': ()}}.items():
        args = {key: {'type': 'string'} for key in spec['arguments']}
        if name == 'finish':
            args['reason'] = {'type': 'string'}
        branches.append({'type': 'object', 'additionalProperties': False, 'required': ['tool', 'arguments'],
            'properties': {'tool': {'type': 'string', 'enum': [name]},
                'arguments': {'type': 'object', 'properties': args, 'required': list(spec['arguments']),
                              'additionalProperties': False}}})
    return {'anyOf': branches}


def decode_json(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError('Duplicate JSON key')
            value[key] = item
        return value
    def constant(_):
        raise ValueError('Non-finite JSON number')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def decode_dsl(raw, edit):
    # Exactly one optional transport newline; content is never stripped or repaired.
    text = raw[:-1] if raw.endswith('\n') else raw
    if '\r' in text:
        raise ValueError('DSL requires LF line endings')
    if text == 'VERIFY':
        return {'tool': 'run_public_tests', 'arguments': {}}
    if text == 'FINISH' or (text.startswith('FINISH ') and '\n' not in text):
        return {'tool': 'finish', 'arguments': {} if text == 'FINISH' else {'reason': text[7:]}}
    if text.startswith('READ ') and '\n' not in text and text[5:]:
        return {'tool': 'read_file', 'arguments': {'path': text[5:]}}
    header, separator, body = text.partition('\n<<<<<<\n')
    if not separator or not body.endswith('\n>>>>>>'):
        raise ValueError('Malformed DSL action/delimiters')
    body = body[:-7]  # Remove the separator LF and six-character END marker.
    if '\n<<<<<<\n' in body or '\n>>>>>>\n' in body:
        raise ValueError('Reserved DSL delimiter in content')
    if edit == 'E0' and header.startswith('EDIT ') and header[5:]:
        parts = body.split('\n======\n')
        if len(parts) != 2:
            raise ValueError('EDIT requires exactly one middle delimiter')
        return {'tool': 'edit_file', 'arguments': {'path': header[5:], 'old': parts[0], 'new': parts[1]}}
    if edit == 'E1' and header.startswith('REPLACE ') and header[8:]:
        return {'tool': 'replace_file', 'arguments': {'path': header[8:], 'content': body}}
    raise ValueError('Unknown DSL action for edit primitive')


def parse_output(raw, protocol, edit):
    stages = {'parse_valid': False, 'schema_valid': False}
    try:
        value = decode_dsl(raw, edit) if protocol == 'runner-dsl-1' else decode_json(raw)
        stages['parse_valid'] = True
    except (ValueError, TypeError, RecursionError) as exc:
        return None, stages, 'parse_valid', str(exc)[:300]
    try:
        if not isinstance(value, dict) or not {'tool', 'arguments'} <= set(value):
            raise ValueError('Expected an ActionRequest object with tool and arguments')
        action = ActionRequest.from_dict(value)
        stages['schema_valid'] = True
        return action, stages, None, None
    except (ValueError, TypeError) as exc:
        return None, stages, 'schema_valid', str(exc)[:300]


def authorize_interface(action, edit):
    tools = {**registry(edit), 'finish': {'arguments': ()}}
    if action.tool not in tools:
        raise ValueError('Undeclared tool: ' + action.tool)
    required = set(tools[action.tool]['arguments'])
    permitted = required | ({'reason'} if action.tool == 'finish' else set())
    if not required <= set(action.arguments) or set(action.arguments) - permitted:
        raise ValueError('Invalid tool arguments')
    if any(not isinstance(v, str) for v in action.arguments.values()):
        raise ValueError('Tool arguments must be strings')
