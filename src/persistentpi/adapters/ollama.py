"""Local Ollama HTTP transport, identity discovery and strict action parsing."""
from dataclasses import dataclass
import datetime as dt
import http.client
import ipaddress
import json
import socket
import time
from urllib.parse import urlsplit

from ..contracts import ActionRequest, canonical, digest
from ..prompts import build_prompt


def endpoint_parts(endpoint):
    parsed = urlsplit(endpoint)
    if parsed.scheme != 'http' or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/'):
        raise ValueError('M0.2 endpoint must be a plain local HTTP origin')
    host = '127.0.0.1' if parsed.hostname == 'localhost' else parsed.hostname
    if not host or not ipaddress.ip_address(host).is_loopback:
        raise ValueError('M0.2 only permits loopback inference endpoints')
    return host, parsed.port or 11434


class HTTPClient:
    def __init__(self, endpoint):
        self.host, self.port = endpoint_parts(endpoint)

    def request(self, method, path, payload=None, timeout=10):
        deadline = time.monotonic() + timeout
        connection = http.client.HTTPConnection(self.host, self.port, timeout=timeout)
        try:
            connection.request(method, path, body=canonical(payload) if payload is not None else None,
                               headers={'Content-Type': 'application/json'})
            response = connection.getresponse()
            chunks = bytearray()
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('HTTP deadline exceeded')
                if connection.sock:
                    connection.sock.settimeout(remaining)
                block = response.read1(4096)
                if not block:
                    break
                chunks.extend(block)
                if len(chunks) > 262144:
                    raise ValueError('Backend response exceeds byte bound')
            if response.status != 200:
                raise RuntimeError('Backend HTTP status ' + str(response.status))
            result = json.loads(chunks)
            if not isinstance(result, dict) or result.get('error'):
                raise ValueError('Backend returned an error or invalid response object')
            return result
        finally:
            connection.close()


def discover(config, client=None):
    client = client or HTTPClient(config['endpoint'])
    version = client.request('GET', '/api/version', timeout=5).get('version')
    tags = client.request('GET', '/api/tags', timeout=5).get('models', [])
    found = next((m for m in tags if m.get('name') == config['model']), None)
    if not found:
        raise ValueError('Requested model is not installed locally: ' + config['model'])
    if config.get('expected_digest') is not None and found.get('digest') != config['expected_digest']:
        raise ValueError('Model digest differs from frozen M0.4 inventory')
    if config.get('expected_runtime_version') is not None and version != config['expected_runtime_version']:
        raise ValueError('Runtime differs from frozen M0.4 inventory')
    show = client.request('POST', '/api/show', {'model': config['model']}, timeout=5)
    if show.get('remote_host') or found.get('remote_host') or 'cloud' in config['model']:
        raise ValueError('Only installed local weights are permitted')
    if 'completion' not in show.get('capabilities', []):
        raise ValueError('Installed model does not expose completion capability')
    details = show.get('details', found.get('details', {}))
    info = show.get('model_info', {})
    architecture = info.get('general.architecture')
    identity = {'provider': 'ollama', 'backend_type': 'local_http', 'endpoint': config['endpoint'],
            'model': config['model'], 'digest': found.get('digest'), 'runtime_version': version,
            'quantization': details.get('quantization_level'), 'parameter_count': info.get('general.parameter_count'),
            'parameter_size': details.get('parameter_size'), 'format': details.get('format'),
            'architecture': architecture, 'declared_context_length': info.get(str(architecture) + '.context_length'),
            'template_hash': digest(show['template']) if show.get('template') is not None else None,
            'system_hash': digest(show['system']) if show.get('system') is not None else None,
            'seed_support': 'documented_backend_option_not_determinism_guarantee',
            'seed_value': config['seed'], 'settings': {k: config[k] for k in
                ('temperature', 'num_ctx', 'num_predict', 'timeout_seconds', 'keep_alive')},
            'backend_defaults': show.get('parameters'), 'capabilities': show.get('capabilities')}
    if config.get('thinking_policy') == 'explicit-false-1':
        identity.update(stored_bytes=found.get('size'), thinking_metadata=show.get('thinking'),
                        thinking_policy='explicit-false-1', think=False)
    return identity


def strict_action(content):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError('Non-finite JSON number')

    value = json.loads(content, object_pairs_hook=pairs, parse_constant=nonfinite)
    if not isinstance(value, dict) or not {'tool', 'arguments'} <= set(value):
        raise ValueError('Expected an ActionRequest object with tool and arguments')
    return ActionRequest.from_dict(value)


@dataclass(frozen=True)
class ModelReply:
    action: ActionRequest | None
    input_tokens: int | None
    output_tokens: int | None
    telemetry: dict
    raw_output: str = ''
    error: str | None = None
    status: str = 'success'
    usage_kind: str = 'measured'


