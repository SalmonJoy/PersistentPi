"""Closed data contract and deterministic scaffold compiler; no code evaluation."""
from dataclasses import dataclass, field
import json
from pathlib import Path
import re

from ..contracts import DecisionState, TaskView, canonical, digest
from ..interfaces import PROTOCOLS, authorize_interface, decode_json, parse_output, registry
from ..prompts import build_prompt
from . import PROTOCOL

COMPILER = 'scaffold-compiler-1'
RENDERER = 'scaffold-renderer-1'
FIELDS = ('task', 'tools', 'budget', 'control', 'observations', 'source', 'public_cases')
MANDATORY = ('task', 'tools', 'budget', 'control')
TOOLS = ('read_file', 'edit_file', 'replace_file', 'finish')


def interface_catalog():
    from .. import interfaces
    items = {}
    for edit in ('E0', 'E1'):
        for protocol in PROTOCOLS:
            key = edit + ':' + protocol
            tools = {k: v for k, v in registry(edit).items() if k != 'run_public_tests'}
            items[key] = {'edit': edit, 'protocol': protocol, 'version': 'existing-interface-1',
                          'tools': tools, 'implementation_hash': digest(Path(interfaces.__file__).read_text())}
    return {'version': 'm09-catalog-1', 'items': items,
            'excluded': {'E2': 'Historical codec unchanged; isolated compiler integration not admitted'}}


def baseline_system(edit):
    view = TaskView('fixture', 'fixture', ('src/solution.py',), ('src/solution.py',), 'fixture', 'fixture')
    messages, _ = build_prompt(view, (), DecisionState(1, 15, 15, 16000, 120),
                               {'max_bytes': 100000, 'field_bytes': 1800, 'recent_observations': 4},
                               'runner-json-schema-1', edit)
    return messages[0]['content'] + ('\nThe control state and available_actions below override the general action listing. '
                                    'finish means GIVE_UP. Choose only an available action.')


@dataclass(frozen=True)
class ScaffoldSpecV1:
    system_text: str
    interface: str = 'E0:runner-json-schema-1'
    tool_descriptions: tuple = ()
    context_fields: tuple = ('budget', 'control', 'observations', 'task', 'tools')
    source_preload: bool = False
    controller: str = 'C3'
    read_allowance: int = 2
    recent_observations: int = 4
    rejection_feedback: str = 'generic'
    retry: str = 'stop'
    stagnation: int = 0
    inspect_calls: int = 15
    act_calls: int = 15
    inspect_output: int = 512
    act_output: int = 512
    version: int = 1

    @classmethod
    def from_dict(cls, value):
        if not isinstance(value, dict) or set(value) - set(cls.__dataclass_fields__):
            raise ValueError('SPEC_UNKNOWN_FIELD')
        data = dict(value)
        descriptions = data.get('tool_descriptions', {})
        if not isinstance(descriptions, dict) or set(descriptions) - set(TOOLS):
            raise ValueError('SPEC_TOOL_DESCRIPTION')
        data['tool_descriptions'] = tuple(sorted(descriptions.items()))
        if 'context_fields' in data:
            if not isinstance(data['context_fields'], (list, tuple)):
                raise ValueError('SPEC_CONTEXT')
            data['context_fields'] = tuple(data['context_fields'])
        try:
            result = cls(**data)
        except TypeError as exc:
            raise ValueError('SPEC_REQUIRED_FIELD') from exc
        result.validate()
        return result

    def to_dict(self):
        return {**self.__dict__, 'tool_descriptions': dict(self.tool_descriptions),
                'context_fields': list(self.context_fields)}

    def validate(self):
        if type(self.version) is not int or self.version != 1:
            raise ValueError('SPEC_VERSION')
        if (not isinstance(self.tool_descriptions, tuple)
                or any(not isinstance(p, tuple) or len(p) != 2 or p[0] not in TOOLS for p in self.tool_descriptions)
                or len({p[0] for p in self.tool_descriptions}) != len(self.tool_descriptions)):
            raise ValueError('SPEC_TOOL_DESCRIPTION')
        texts = [self.system_text, *dict(self.tool_descriptions).values()]
        if any(not isinstance(t, str) or not t.isascii() or '\x00' in t for t in texts):
            raise ValueError('SPEC_TEXT')
        if sum(len(t.encode()) for t in texts) > 4096:
            raise ValueError('SPEC_TEXT_SIZE')
        if any(re.search(r'\bp[0-9a-f]{16}\b|```|\bdef\s+solve\s*\(|\b(reference_solution|task_lookup)\b', t) for t in texts):
            raise ValueError('SPEC_BENCHMARK_PAYLOAD')
        if self.interface not in interface_catalog()['items']:
            raise ValueError('SPEC_INTERFACE')
        if self.controller not in ('C0', 'C1', 'C2', 'C3') or type(self.source_preload) is not bool:
            raise ValueError('SPEC_CONTROLLER')
        if (type(self.read_allowance) is not int or self.read_allowance not in (0, 1, 2)
                or (self.read_allowance == 0 and not self.source_preload)):
            raise ValueError('SPEC_READ_ALLOWANCE')
        if type(self.recent_observations) is not int or self.recent_observations not in range(5):
            raise ValueError('SPEC_RECENT')
        if self.rejection_feedback not in ('generic', 'precise') or self.retry not in ('stop', 'retry'):
            raise ValueError('SPEC_POLICY')
        if type(self.stagnation) is not int or self.stagnation not in (0, 2, 3):
            raise ValueError('SPEC_STAGNATION')
        if (not isinstance(self.context_fields, tuple) or any(not isinstance(v, str) for v in self.context_fields)
                or len(set(self.context_fields)) != len(self.context_fields)
                or set(self.context_fields) - set(FIELDS) or not set(MANDATORY) <= set(self.context_fields)):
            raise ValueError('SPEC_CONTEXT')
        for v in (self.inspect_calls, self.act_calls):
            if type(v) is not int or not 1 <= v <= 15:
                raise ValueError('SPEC_CALL_ALLOCATION')
        for v in (self.inspect_output, self.act_output):
            if type(v) is not int or v not in (128, 256, 512, 1024):
                raise ValueError('SPEC_OUTPUT_ALLOCATION')
        return self


