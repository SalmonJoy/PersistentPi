"""Transport-independent Planner contract. No default network transport."""
from dataclasses import dataclass
import time
import math

from ..contracts import canonical


@dataclass(frozen=True)
class PlannerReply:
    response: dict
    identity: dict
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int = 0
    reasoning_in_output: bool = True
    latency: float = 0
    seed_supported: bool = True

    @property
    def text(self):
        return self.response['message']['content']

    @property
    def total_tokens(self):
        return self.input_tokens + self.output_tokens + (0 if self.reasoning_in_output else self.reasoning_tokens)

    def validate(self):
        for v in (self.input_tokens, self.output_tokens, self.reasoning_tokens):
            if type(v) is not int or v < 0:
                raise ValueError('Planner usage unavailable')
        if self.output_tokens + (0 if self.reasoning_in_output else self.reasoning_tokens) > 4096:
            raise ValueError('Planner output bound violation')
        if len(canonical(self.response)) > 65536 or not isinstance(self.text, str):
            raise ValueError('Planner response bound violation')
        if type(self.latency) not in (int, float) or not math.isfinite(self.latency) or not 0 <= self.latency <= 180:
            raise ValueError('Planner latency unavailable')
        if type(self.seed_supported) is not bool or type(self.reasoning_in_output) is not bool:
            raise ValueError('Planner capability accounting invalid')
        return self


class FakePlanner:
    offline = True

    def __init__(self, sequence, seed_supported=True):
        self.sequence, self.seed_supported = iter(sequence), seed_supported
        self.requests = []

    def propose(self, observation_bundle, archive_view, remaining_budget):
        payload = observation_bundle['request']
        self.requests.append(payload)
        value = next(self.sequence)
        if callable(value):
            value = value(observation_bundle, archive_view, remaining_budget)
        if isinstance(value, BaseException):
            raise value
        text = value if isinstance(value, str) else canonical(value).decode()
        return PlannerReply({'model': 'fake-planner', 'message': {'content': text}, 'done': True},
                            {'model': 'fake-planner', 'backend': 'offline-fixture', 'seed_supported': self.seed_supported},
                            100, min(4096, len(text)), seed_supported=self.seed_supported)

    def prepare_request(self, payload):
        return payload


class CloudPlanner:
    offline = False

    def __init__(self, frozen_identity, configuration, transport=None):
        self.identity, self.configuration, self.transport = frozen_identity, configuration, transport

    def validate_identity(self, current):
        if current != self.identity:
            raise RuntimeError('Planner identity drift')

    def prepare_request(self, request):
        payload = dict(request)
        supported = self.configuration.get('seed_supported', False)
        payload['options'] = {**payload['options']}
        if not supported:
            payload['options'].pop('seed', None)
        payload.pop('think', None)
        if self.configuration.get('reasoning_parameter'):
            payload[self.configuration['reasoning_parameter']] = self.configuration['reasoning_value']
        if len(canonical(payload)) > 16384:
            raise ValueError('Mapped Planner request exceeds byte cap')
        return payload

    def propose(self, observation_bundle, archive_view, remaining_budget):
        if self.transport is None:
            raise RuntimeError('Cloud inference not enabled in M0.9B')
        payload = self.prepare_request(observation_bundle['request'])
        result = self.transport(payload, timeout=180)
        self.validate_identity(result.identity)
        return result.validate()


def admission(identity, frozen_identity, included_allowance, required_allowance, configuration):
    if identity != frozen_identity:
        raise RuntimeError('Pre-start Planner identity drift')
    if (type(included_allowance) not in (int, float) or not math.isfinite(included_allowance)
            or type(required_allowance) not in (int, float) or not math.isfinite(required_allowance)
            or required_allowance <= 0 or included_allowance < required_allowance
            or configuration.get('purchased_credit_ceiling') != 0):
        raise RuntimeError('Free-only Planner feasibility not established')
    return {'admitted': True, 'identity': identity, 'seed_supported': configuration.get('seed_supported', False),
            'configuration': configuration, 'included_allowance': included_allowance,
            'required_allowance': required_allowance, 'purchased_credits': 0}