class OllamaModel:
    request_receipts = True
    usage_kind = 'measured'

    def __init__(self, config, identity, client=None):
        self.config, self.identity = config, identity
        self.client = client or HTTPClient(config['endpoint'])

    def prompt(self, task, observations, state):
        return build_prompt(task, observations, state, self.config['context'],
            self.config.get('output_protocol', 'runner-json-1'), self.config.get('edit_primitive', 'E0'))

    def response_format(self, protocol, edit):
        if protocol == 'runner-json-schema-1':
            from ..interfaces import action_schema
            return action_schema(edit)
        return None if protocol == 'runner-dsl-1' else 'json'

    def parse_response(self, content, protocol, edit):
        from ..interfaces import parse_output
        return parse_output(content, protocol, edit)

    def generate(self, task, observations, state, record_request=None):
        started = dt.datetime.now(dt.timezone.utc).isoformat()
        began = time.monotonic()
        telemetry = {'telemetry_version': 1, 'started_utc': started, 'identity': self.identity,
                     'usage_kind': 'measured', 'repair_calls': 0, 'request_sent': False}
        response = {}
        try:
            protocol = self.config.get('output_protocol', 'runner-json-1')
            edit = self.config.get('edit_primitive', 'E0')
            messages, context = self.prompt(task, observations, state)
            options = {'temperature': self.config['temperature'], 'seed': self.config['seed'],
                       'num_ctx': self.config['num_ctx'],
                       'num_predict': min(self.config['num_predict'], max(1, state.remaining_tokens))}
            payload = {'model': self.config['model'], 'messages': messages, 'stream': False,
                       'format': 'json', 'options': options, 'keep_alive': self.config['keep_alive']}
            if self.config.get('thinking_policy') == 'explicit-false-1':
                if self.config.get('think') is not False:
                    raise ValueError('M0.4 primary condition requires explicit think=false')
                payload['think'] = False
                telemetry['thinking_policy'] = 'explicit-false-1'
            response_format = self.response_format(protocol, edit)
            if response_format is None:
                del payload['format']
            else:
                payload['format'] = response_format
            if 'output_protocol' in self.config:
                telemetry.update(output_protocol=protocol, edit_primitive=edit,
                    backend_constrained=protocol == 'runner-json-schema-1',
                    backend_format=payload.get('format'), normalization='none except optional single DSL final LF')
            telemetry['context'] = context
            timeout = min(self.config['timeout_seconds'], state.remaining_wall_seconds)
            if timeout <= 0:
                raise TimeoutError('No remaining request wall budget')
            if record_request:
                record_request({'request_version': 1, 'endpoint_type': 'ollama_local_http',
                                'payload': payload, 'context': context, 'timeout_seconds': timeout})
            # Detect tag/runtime changes before every generation; never silently use a new model.
            def remaining_timeout(cap):
                remaining = timeout - (time.monotonic() - began)
                if remaining <= 0:
                    raise TimeoutError('Identity preflight exhausted request deadline')
                return min(cap, remaining)

            current_version = self.client.request('GET', '/api/version', timeout=remaining_timeout(5)).get('version')
            current_tags = self.client.request('GET', '/api/tags', timeout=remaining_timeout(5)).get('models', [])
            current = next((m for m in current_tags if m.get('name') == self.config['model']), {})
            telemetry.update(observed_digest=current.get('digest'), observed_runtime_version=current_version)
            if current.get('digest') != self.identity['digest'] or current_version != self.identity['runtime_version']:
                raise ValueError('Model digest or runtime version changed since run reservation')
            remaining = timeout - (time.monotonic() - began)
            if remaining <= 0:
                raise TimeoutError('Identity preflight exhausted request deadline')
            telemetry['request_sent'] = True
            response = self.client.request('POST', '/api/chat', payload, timeout=remaining)
            if self.config.get('thinking_policy') == 'explicit-false-1':
                thinking = response.get('message', {}).get('thinking', '')
                telemetry['thinking_response_bytes'] = len(thinking.encode('utf-8')) if isinstance(thinking, str) else None
                if thinking:
                    raise ValueError('Unexpected thinking output in non-thinking primary condition')
            if response.get('done') is not True or response.get('model') != self.config['model']:
                raise ValueError('Incomplete response or unexpected model identity')
            content = response.get('message', {}).get('content')
            if not isinstance(content, str) or len(content.encode('utf-8')) > 16384:
                raise ValueError('Missing or oversized model content')
            action, error = None, None
            if 'output_protocol' in self.config:
                action, stages, exit_stage, error = self.parse_response(content, protocol, edit)
                telemetry.update(interface_parse=stages, interface_exit_stage=exit_stage)
            else:
                try:
                    action = strict_action(content)
                except (ValueError, TypeError, RecursionError) as exc:
                    error = str(exc)[:300]
            status = 'success' if action is not None else 'malformed_model_output'
        except (TimeoutError, socket.timeout) as exc:
            action, content, error, status = None, '', type(exc).__name__, 'timeout'
        except (OSError, ValueError, TypeError, RuntimeError, http.client.HTTPException) as exc:
            action, content, error, status = None, '', str(exc)[:300], 'infrastructure_failure'
        counts = {}
        for key in ('prompt_eval_count', 'eval_count', 'prompt_eval_cached_count', 'total_duration',
                    'load_duration', 'prompt_eval_duration', 'eval_duration'):
            value = response.get(key)
            counts[key] = value if type(value) is int and value >= 0 else None
        prompt, output = counts['prompt_eval_count'], counts['eval_count']
        telemetry.update(counts)
        telemetry['additional_backend_metrics'] = {key: value for key, value in response.items()
            if key not in counts and key.endswith(('_count', '_duration'))
            and type(value) is int and value >= 0}
        telemetry.update(ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                         wall_seconds=time.monotonic() - began, status=status,
                         done_reason=response.get('done_reason'),
                         total_tokens=prompt + output if prompt is not None and output is not None else None,
                         tokens_per_second=(output * 1e9 / counts['eval_duration'])
                         if output is not None and counts['eval_duration'] else None)
        return ModelReply(action, prompt, output, telemetry, content, error, status)
