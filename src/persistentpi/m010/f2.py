"""Native tool submission; arguments are data, never executable functions."""
from ..contracts import canonical
from .mutation import mutation_schema, parse_f1

NAME = 'submit_scaffold_mutation'


def tool_schema():
    return {'type': 'function', 'function': {'name': NAME,
        'description': 'Submit one scaffold mutation proposal for deterministic validation.',
        'parameters': mutation_schema()}}


def arguments(response):
    message = response.get('message', {})
    calls = message.get('tool_calls')
    if not isinstance(calls, list) or len(calls) != 1:
        raise ValueError('F2_CALL_COUNT')
    call = calls[0]
    if not isinstance(call, dict) or not isinstance(call.get('function'), dict):
        raise ValueError('F2_CALL_STRUCTURE')
    function = call['function']
    if function.get('name') != NAME:
        raise ValueError('F2_TOOL_NAME')
    if not isinstance(function.get('arguments'), dict):
        raise ValueError('F2_ARGUMENT_OBJECT')
    return function['arguments']


def parse_f2(response):
    return parse_f1(canonical(arguments(response)).decode())
