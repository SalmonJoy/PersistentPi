"""Trusted action boundary for reviewed fixture trials, not an OS sandbox."""
from pathlib import Path
import json
import time
import uuid

from ._verification import save_evaluation, VERIFIER_VERSION
from .artifacts import atomic_write, bounded_text, file_map, is_link, relative_name
from .contracts import ActionResult, DecisionState, Observation, PublicFeedback, canonical, digest
from .telemetry import utc
from .tools import authorize


class Supervisor:
    def __init__(self, store, artifacts, run_id, workspace, task, budget, verifier,
                 clock=time.monotonic):
        self.store, self.artifacts, self.run_id = store, artifacts, run_id
        self.workspace, self.task = Path(workspace), task
        self.budget, self.verifier, self.clock = budget, verifier, clock
        self.started = clock()
        self.usage = {'attempts': 0, 'model_decisions': 0, 'tool_calls': 0,
                      'input_tokens': 0, 'output_tokens': 0, 'wall_seconds': 0.0,
                      'token_usage_kind': 'simulated'}
        self.observations = []
        self.protocol = store.row(run_id)['protocol_version']
        self.interface = None
        self.funnel = None
        if self.protocol in ('0.3', '0.4', '0.5'):
            manifest_hash = store.row(run_id)['manifest_hash']
            manifest = json.loads(store.db.execute('SELECT json FROM manifests WHERE hash=?', (manifest_hash,)).fetchone()[0])
            self.interface = manifest['interface']
        self.last_action_hash = None
        from .contracts import CheckpointRef
        self.selected = CheckpointRef(store.row(run_id)['initial_checkpoint'])

    def persist_usage(self):
        self.usage['wall_seconds'] = max(0, self.clock() - self.started)
        self.store.update_run(self.run_id, usage_json=canonical(self.usage).decode())

    def cancelled(self):
        return bool(self.store.row(self.run_id)['stop_requested'])

    def state(self):
        b, u = self.budget, self.usage
        return DecisionState(b.max_attempts - u['attempts'],
                             b.max_model_decisions - u['model_decisions'],
                             b.max_tool_calls - u['tool_calls'],
                             b.max_tokens - u['input_tokens'] - u['output_tokens'],
                             max(0, b.max_wall_seconds - (self.clock() - self.started)))

    def exhausted(self):
        state = self.state()
        for field, reason in (('remaining_wall_seconds', 'wall_budget_exhausted'),
                              ('remaining_attempts', 'attempt_budget_exhausted'),
                              ('remaining_decisions', 'decision_budget_exhausted'),
                              ('remaining_tool_calls', 'tool_budget_exhausted'),
                              ('remaining_tokens', 'token_budget_exhausted')):
            if getattr(state, field) <= 0:
                return reason
        return None

    def path(self, name, write=False):
        relative_name(name)
        allowed = self.task.editable_paths if write else self.task.readable_paths
        if name not in allowed:
            raise ValueError('Protected or undeclared path')
        path = self.workspace / name
        for candidate in (self.workspace, *[self.workspace.joinpath(*Path(name).parts[:i])
                                           for i in range(1, len(Path(name).parts) + 1)]):
            if is_link(candidate):
                raise ValueError('Links/reparse points are forbidden')
        if not path.resolve().is_relative_to(self.workspace.resolve()):
            raise ValueError('Path escapes workspace')
        if not path.is_file():
            raise ValueError('Expected a regular file')
        return path

    def perform(self, action, call_id):
        if self.interface:
            from .interfaces import authorize_interface
            authorize_interface(action, self.interface['edit_primitive'])
        else:
            authorize(action)
        arguments = action.arguments
        if action.tool == 'read_file':
            path = self.path(arguments['path'])
            self.mark('action_authorized')
            self.mark('action_applicable')
            with path.open('rb') as stream:
                raw = stream.read(self.budget.max_output_bytes + 1)
            text, truncated = bounded_text(raw, self.budget.max_output_bytes)
            return ActionResult(action.tool, True, {'text': text, 'truncated': truncated})
        if action.tool in ('edit_file', 'replace_file'):
            path = self.path(arguments['path'], write=True)
            self.mark('action_authorized')
            files = file_map(self.workspace)
            before = files[arguments['path']].decode('utf-8')
            if action.tool == 'replace_file':
                after = arguments['content'].encode('utf-8')
                if b'\x00' in after or '\x00' in before:
                    raise ValueError('Replacement requires text files')
                if len(after) > self.budget.max_edit_bytes or len(files[arguments['path']]) > self.budget.max_edit_bytes:
                    raise ValueError('Replacement file size limit exceeded')
                if after == files[arguments['path']]:
                    raise ValueError('Replacement is unchanged')
            else:
                old, new = arguments['old'], arguments['new']
                if not old or old == new or len(canonical(arguments)) > self.budget.max_edit_bytes:
                    raise ValueError('Edit is empty, unchanged or too large')
                if before.count(old) != 1:
                    raise ValueError('Edit requires exactly one matching occurrence')
                after = before.replace(old, new, 1).encode('utf-8')
            size = sum(map(len, files.values())) - len(files[arguments['path']]) + len(after)
            if size > self.budget.max_workspace_bytes:
                raise ValueError('Workspace byte budget exceeded')
            if self.verifier.execution_policy == 'bounded-python-1':
                from .bounded_python import parse
                parse(after.decode('utf-8'))
            self.mark('action_applicable')
            if action.tool == 'replace_file':
                before_checkpoint = self.artifacts.checkpoint(self.workspace, self.selected.hash)
                self.mark('checkpoint_created')
                self.store.event(self.run_id, 'supervisor', 'pre_edit_checkpoint',
                                 {'call_id': call_id, 'checkpoint': before_checkpoint.to_dict()})
            atomic_write(path, after)
            return ActionResult(action.tool, True, {'path': arguments['path'], 'bytes': len(after)})
        self.mark('action_authorized')
        self.mark('action_applicable')
        checkpoint = self.artifacts.checkpoint(self.workspace, self.selected.hash)
        self.mark('checkpoint_created')
        attempt_id = str(uuid.uuid4())
        self.usage['attempts'] += 1
        self.selected = checkpoint
        self.persist_usage()
        self.store.update_run(self.run_id, selected_checkpoint=checkpoint.hash)
        with self.store.db:
            self.store.db.execute('INSERT INTO attempts VALUES(?,?,?,?,?,?,?)',
                                 (attempt_id, self.run_id, self.usage['attempts'], checkpoint.hash,
                                  checkpoint.parent_hash, 'pending', None))
        self.store.event(self.run_id, 'public_verifier', 'verification_started',
                         {'call_id': call_id, 'attempt_id': attempt_id, 'checkpoint': checkpoint.to_dict(),
                          'verifier_id': self.verifier.test_id, 'verifier_hash': self.verifier.test_hash,
                          'verifier_version': VERIFIER_VERSION})
        self.mark('action_executed')
        self.mark('public_verification_reached')
        timeout = min(self.budget.test_timeout_seconds, self.state().remaining_wall_seconds)
        result = self.verifier.check(checkpoint, timeout, self.budget.max_output_bytes, self.cancelled)
        if result.split != 'public':
            raise RuntimeError('Public verifier returned a private result')
        record = save_evaluation(self.store, self.artifacts, self.run_id, attempt_id,
                                 checkpoint, self.verifier.test_hash, result)
        with self.store.db:
            self.store.db.execute('UPDATE attempts SET outcome=?,result_json=? WHERE id=?',
                                 (result.outcome, canonical(record).decode(), attempt_id))
        self.store.event(self.run_id, 'public_verifier', 'verification_completed',
                         {'call_id': call_id, 'attempt_id': attempt_id, 'result': record})
        if result.outcome == 'pass':
            self.mark('public_verification_passed')
        feedback = PublicFeedback(result.outcome, result.test_id, VERIFIER_VERSION,
                                  result.duration_seconds, result.output, result.output_truncated)
        return ActionResult(action.tool, result.outcome == 'pass', feedback.to_dict(), checkpoint=checkpoint)

    def finish(self, status, reason):
        if self.funnel is not None:
            self.flush_funnel(reason)
        if self.protocol == '0.2' and 'budget' in reason:
            self.classify('budget_exhausted', {'reason': reason})
        self.persist_usage()
        self.store.update_run(self.run_id, status=status, stop_reason=reason,
                              selected_checkpoint=self.selected.hash, ended_utc=utc(),
                              evaluation_status='pending' if status == 'finished' else 'not_evaluated')
        self.store.event(self.run_id, 'supervisor', 'runner_terminated',
                         {'status': status, 'reason': reason, 'usage': self.usage,
                          'checkpoint': self.selected.to_dict()})

    def mark(self, stage):
        if self.funnel is not None:
            self.funnel['stages'][stage] = True

    def flush_funnel(self, reason, evidence=None):
        if self.funnel is None:
            return
        stages = self.funnel['stages']
        mandatory = ('model_response_received', 'parse_valid', 'schema_valid', 'action_authorized',
                     'action_applicable', 'action_executed')
        exit_stage = next((s for s in mandatory if not stages[s]), None)
        if exit_stage is None and stages['public_verification_reached'] and not stages['public_verification_passed']:
            exit_stage = 'public_verification_passed'
        family = ('backend/control failure' if exit_stage == 'model_response_received' else
                  'format failure' if exit_stage in mandatory[1:3] else
                  'tool-contract failure' if exit_stage in mandatory[3:5] else
                  'coding failure' if exit_stage == 'public_verification_passed' and reason == 'public_fail' else
                  'control/operation' if exit_stage else 'none')
        self.funnel.update(exit_stage=exit_stage, reason=reason, failure_family=family,
                           evidence=(evidence or '')[:500])
        self.store.event(self.run_id, 'supervisor', 'decision_funnel', self.funnel)
        self.funnel = None

    def classify(self, category, evidence, call_id=None):
        self.store.event(self.run_id, 'supervisor', 'failure_classified',
                         {'taxonomy_version': '0.2', 'category': category,
                          'call_id': call_id, 'evidence': evidence})

    def record_request(self, call_id, request):
        artifact = self.artifacts.put(canonical(request), 'model_request', 'public')
        self.store.event(self.run_id, 'supervisor', 'model_request',
                         {'call_id': call_id, 'request_artifact': artifact})

    def account_measured(self, reply, call_id):
        raw = self.artifacts.put(reply.raw_output.encode('utf-8'), 'model_output', 'public')
        self.store.event(self.run_id, 'runner', 'model_call_completed',
                         {'call_id': call_id, 'telemetry_version': 1, 'telemetry': reply.telemetry,
                          'raw_output_artifact': raw, 'error': reply.error,
                          'valid_structured_output': reply.action is not None})
        if self.funnel is not None:
            self.mark('model_response_received') if reply.telemetry.get('request_sent') and reply.status not in ('timeout', 'infrastructure_failure') else None
            for stage, passed in reply.telemetry.get('interface_parse', {}).items():
                if passed:
                    self.mark(stage)
        if reply.action is not None:
            self.usage['valid_structured_outputs'] += 1
        elif reply.status == 'malformed_model_output':
            self.usage['invalid_structured_outputs'] += 1
        else:
            self.usage['backend_failures'] += 1
        for name, value in (('input_tokens', reply.input_tokens), ('output_tokens', reply.output_tokens)):
            if value is None:
                self.usage[name] = None
            elif type(value) is not int or value < 0:
                raise ValueError('Invalid measured usage')
            else:
                self.usage[name] += value
        self.persist_usage()
        if self.cancelled():
            self.finish('stopped', 'manual_stop')
            return 'stop'
        if reply.status in ('timeout', 'infrastructure_failure') or None in (reply.input_tokens, reply.output_tokens):
            category = reply.status if reply.status in ('timeout', 'infrastructure_failure') else 'infrastructure_failure'
            self.classify(category, {'error': reply.error, 'usage_complete': None not in (reply.input_tokens, reply.output_tokens)}, call_id)
            self.finish('interrupted', 'model_' + category)
            return 'stop'
        total = self.usage['input_tokens'] + self.usage['output_tokens']
        if total > self.budget.max_tokens:
            self.store.event(self.run_id, 'supervisor', 'measured_token_overrun',
                             {'call_id': call_id, 'tokens': total, 'limit': self.budget.max_tokens,
                              'action_executed': False})
            self.finish('finished', 'token_budget_exhausted')
            return 'stop'
        if reply.action is None:
            self.flush_funnel(reply.error or 'malformed_model_output', reply.raw_output[:500])
            self.classify('malformed_model_output', {'error': reply.error, 'raw_output_artifact': raw}, call_id)
            self.finish('finished', 'malformed_model_output')
            return 'stop'
        return 'continue'

    def run(self, runner):
        measured = getattr(runner.model, 'usage_kind', 'simulated') == 'measured'
        if measured:
            if self.protocol not in ('0.2', '0.3', '0.4') or self.verifier.execution_policy != 'bounded-python-1':
                raise ValueError('Measured Runner requires protocol 0.2 and bounded-python-1')
            self.usage.update(token_usage_kind='measured', valid_structured_outputs=0,
                              invalid_structured_outputs=0, backend_failures=0)
        try:
            while True:
                if self.cancelled():
                    self.finish('stopped', 'manual_stop')
                    break
                reason = self.exhausted()
                if reason:
                    self.finish('finished', reason)
                    break
                step = self.usage['model_decisions'] + 1
                call_id = str(uuid.uuid4())
                if self.interface:
                    from .interfaces import STAGES
                    self.funnel = {'funnel_version': 1, 'call_id': call_id,
                        'protocol_version': self.interface['output_protocol'],
                        'edit_primitive': self.interface['edit_primitive'], 'tool': None,
                        'stages': dict.fromkeys(STAGES, False)}
                self.usage['model_decisions'] = step
                self.persist_usage()
                self.store.event(self.run_id, 'runner', 'decision_started', {'call_id': call_id, 'step': step})
                started = self.clock()
                reply = runner.next_action(self.task, self.observations, self.state(),
                                           lambda request: self.record_request(call_id, request))
                if measured:
                    disposition = self.account_measured(reply, call_id)
                    if disposition == 'stop':
                        break
                cost = reply.input_tokens + reply.output_tokens
                if not measured and cost > self.state().remaining_tokens:
                    self.store.event(self.run_id, 'supervisor', 'token_admission_denied',
                                     {'call_id': call_id, 'estimated_tokens': cost, 'usage_kind': reply.usage_kind})
                    self.finish('finished', 'token_budget_exhausted')
                    break
                if not measured:
                    self.usage['input_tokens'] += reply.input_tokens
                    self.usage['output_tokens'] += reply.output_tokens
                self.persist_usage()
                request = self.artifacts.put(canonical(reply.action), 'action_request', 'public')
                self.store.event(self.run_id, 'runner', 'decision_completed',
                                 {'call_id': call_id, 'action_artifact': request,
                                  'input_tokens': reply.input_tokens, 'output_tokens': reply.output_tokens,
                                  'usage_kind': reply.usage_kind, 'duration_seconds': self.clock() - started})
                if self.cancelled():
                    self.finish('stopped', 'manual_stop')
                    break
                if self.state().remaining_wall_seconds <= 0:
                    self.finish('finished', 'wall_budget_exhausted')
                    break
                action = reply.action
                if self.funnel is not None:
                    self.funnel['tool'] = action.tool
                if measured:
                    key = digest(action)
                    if key == self.last_action_hash:
                        self.classify('repeated_action', {'action_hash': key}, call_id)
                    self.last_action_hash = key
                if action.tool == 'finish':
                    if not set(action.arguments) - {'reason'} and (not measured or isinstance(action.arguments.get('reason', ''), str)):
                        for stage in ('action_authorized', 'action_applicable', 'action_executed'):
                            self.mark(stage)
                        self.finish('finished', 'explicit_finish')
                        break
                    if not measured:
                        raise ValueError('Invalid finish request')
                self.usage['tool_calls'] += 1
                self.persist_usage()
                self.store.event(self.run_id, 'supervisor', 'action_started',
                                 {'call_id': call_id, 'action_artifact': request})
                started = self.clock()
                prior_attempts = self.usage['attempts']
                try:
                    result = self.perform(action, call_id)
                except (ValueError, OSError, UnicodeError) as exc:
                    if self.usage['attempts'] != prior_attempts:
                        raise
                    result = ActionResult(action.tool, False, error=str(exc))
                artifact = self.artifacts.put(canonical(result), 'action_result', 'public')
                self.store.event(self.run_id, 'supervisor', 'action_completed',
                                 {'call_id': call_id, 'ok': result.ok, 'result_artifact': artifact,
                                  'duration_seconds': self.clock() - started, 'usage': self.usage})
                self.observations.append(Observation(step, action, result))
                if self.funnel is not None:
                    if not result.error:
                        self.mark('action_executed')
                    reason = result.error or ('public_' + result.data['outcome'] if action.tool == 'run_public_tests' else 'completed_nonverification_action')
                    self.flush_funnel(reason, result.error)
                if measured:
                    category = None
                    if result.error:
                        category = 'incorrect_edit' if action.tool == 'edit_file' and 'path' not in result.error.lower() else 'invalid_action'
                    elif result.data.get('outcome') == 'fail':
                        category = 'public_test_failure'
                    elif result.data.get('outcome') == 'timeout':
                        category = 'timeout'
                    elif result.data.get('outcome') == 'error':
                        category = 'infrastructure_failure'
                    if category:
                        self.classify(category, {'result_artifact': artifact}, call_id)
                if action.tool == 'run_public_tests' and result.data.get('outcome') == 'pass':
                    self.finish('stopped' if self.cancelled() else 'finished',
                                'manual_stop' if self.cancelled() else 'public_success')
                    break
        except KeyboardInterrupt:
            self.finish('stopped', 'keyboard_interrupt')
        except Exception as exc:
            self.store.event(self.run_id, 'supervisor', 'execution_error',
                             {'exception_type': type(exc).__name__, 'message': str(exc)[:2048]})
            if measured:
                self.classify('infrastructure_failure', {'exception_type': type(exc).__name__})
            self.finish('interrupted', 'execution_error')
        return self.store.row(self.run_id)
