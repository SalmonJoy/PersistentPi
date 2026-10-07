"""Recording HTTP-boundary fixtures. These are not Runners or model adapters."""
from copy import deepcopy
import json
import threading
import time

from ..contracts import canonical, digest

PRICING = {'model': 'gpt-oss:120b', 'authoritative': True, 'source': 'synthetic-test-fixture-not-account-evidence',
           'input_per_million': '0.15', 'cached_input_per_million': '0.014', 'output_per_million': '0.60'}


def submission(scenario, arm, valid=True):
    if not valid:
        return {'content': ''}
    parent = scenario['parent_id']
    if arm == 'F0':
        value = {'parents': [parent], 'scaffold': deepcopy(scenario['payload']['parent']['spec']),
                 'mutation': 'fixture', 'rationale': 'fixture', 'targeted_categories': ['OTHER']}
    else:
        value = {'parent_id': parent, 'mutations': [{'field': 'recent_observations', 'value': 4}],
                 'target_failures': ['OTHER']}
    if arm == 'F2':
        return {'content': '', 'tool_calls': [{'function': {'name': 'submit_scaffold_mutation', 'arguments': value}}]}
    return {'content': canonical(value).decode()}


def fixture_response(scenario, arm, valid=True):
    return {'model': 'gpt-oss:120b', 'done': True, 'done_reason': 'stop', 'message': submission(scenario, arm, valid),
            'prompt_eval_count': 1000, 'prompt_eval_cached_count': 100, 'eval_count': 100}


class RecordingTransport:
    kind = 'recording-stub'

    def __init__(self, scenarios, handler=None, concurrency=3, order=('F0', 'F1', 'F2')):
        self.scenarios = {s['id']: s for s in scenarios}
        self.handler = handler or (lambda s, a: fixture_response(s, a))
        self.concurrency = concurrency
        self.order = tuple(order)
        self.events = []
        self.lock = threading.Lock()
        self.active = 0
        self.peak = 0
        self.finished = set()

    def send(self, payload, identity):
        sid, arm = identity['scenario'], identity['arm']
        with self.lock:
            self.active += 1
            self.peak = max(self.peak, self.active)
            self.events.append({'event': 'send', 'scenario': sid, 'arm': arm, 'identity': identity['request_id'],
                                'request_hash': digest(payload), 'at': time.monotonic()})
        try:
            # Frozen arm delay creates known out-of-order receipts without feeding a sibling result.
            time.sleep(.002 * (self.order.index(arm) + 1))
            response = self.handler(self.scenarios[sid], arm)
            with self.lock:
                self.events.append({'event': 'receipt', 'scenario': sid, 'arm': arm, 'at': time.monotonic()})
            return response
        finally:
            with self.lock:
                self.active -= 1


def campaign_handler(label):
    if label not in 'ABCDEFGHI':
        raise ValueError('M010_CAMPAIGN_FIXTURE')
    def handle(s, arm):
        j = s['instance']
        valid = {
            'A': arm != 'F0', 'B': True, 'C': arm == 'F1' and j != 2,
            'D': False, 'E': arm == 'F2', 'F': True, 'G': arm == 'F1',
            'H': False, 'I': True}[label]
        response = fixture_response(s, arm, valid)
        if label == 'F' and s['family'] == 'context_mismatch' and j == 0 and arm == 'F1':
            raise TimeoutError('synthetic unresolved send')
        if label == 'G' and s['family'] == 'no_op_repetition' and j < 2 and arm == 'F1':
            value = json.loads(response['message']['content'])
            value['command'] = '<non-executable prohibited-field fixture>'
            response['message']['content'] = canonical(value).decode()
        if label == 'H':
            response['message'] = submission(s, arm, True)
            response['done_reason'] = 'length'
            response['eval_count'] = 4096
        return response
    return handle
