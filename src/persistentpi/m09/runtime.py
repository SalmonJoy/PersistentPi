"""Single-candidate executor using the existing trusted Supervisor and public verifier."""
import json
import os
import time
import uuid

from ..artifacts import atomic_write
from ..contracts import ActionRequest, ActionResult, Budget, DecisionState, Observation, canonical, digest
from ..interfaces import authorize_interface, parse_output
from ..m08.runtime import CaseVerifier
from ..m08.primitive_runtime import project as historical_projection
from ..supervisor import Supervisor
from ..telemetry import utc
from .analysis import Result
from .render import controller_for, wire_request


class FixtureCounter:
    def prompt_upper_bound(self, messages):
        return len(canonical(messages)) // 4 + 256


class ScriptedBackend:
    offline = True

    def __init__(self, sequence):
        self.sequence = iter(sequence)
        self.requests = []

    def respond(self, payload):
        self.requests.append(payload)
        value = next(self.sequence)
        if isinstance(value, BaseException):
            raise value
        if isinstance(value, dict) and 'message' in value:
            return value
        return {'message': {'content': value if isinstance(value, str) else canonical(value).decode()},
                'prompt_eval_count': 100, 'eval_count': 100, 'eval_duration': 1000000}


def new_supervisor(store, configuration, task, job_id, window, clock):
    budget = Budget(**window)
    mh = store.store.manifest('m09-task-run', {'protocol': '0.6', 'interface': {
        'edit_primitive': configuration.spec.interface.split(':')[0],
        'output_protocol': configuration.spec.interface.split(':', 1)[1]}, 'scaffold': configuration.scaffold_id})
    fields = {'id': job_id, 'experiment_id': store.id, 'trial_key': digest([store.id, configuration.scaffold_id, task.task_hash]),
              'mode': 'development', 'task_id': task.task_id, 'task_hash': task.task_hash, 'fixture_version': 'm09-1',
              'protocol_version': '0.6', 'scaffold_id': configuration.scaffold_id, 'scaffold_hash': configuration.scaffold_id,
              'scaffold_version': '1', 'seed': 42, 'replicate': 0, 'manifest_hash': mh, 'dirty': 0,
              'status': 'running', 'budget_json': canonical(window).decode(), 'usage_json': '{}', 'platform_json': '{}',
              'owner_pid': os.getpid(), 'created_utc': utc()}
    with store.db:
        store.db.execute('INSERT INTO runs(' + ','.join(fields) + ') VALUES(' + ','.join('?' for _ in fields) + ')', tuple(fields.values()))
        store.db.execute('UPDATE m09_jobs SET run_id=? WHERE id=?', (job_id, job_id))
    workspace = store.store.state / 'workspaces' / job_id
    atomic_write(workspace / 'src/solution.py', task.source.encode())
    atomic_write(workspace / 'public_tests/cases.json', canonical(task.cases))
    initial = store.artifacts.checkpoint(workspace)
    store.store.update_run(job_id, initial_checkpoint=initial.hash, selected_checkpoint=initial.hash)
    verifier = CaseVerifier(store.artifacts, job_id, task.cases, task.view.public_test_id)
    supervisor = Supervisor(store.store, store.artifacts, job_id, workspace, task.view, budget, verifier, clock)
    supervisor.interface = {'edit_primitive': configuration.spec.interface.split(':')[0]}
    return supervisor


class CandidateExecutor:
    offline = True

    def __init__(self, backend_factory, tokenizer, base_config, window, clock=time.monotonic):
        self.backend_factory, self.tokenizer, self.base_config = backend_factory, tokenizer, base_config
        self.window, self.clock = window, clock

    def evaluate(self, configuration, task, cohort_hash, job_id, store):
        supervisor = new_supervisor(store, configuration, task, job_id, self.window, self.clock)
        backend = self.backend_factory(configuration, task)
        if not getattr(backend, 'offline', False):
            raise RuntimeError('Live Runner inference is not enabled in M0.9B')
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
