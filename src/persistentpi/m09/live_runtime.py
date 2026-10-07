"""Pinned laptop transport plus the unchanged single-candidate execution kernel."""
import json
import os
import time
import uuid

from ..artifacts import atomic_write
from ..contracts import ActionRequest, ActionResult, Budget, DecisionState, Observation, canonical, digest
from ..interfaces import authorize_interface, parse_output
from ..m08.primitive_runtime import project as historical_projection
from ..adapters.ollama import HTTPClient, discover
from .runtime import CandidateExecutor, new_supervisor
from .analysis import Result
from .render import controller_for, wire_request

class LocalRunnerBackend:
    offline = False

    def __init__(self, binding, base_config, expected_identity):
        self.binding, self.config, self.expected = binding, base_config, expected_identity
        self.client = HTTPClient(base_config['endpoint'])
        self.deadline = None

    def respond(self, payload):
        owner = self
        class BoundedClient:
            def request(self, method, path, payload=None, timeout=10):
                remaining = owner.deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('Runner request deadline')
                return owner.client.request(method, path, payload, min(timeout, remaining))
        client = BoundedClient()
        if discover(self.config, client) != self.expected:
            raise RuntimeError('Frozen Runner identity drift')
        response = client.request('POST', '/api/chat', payload, timeout=30)
        if (response.get('done') is not True or response.get('model') != self.config['model']
                or response.get('message', {}).get('thinking')):
            raise RuntimeError('Runner identity/completion/thinking mismatch')
        return response


