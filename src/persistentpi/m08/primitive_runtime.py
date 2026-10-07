"""M0.8D primitive adapter; historical M0.8 execution files remain frozen."""
from dataclasses import replace
import json
import uuid

from ..contracts import ActionRequest, ActionResult, Observation, canonical, digest
from ..interfaces import registry
from ..orchestration import OrchestrationController
from ..prompts import build_prompt
from .acquisition_pilot import LEGACY
from .feedback import prompt as historical_prompt
from .runtime import FeedbackModel, Window, observation_dict


class PrimitiveController(OrchestrationController):
    def __init__(self, sources, primitive):
        if primitive not in ('E0', 'E1'):
            raise ValueError('Unknown primitive')
        self.primitive = primitive
        super().__init__('V1', sources, 2)

    def actions(self):
        return tuple('replace_file' if a == 'edit_file' and self.primitive == 'E1' else a
                     for a in super().actions())

    def observe(self, action, successful):
        # Only the controller's edit counter needs an identifier adapter.
        # Actual model actions and Supervisor application are never transformed.
        counted = ActionRequest('edit_file', action.arguments) if action.tool == 'replace_file' else action
        super().observe(counted, successful)


def restore(value, primitive):
    c = PrimitiveController(value['sources'], primitive)
    c.phase, c.epoch = value['phase'], value['epoch']
    c.reads, c.observed = value['successful_reads'], dict(value['observed_epochs'])
    c.visible, c.accepted_edits = set(value['visible_paths']), value['accepted_edits']
    if c.snapshot() != value:
        raise ValueError('Inconsistent primitive controller')
    return c


def project(observation):
    if (observation.action.tool == 'replace_file' and not observation.result.ok and
            observation.result.error in ('Replacement is unchanged', 'Replacement file size limit exceeded')):
        return replace(observation, result=replace(observation.result, error=LEGACY))
    return observation


def primitive_prompt(task, observations, state, config, controller):
    if config['edit_primitive'] == 'E0':
        return historical_prompt(task, observations, state, config, controller, 'detailed')
    projected = tuple(project(o) for o in observations)
    unpacked_context = {**config['context'], 'max_bytes': 1000000}
    messages, metadata = build_prompt(task, projected, state, unpacked_context,
                                      config['output_protocol'], 'E1')
    public = json.loads(messages[1]['content'])
    public['budget'].pop('remaining_attempts', None)
    public['tools'] = {k:v for k,v in registry('E1').items() if k in controller.actions()}
    public['control'] = {'policy':'C3', 'version':'inspect-act-1', 'phase':controller.phase,
                         'successful_reads':controller.reads, 'inspection_budget':2,
                         'available_actions':list(controller.actions())}
    messages[0]['content'] += ('\nThe control state and available_actions below override the general action listing. '
                               'finish means GIVE_UP. Choose only an available action.')
    # There is no public-verification history before this study's terminal candidate.
    if any(o.action.tool == 'run_public_tests' for o in observations):
        raise ValueError('M0.8D prohibits repair feedback')
    while True:
        messages[1]['content'] = canonical(public).decode()
        if len(canonical(messages)) <= config['context']['max_bytes']:
            break
        if not public['observations']:
            raise ValueError('Task context exceeds prompt bound')
        public['observations'].pop(0)
    metadata.update(prompt_version='m08-window-1', context_version='m08-equal-feedback-reserve-1',
                    prompt_hash=digest(messages), prompt_bytes=len(canonical(messages)),
                    observations_included=len(public['observations']),
                    observations_dropped=len(observations)-len(public['observations']),
                    reserved_prompt_bytes=len(canonical(messages)))
    return messages, metadata


class PrimitiveModel(FeedbackModel):
    def prompt(self, task, observations, state):
        return primitive_prompt(task, observations, state, self.config, self.controller)