def references():
    return {name: ScaffoldSpecV1(baseline_system(edit), interface=edit + ':runner-json-schema-1')
            for name, edit in (('B0', 'E0'), ('B1', 'E1'))}


@dataclass(frozen=True)
class RunnerConfiguration:
    scaffold_id: str
    spec: ScaffoldSpecV1
    catalog_hash: str
    compiler: str = COMPILER
    renderer: str = RENDERER
    protocol: str = PROTOCOL

    def complexity(self):
        default = references()['B0'].to_dict()
        current = self.spec.to_dict()
        return (len(self.spec.system_text.encode()) + sum(len(v.encode()) for _, v in self.spec.tool_descriptions),
                2 if self.spec.controller == 'C3' else 1,
                2 if self.spec.read_allowance == 0 else 3,
                sum(current[k] != default[k] for k in current if k not in ('system_text', 'tool_descriptions')))


def compile_scaffold(spec, catalog=None):
    spec = spec if isinstance(spec, ScaffoldSpecV1) else ScaffoldSpecV1.from_dict(spec)
    spec.validate()
    catalog = catalog or interface_catalog()
    if catalog != interface_catalog():
        raise ValueError('Frozen catalog differs from trusted compiler')
    value = {'spec': spec.to_dict(), 'compiler': COMPILER, 'renderer': RENDERER,
             'catalog_hash': digest(catalog), 'protocol': PROTOCOL}
    return RunnerConfiguration(digest(value), spec, digest(catalog))


@dataclass(frozen=True)
class ProposalEnvelope:
    parents: tuple
    scaffold: ScaffoldSpecV1
    mutation: str
    rationale: str
    targeted_categories: tuple
    predicted_metrics: dict = field(default_factory=dict)

    def to_dict(self):
        return {'parents': list(self.parents), 'scaffold': self.scaffold.to_dict(), 'mutation': self.mutation,
                'rationale': self.rationale, 'targeted_categories': list(self.targeted_categories),
                'predicted_metrics': self.predicted_metrics}


def parse_proposal(raw, allowed_parents):
    if not isinstance(raw, str) or len(raw.encode()) > 65536:
        raise ValueError('PROPOSAL_SIZE')
    value = decode_json(raw)
    required = {'parents', 'scaffold', 'mutation', 'rationale', 'targeted_categories'}
    if not isinstance(value, dict) or not required <= set(value) or set(value) - required - {'predicted_metrics'}:
        raise ValueError('PROPOSAL_FIELDS')
    parents = value['parents']
    if (not isinstance(parents, list) or not 1 <= len(parents) <= 2 or len(set(parents)) != len(parents)
            or any(p not in allowed_parents for p in parents)):
        raise ValueError('PROPOSAL_PARENT')
    for name in ('mutation', 'rationale'):
        if not isinstance(value[name], str) or len(value[name].encode()) > 1024:
            raise ValueError('PROPOSAL_TEXT')
    from .disclosure import CATEGORIES
    categories = value['targeted_categories']
    if not isinstance(categories, list) or any(c not in CATEGORIES for c in categories):
        raise ValueError('PROPOSAL_CATEGORY')
    prediction = value.get('predicted_metrics', {})
    if not isinstance(prediction, dict) or set(prediction) - {'public_passes', 'formations', 'runner_tokens', 'runner_calls'}:
        raise ValueError('PROPOSAL_PREDICTION')
    if any(type(v) not in (int, float) for v in prediction.values()):
        raise ValueError('PROPOSAL_PREDICTION')
    return ProposalEnvelope(tuple(sorted(parents)), ScaffoldSpecV1.from_dict(value['scaffold']),
                            value['mutation'], value['rationale'], tuple(sorted(set(categories))), prediction)
