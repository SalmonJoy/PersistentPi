"""Fixed-purpose public-only test evidence and equal-capacity context projection."""
import ast
import hashlib
import json
import re

from ..artifacts import bounded_text
from ..contracts import ActionResult, Observation, canonical, digest
from ..interfaces import registry
from ..prompts import build_prompt

MARKER = '[truncated]'


def cut(text, limit, marker=False):
    value, truncated = bounded_text(text.encode('utf-8'),limit)
    if truncated and marker:
        value = bounded_text(text.encode('utf-8'),limit-len(MARKER))[0]+MARKER
    return value, truncated


def sanitized(text):
    text = re.sub(r'[A-Za-z]:[\\/][^\s\"\x27]+|(?<!\w)/(?:[^\s/]+/)+[^\s]+','<host-path>',text)
    return '\n'.join(line for line in text.splitlines() if 'File "' not in line and 'Interpreter.' not in line)


def detailed(result):
    if result['outcome'] != 'fail':
        return result['outcome'].upper()
    failures = []
    for case in result['cases']:
        if case['outcome'] == 'fail':
            message, _ = cut(sanitized(case['message']),384)
            traceback, _ = cut(sanitized(case.get('traceback','')),192)
            failures.append({'test_id':case['id'],'type':case['type'],'message':message,'traceback':traceback})
        if len(failures) == 2:
            break
    value = canonical({'outcome':'FAIL','failures':failures}).decode()
    # The complete field, including the marker, never exceeds its fixed allowance.
    return cut(value,1800,marker=True)[0]


def projected_observation(observation, mode):
    if observation.action.tool != 'run_public_tests':
        return observation
    if mode not in ('detailed','outcome_only'):
        raise ValueError('No verification history is permitted in a fresh restart')
    result = observation.result.data['structured_public']
    text = detailed(result) if mode == 'detailed' else result['outcome'].upper()
    # Budget the transported JSON string too, so escaping cannot defeat the
    # identical reservation used to decide eviction in the two projections.
    if mode == 'detailed' and len(canonical(canonical(text).decode())) > 1800:
        while len(canonical(canonical(text+MARKER).decode())) > 1800:
            text = text[:-1]
        text += MARKER
    return Observation(observation.step,observation.action,
                       ActionResult('run_public_tests', result['outcome']=='pass', {'output':text}))


def prompt(task, observations, state, config, controller, mode):
    projected = tuple(projected_observation(o,mode) for o in observations)
    unpacked_context = {**config['context'],'max_bytes':1000000}
    messages, metadata = build_prompt(task,projected,state,unpacked_context,config['output_protocol'],'E0')
    public = json.loads(messages[1]['content'])
    public['budget'].pop('remaining_attempts',None)
    public['tools'] = {k:v for k,v in registry('E0').items() if k in controller.actions()}
    public['control'] = {'policy':'C3','version':'inspect-act-1','phase':controller.phase,
                         'successful_reads':controller.reads,'inspection_budget':2,
                         'available_actions':list(controller.actions())}
    messages[0]['content'] += ('\nThe control state and available_actions below override the general action listing. '
                               'finish means GIVE_UP. Choose only an available action.')
    # Account for a full detailed field in both arms, even when O contains only FAIL.
    def packed_size():
        shadow = json.loads(canonical(public))
        reserve = 0
        for observation in shadow['observations']:
            if observation['action']['tool'] == 'run_public_tests':
                observation['result']['data']['output'] = ''
                reserve += 1800
        messages[1]['content'] = canonical(public).decode()
        shadow_messages = [messages[0],{'role':'user','content':canonical(shadow).decode()}]
        return len(canonical(shadow_messages))+reserve
    while packed_size() > config['context']['max_bytes']:
        if not public['observations']:
            raise ValueError('Task context exceeds prompt bound')
        public['observations'].pop(0)
    metadata.update(prompt_version='m08-window-1',context_version='m08-equal-feedback-reserve-1',
                    prompt_hash=digest(messages),prompt_bytes=len(canonical(messages)),
                    observations_included=len(public['observations']),
                    observations_dropped=len(observations)-len(public['observations']),
                    reserved_prompt_bytes=packed_size())
    # Research/debug metadata is a receipt; never insert it into the payload.
    return messages, metadata


def candidate_signatures(source):
    try:
        normalized = ast.dump(ast.parse(source),include_attributes=False)
    except SyntaxError:
        normalized = None
    return {'byte_hash':hashlib.sha256(source.encode('utf-8')).hexdigest(),'ast_hash':digest(normalized) if normalized else None}
