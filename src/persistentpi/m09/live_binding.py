"""Admission-bound native research transport; no cohort or evaluator capability."""
from dataclasses import dataclass
import json
import math
from pathlib import Path
import subprocess
import time

from ..contracts import canonical, digest
from .admission import ALIAS, ADAPTER, ENDPOINT, assert_identity, resolve_identity, usage, proposal_reply, safe_bytes
from .disclosure import validate_projection, VERSION, SYSTEM, project
from .manager import proposal_contract
from .pro_admission import ObservedCloudTransport, calculated_charge
from .storage import LIMITS
from .live_evidence import authentication_evidence

PARENT = '0ceb6ea3c2c297943423a2282c4872ef557c12f0'
LIVE_ADAPTER = 'm09c-live-native-1'
RENDERER = 'm09c-admitted-request-1'
_SEAL = object()


@dataclass(frozen=True)
class AdmissionBinding:
    configuration_json: str
    identity_json: str
    linkage_json: str
    seal: object

    def __post_init__(self):
        if self.seal is not _SEAL:
            raise ValueError('Binding must originate from anchored admission')

    @classmethod
    def load(cls, root):
        root = Path(root)
        base = 'docs/research-records/m09cr2/'
        names = {'preregistration': 'configs/m09-preregistered.json',
                 'pricing': base+'pricing-observation.json',
                 'rotation': base+'rotation-attestation.json',
                 'admission': base+'admission-result.json',
                 'freeze': base+'artifacts/frozen/freeze.json',
                 'config': base+'artifacts/frozen/resolved-configuration.json',
                 'amendment': base+'artifacts/frozen/amendment.json'}
        values, hashes = {}, {}
        for key, name in names.items():
            # Anchor bytes to the admitted commit, not caller-supplied JSON assertions.
            original = subprocess.run(['git', '-C', str(root), 'show', PARENT+':'+name],
                                      check=True, capture_output=True).stdout
            current = (root/name).read_bytes()
            if current != original:
                raise ValueError('Admission artifact drift')
            values[key], hashes[key] = json.loads(current), digest(json.loads(current))
        admission, freeze, config = values['admission'], values['freeze'], values['config']
        identity = admission['identity']
        if (admission['decision']['state'] != 'ADMITTED'
                or admission['amendment_hash'] != freeze['amendment_hash']
                or hashes['amendment'] != freeze['amendment_hash']
                or hashes['config'] != freeze['resolved_configuration_hash']
                or config['protocol_version'] != '0.6'
                or config['planner']['model'] != identity['requested_alias']
                or identity['requested_alias'] != ALIAS
                or identity['adapter_version'] != ADAPTER or identity['endpoint'] != ENDPOINT
                or config['planner']['max_requests'] != 8 or config['planner']['max_tokens'] != 200000
                or config['accounting_scope']['planner'] != (
                    'provider_accounted_tokens = prompt_eval_count + eval_count; cached count separate; thinking content provenance only')):
            raise ValueError('Admission linkage/contract mismatch')
        linkage = {'parent_commit': PARENT, 'artifact_hashes': hashes,
                   'parent_preregistration_hash': hashes['preregistration'],
                   'amendment_hash': freeze['amendment_hash'],
                   'resolved_configuration_hash': freeze['resolved_configuration_hash'],
                   'wire_adapter': ADAPTER, 'live_adapter': LIVE_ADAPTER,
                   'endpoint': identity['endpoint'], 'usage': config['accounting_scope']['planner']}
        return cls(canonical(config).decode(), canonical(identity).decode(), canonical(linkage).decode(), _SEAL)

    @property
    def identity(self):
        return json.loads(self.identity_json)

    @property
    def parent(self):
        return json.loads(self.configuration_json)

    @property
    def hash(self):
        return digest([self.configuration_json, self.identity_json, self.linkage_json])

    def configuration(self, validation=False):
        return {**self.parent, 'operational_launch': {
            'target': 'SEARCH_ONLY', 'binding_hash': self.hash,
            'validation_only': validation, 'adapter': LIVE_ADAPTER, 'renderer': RENDERER}}

    def check(self, configuration):
        launch = configuration.get('operational_launch', {})
        if (type(launch.get('validation_only')) is not bool
                or configuration != self.configuration(launch.get('validation_only'))):
            raise ValueError('Campaign/admission configuration mismatch')