class PrimitiveWindow(Window):
    """Frozen Window.run loop with only two edit-identifier predicates generalized.

    A parity test compares this method's AST against historical Window.run.
    Supervisor, verification, budgets, admission, receipts and stop rules are inherited.
    """
    def run(self, runner):
        reason,status = None,'finished'
        try:
            while True:
                if self.cancelled() or self.campaign.cancelled():
                    reason,status = 'manual_stop','stopped'
                    break
                reason = self.exhausted()
                if reason:
                    break
                self.campaign.check_limits(active_wall=self.clock()-self.started)
                state = self.state()
                admission = runner.model.admission(self.task,self.observations,state)
                if admission is None:
                    reason = 'context_admission_denied'
                    break
                if admission > state.remaining_tokens:
                    reason = 'token_budget_exhausted'
                    break
                self.campaign.check_limits(reserve_tokens=admission,active_wall=self.clock()-self.started)
                call = str(uuid.uuid4())
                self.usage['model_decisions'] += 1
                self.persist_usage()
                self.store.event(self.run_id,'runner','decision_started',{'call_id':call,'window_decision':self.usage['model_decisions']})
                began = self.clock()
                phase = self.controller.phase
                reply = runner.next_action(self.task,self.observations,self.state(),lambda r:self.record_request(call,r))
                inference = (reply.telemetry.get('prompt_eval_duration',0) or 0)+(reply.telemetry.get('eval_duration',0) or 0)
                inference = inference/1e9
                raw = self.artifacts.put(reply.raw_output.encode(),'model_output','public')
                self.store.event(self.run_id,'runner','model_call_completed',{'call_id':call,'telemetry':reply.telemetry,
                                                                            'output_hash':raw,'status':reply.status})
                if None in (reply.input_tokens,reply.output_tokens):
                    reason,status = 'model_unknown_usage','interrupted'
                    break
                if any(type(x) is not int or x<0 for x in (reply.input_tokens,reply.output_tokens)):
                    raise ValueError('Invalid model usage')
                if reply.usage_kind!=self.campaign.usage_kind:
                    raise ValueError('Measured/simulated model accounting mismatch')
                self.usage['input_tokens'] += reply.input_tokens
                self.usage['output_tokens'] += reply.output_tokens
                self.usage['inference_seconds'] += inference
                self.receipt(call,'model',{'model_decisions':1,'input_tokens':reply.input_tokens,
                    'output_tokens':reply.output_tokens,'tokens':reply.input_tokens+reply.output_tokens,
                    'inference_seconds':inference,'request_wall_seconds':self.clock()-began,
                    'usage_kind':reply.usage_kind,'semantic_action':reply.action.tool if reply.action else None,
                    'control_phase':phase})
                self.persist_usage()
                if reply.output_tokens>512 or reply.input_tokens+reply.output_tokens>admission or self.usage['input_tokens']+self.usage['output_tokens'] > self.budget.max_tokens:
                    reason,status = 'measured_token_bound_violation','interrupted'
                    break
                if reply.status in ('timeout','infrastructure_failure'):
                    reason,status = 'model_'+reply.status,'interrupted'
                    break
                if reply.action is None:
                    reason = 'malformed_model_output'
                    break
                if self.cancelled() or self.campaign.cancelled():
                    reason,status = 'manual_stop','stopped'
                    break
                if self.state().remaining_wall_seconds <= 0:
                    reason = 'wall_budget_exhausted'
                    break
                action = reply.action
                self.store.event(self.run_id,'runner','decision_completed',{'call_id':call,'action':action.to_dict()})
                if action.tool == 'finish' and not set(action.arguments)-{'reason'} and isinstance(action.arguments.get('reason',''),str):
                    reason = 'give_up'
                    break
                self.usage['tool_calls'] += 1
                self.persist_usage()
                began = self.clock()
                try:
                    if action.tool == self.edit_tool and (self.state().remaining_tool_calls < 1 or self.state().remaining_wall_seconds < 5):
                        raise ValueError('Automatic verification reservation exhausted')
                    result = super().perform(action,call)
                except (ValueError,OSError,UnicodeError) as exc:
                    result = ActionResult(action.tool,False,error=str(exc))
                self.receipt(call+'-tool','tool',{'tool':action.tool,'tool_calls':1,'accepted':result.ok,
                    'error':result.error,'action_hash':digest(action),'checkpoint':self.selected.hash,
                    'duration_seconds':self.clock()-began})
                self.observations.append(Observation(self.step_offset+self.usage['model_decisions'],action,result))
                self.store.event(self.run_id,'supervisor','action_completed',{'call_id':call,'action':action.to_dict(),'result':result.to_dict()})
                if action.tool == self.edit_tool:
                    self.usage['accepted_edits' if result.ok else 'rejected_edits'] += 1
                    if result.ok:
                        if self.cancelled() or self.campaign.cancelled():
                            reason,status = 'manual_stop','stopped'
                            break
                        outcome = self.verify_candidate(call)
                        reason = 'public_'+outcome
                        if outcome not in ('pass','fail'):
                            status = 'stopped' if outcome=='stopped' else 'interrupted'
                        break
        except KeyboardInterrupt:
            reason,status = 'keyboard_interrupt','stopped'
        except Exception as exc:
            reason,status = 'infrastructure_error','interrupted'
            self.store.event(self.run_id,'control_plane','window_error',{'type':type(exc).__name__,'message':str(exc)[:1000]})
        self.finish(status,reason)
        self.receipt(self.run_id+'-wall','window',{'wall_seconds':self.usage['wall_seconds']})
        state = {'version':1,'controller':self.controller.snapshot(),
                 'observations':[observation_dict(o) for o in self.observations],
                 'candidate':self.candidate,'selected_checkpoint':self.selected.hash,
                 'status':status,'stop_reason':reason,'usage':self.usage,'receipt_ids':self.receipts}
        artifact = self.artifacts.put(canonical(state),'window_state','research')
        with self.store.db:
            self.store.db.execute('UPDATE m08_windows SET state_artifact=? WHERE run_id=?',(artifact,self.run_id))
        return state,artifact
