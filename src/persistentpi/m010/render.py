"""Independent, bounded arm requests; no response history or repair hints."""
from copy import deepcopy

from ..contracts import canonical, digest
from ..m09.disclosure import validate_projection
from .config import DEFAULT, COMMON_SYSTEM, SUFFIX
from .f0 import SYSTEM, proposal_contract
from .f2 import tool_schema
from .mutation import mutation_schema, shared_rules


def render(scenario, arm):
    if arm not in ('F0', 'F1', 'F2'):
        raise ValueError('M010_ARM')
    body = deepcopy(scenario['payload'])
    validate_projection(body['observation'])
    body['contract'] = proposal_contract() if arm == 'F0' else {
        'rules': shared_rules(), **({'schema': mutation_schema()} if arm == 'F1' else {})}
    system = SYSTEM if arm == 'F0' else COMMON_SYSTEM + ' ' + SUFFIX[arm]
    payload = {'model': DEFAULT['planner']['api_identifier'], 'messages': [
        {'role': 'system', 'content': system}, {'role': 'user', 'content': canonical(body).decode()}],
        'stream': False, 'think': 'high', 'options': {'temperature': 0, 'num_predict': 4096}}
    if arm == 'F2':
        payload['tools'] = [tool_schema()]
    raw = canonical(payload)
    if len(raw) > 16384:
        raise ValueError('M010_REQUEST_BYTES')
    return payload


def request_identity(study_id, scenario_id, arm):
    return digest(['M0.10A/1', study_id, scenario_id, arm])


def probe_arguments():
    return {'parent_id': '0' * 64, 'mutations': [{'field': 'recent_observations', 'value': 1}],
            'target_failures': ['OTHER']}


def probe_request():
    value = {'model': 'gpt-oss:120b', 'messages': [
        {'role': 'system', 'content': 'Operational capability check. Submit exactly one native '
         'submit_scaffold_mutation call with the supplied literal arguments. Do not optimize, execute, '
         'or request another turn.'},
        {'role': 'user', 'content': canonical(probe_arguments()).decode()}],
        'stream': False, 'think': 'high', 'options': {'temperature': 0, 'num_predict': 4096},
        'tools': [tool_schema()]}
    if len(canonical(value)) > 16384:
        raise ValueError('M010_PROBE_BYTES')
    return value