def render_request(binding, configuration, observation, parent, archive, remaining, contract):
    binding.check(configuration)
    if set(observation) != {'policy', 'aggregate', 'families', 'failure_counts', 'excerpts', 'archive_decisions'}:
        raise ValueError('Disclosure contract mismatch')
    validate_projection(observation)
    if contract != proposal_contract():
        raise ValueError('Unapproved proposal contract')
    if (set(remaining) - set(LIMITS) or any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in remaining.values())):
        raise ValueError('Invalid remaining budget')
    # Reuse the historical positive-allowlist validator without its model constant.
    for item in archive:
        if set(item) != {'id', 'metrics', 'tasks'} or item['tasks'] != 32:
            raise ValueError('Archive disclosure mismatch')
        validate_projection({**project(), 'aggregate': item['metrics']})
        if not isinstance(item['id'], str) or len(item['id']) != 64 or any(c not in '0123456789abcdef' for c in item['id']):
            raise ValueError('Archive identity mismatch')
    identity = binding.identity
    options = {'temperature': identity['parameter_mapping']['temperature']['value'], 'num_predict': 4096}
    if identity['parameter_mapping']['seed']['supported']:
        options['seed'] = identity['parameter_mapping']['seed']['value']
    value = {'parent': {'id': parent.scaffold_id, 'spec': parent.spec.to_dict()},
             'observation': observation, 'archive': archive, 'remaining': remaining, 'contract': contract}
    while True:
        payload = {'model': identity['api_identifier'], 'messages': [
            {'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': canonical(value).decode()}],
            'stream': False, 'options': options,
            identity['parameter_mapping']['thinking']['field']: identity['parameter_mapping']['thinking']['value']}
        if len(canonical(payload)) <= 16384:
            return payload
        if value['observation']['excerpts']:
            value['observation'] = {**value['observation'], 'excerpts': value['observation']['excerpts'][:-1]}
        elif value['archive']:
            value['archive'] = value['archive'][:-1]
        else:
            raise ValueError('Mandatory Planner request exceeds byte cap')


class ResearchTransport(ObservedCloudTransport):
    offline = False

    def __init__(self, environment, binding):
        super().__init__(environment)
        self.binding = binding
        root = Path(__file__).resolve().parents[3]
        self.pricing = json.loads((root/'docs/research-records/m09cr2/pricing-observation.json').read_bytes())

    def current_identity(self):
        catalog, metadata = self.metadata()
        response = self._request('POST', '/api/me')
        self.authentication = authentication_evidence(response, self.last_http_status)
        seed = self.binding.identity['parameter_mapping']['seed']
        self.current_identity_value = resolve_identity(catalog, metadata, True if seed['supported'] else None)
        return self.current_identity_value

    def proposal(self, payload, timeout):
        if timeout != 180 or payload['model'] != self.binding.identity['api_identifier']:
            raise ValueError('Unapproved research route')
        for name in ('last_http_status','last_response_bytes','last_response_sha256'):
            setattr(self, name, None)
        return self._request('POST', '/api/chat', payload, timeout=timeout)

    def validate_payload(self, payload):
        safe_bytes(payload, (self._secret,))


class AdmittedPlanner:
    offline = False

    def __init__(self, binding, configuration, transport):
        if type(binding) is not AdmissionBinding:
            raise ValueError('Anchored binding required')
        binding.check(configuration)
        if not configuration['operational_launch']['validation_only'] and type(transport) is not ResearchTransport:
            raise ValueError('Only the admitted native transport is enabled live')
        if configuration['operational_launch']['validation_only'] and not getattr(transport, 'offline', False):
            raise ValueError('Validation requires a non-network transport')
        self.binding, self.configuration, self.transport = binding, configuration, transport
        self.last_usage = None

    def pre_request(self):
        self.binding.check(self.configuration)
        assert_identity(self.binding.identity, self.transport.current_identity())

    def prepare_request(self, payload):
        self.binding.check(self.configuration)
        identity = self.binding.identity
        expected = {'temperature': 0, 'num_predict': 4096}
        if identity['parameter_mapping']['seed']['supported']:
            expected['seed'] = 42
        if (payload['model'] != identity['api_identifier'] or payload['options'] != expected
                or payload.get('think') != 'high' or payload.get('stream') is not False
                or set(payload) != {'model', 'messages', 'stream', 'options', 'think'}
                or len(canonical(payload)) > 16384):
            raise ValueError('Outbound admitted request mismatch')
        validate_projection(json.loads(payload['messages'][1]['content'])['observation'])
        body = json.loads(payload['messages'][1]['content'])
        from .spec import compile_scaffold
        parent = compile_scaffold(body['parent']['spec'])
        if parent.scaffold_id != body['parent']['id'] or payload != render_request(
                self.binding, self.configuration, body['observation'], parent,
                body['archive'], body['remaining'], body['contract']):
            raise ValueError('Frozen request renderer mismatch')
        if hasattr(self.transport, 'validate_payload'):
            self.transport.validate_payload(payload)
        return payload

    def propose(self, bundle, archive, remaining):
        self.last_response, self.last_usage = None, None
        self.last_provenance = None
        payload = self.prepare_request(bundle['request'])
        began = time.monotonic()
        response = self.transport.proposal(payload, timeout=180)
        latency = time.monotonic() - began
        self.last_response = response
        self.last_usage = usage(response)
        self.last_provenance = {
            'endpoint': self.binding.identity['endpoint'], 'binding_hash': self.binding.hash,
            'wire_response_sha256': getattr(self.transport,'last_response_sha256',None),
            'wire_response_bytes': getattr(self.transport,'last_response_bytes',None),
            'http_status': getattr(self.transport,'last_http_status',None),
            'latency_seconds': latency,
            'credit_calculation': calculated_charge(response,self.transport.pricing)
                if hasattr(self.transport,'pricing') else {'synthetic_only':True}}
        if (response.get('model') != self.binding.identity['api_identifier']
                or response.get('done') is not True or response.get('done_reason') not in ('stop','length')
                or response.get('error') or not isinstance(response.get('message', {}).get('content'), str)
                or not isinstance(response.get('message', {}).get('thinking'), str)):
            raise ValueError('Planner response identity/completion mismatch')
        return proposal_reply(response, self.binding.identity, latency,
                              self.binding.identity['parameter_mapping']['seed']['supported'])