class LiveCandidateExecutor(CandidateExecutor):
    offline = False

    def __init__(self, backend_factory, tokenizer, base_config, window, clock=time.monotonic, binding=None):
        super().__init__(backend_factory, tokenizer, base_config, window, clock)
        self.binding = binding

    def evaluate(self, configuration, task, cohort_hash, job_id, store):
        supervisor = new_supervisor(store, configuration, task, job_id, self.window, self.clock)
        backend = self.backend_factory(configuration, task)
        if not getattr(backend, 'offline', False):
            if type(backend) is not LocalRunnerBackend or self.binding is None or backend.binding.hash != self.binding.hash:
                raise RuntimeError('Unadmitted Runner backend')
            self.binding.check(store.config)
            supervisor.usage['token_usage_kind'] = 'measured'
        s = configuration.spec
        controller = controller_for(configuration, task.view.editable_paths)
        observations, phase_calls, repetition = [], {'INSPECT': 0, 'ACT': 0}, {}
        formed, outcome, reason, inference = False, None, 'decision_budget_exhausted', 0.
        edit = s.interface.split(':')[0]
        edit_tool = 'edit_file' if edit == 'E0' else 'replace_file'

        def read(path):
            if supervisor.state().remaining_tool_calls <= 0:
                raise RuntimeError('Preload tool budget exhausted')
            supervisor.usage['tool_calls'] += 1
            action = ActionRequest('read_file', {'path': path})
            result = supervisor.perform(action, str(uuid.uuid4()))
            controller.observe(action, result.ok)
            observations.append(Observation(0, action, result))
            supervisor.persist_usage()

        if s.source_preload:
            read('src/solution.py')
        if 'public_cases' in s.context_fields:
            read('public_tests/cases.json')
        while not supervisor.exhausted():
            if (store.store.state / 'STOP').exists() or supervisor.cancelled():
                raise RuntimeError('Manual STOP')
            if store.totals()['active_wall_seconds'] >= 43200:
                raise RuntimeError('Active wall ceiling')
            phase = controller.phase or 'ACT'
            if phase_calls[phase] >= (s.inspect_calls if phase == 'INSPECT' else s.act_calls):
                reason = 'phase_budget_exhausted'
                break
            state = supervisor.state()
            payload, _ = wire_request(configuration, task.view, observations, state, controller, self.base_config,
                                      task.source if controller.observed.get('src/solution.py') is not None else None,
                                      task.cases)
            admission = self.tokenizer.prompt_upper_bound(payload['messages']) + payload['options']['num_predict']
            if admission > 4096 or admission > state.remaining_tokens:
                reason = 'context_admission_denied' if admission > 4096 else 'token_budget_exhausted'
                break
            call = str(uuid.uuid4())
            supervisor.usage['model_decisions'] += 1
            phase_calls[phase] += 1
            supervisor.persist_usage()
            supervisor.record_request(call, {'payload': payload, 'scaffold': configuration.scaffold_id})
            if not getattr(backend, 'offline', False):
                backend.deadline = time.monotonic() + min(30, supervisor.state().remaining_wall_seconds)
            response = backend.respond(payload)
            raw = response['message']['content']
            a, b = response.get('prompt_eval_count'), response.get('eval_count')
            if type(a) is not int or type(b) is not int or min(a, b) < 0:
                raise RuntimeError('Runner usage unavailable')
            if b > payload['options']['num_predict'] or a+b > admission or len(raw.encode()) > 4096:
                raise RuntimeError('Runner measured output/admission violation')
            supervisor.usage['input_tokens'] += a
            supervisor.usage['output_tokens'] += b
            inference += response.get('eval_duration', 0)/1e9 + response.get('prompt_eval_duration', 0)/1e9
            supervisor.store.event(job_id, 'runner', 'model_response',
                                    {'call': call, 'response': store.put(response, 'runner_response'), 'input_tokens': a, 'output_tokens': b})
            if supervisor.state().remaining_wall_seconds <= 0:
                reason = 'wall_clock_budget_exhausted'
                break
            action, _, _, _ = parse_output(raw, s.interface.split(':', 1)[1], edit)
            if action is None:
                reason = 'malformed_model_output'
                supervisor.store.event(job_id, 'supervisor', 'protocol_event',
                                       {'category': 'MALFORMED', 'before_phase': phase, 'after_phase': phase})
                if s.retry == 'stop':
                    break
                continue
            if action.tool != 'finish':
                supervisor.usage['tool_calls'] += 1
            try:
                authorize_interface(action, edit)
                if action.tool not in controller.actions():
                    raise ValueError('Action unavailable in current control state.')
                if action.tool == 'finish':
                    reason = 'give_up'
                    supervisor.store.event(job_id, 'supervisor', 'protocol_event',
                                           {'action': action.to_dict(), 'category': 'GIVE_UP', 'before_phase': phase, 'after_phase': phase})
                    break
                if action.tool == edit_tool and (supervisor.state().remaining_tool_calls < 1 or supervisor.state().remaining_wall_seconds < 5):
                    raise ValueError('Automatic verification reservation exhausted')
                if action.tool == 'run_public_tests':
                    raise ValueError('Verification is Supervisor-triggered')
                rejection = controller.rejection(action)
                if rejection:
                    raise ValueError(rejection)
                result = supervisor.perform(action, call)
            except (ValueError, OSError, UnicodeError) as exc:
                result = ActionResult(action.tool, False, error=str(exc))
            observation = Observation(supervisor.usage['model_decisions'], action, result)
            if s.rejection_feedback == 'generic':
                observation = historical_projection(observation)
            elif not result.ok and action.tool == 'edit_file' and action.arguments.get('old') == action.arguments.get('new'):
                observation = Observation(observation.step, action, ActionResult(action.tool, False, error='Edit is unchanged: old and new are identical.'))
            observations.append(observation)
            controller.observe(action, result.ok)
            supervisor.persist_usage()
            signature = digest(action.to_dict())
            repetition[signature] = repetition.get(signature, 0)+1
            supervisor.store.event(job_id, 'supervisor', 'protocol_event',
                                    {'action': action.to_dict(), 'result': result.to_dict(),
                                     'before_phase': phase, 'after_phase': controller.phase or 'ACT',
                                     'repeat_count': repetition[signature], 'calls': supervisor.usage['model_decisions'],
                                     'input_tokens': supervisor.usage['input_tokens'], 'output_tokens': supervisor.usage['output_tokens']})
            if action.tool == edit_tool and result.ok:
                formed = True
                supervisor.usage['tool_calls'] += 1
                verification = supervisor.perform(ActionRequest('run_public_tests', {}), str(uuid.uuid4()))
                outcome = verification.data['outcome']
                if outcome not in ('pass', 'fail'):
                    raise RuntimeError('Public verification infrastructure failure')
                reason = 'public_' + outcome
                supervisor.store.event(job_id, 'supervisor', 'protocol_event', {'category': 'PUBLIC_' + outcome.upper()})
                break
            if s.stagnation and not result.ok and repetition[signature] >= s.stagnation:
                reason = 'stagnation'
                break
        if supervisor.exhausted() and not formed and reason == 'decision_budget_exhausted':
            reason = supervisor.exhausted()
        supervisor.finish('finished', reason)
        return Result(configuration.scaffold_id, cohort_hash, task.task_id, task.task_hash, task.family, task.template,
                      formed, outcome, supervisor.usage['model_decisions'], supervisor.usage['input_tokens'],
                      supervisor.usage['output_tokens'], inference, supervisor.usage['wall_seconds'], job_id, reason)
