"""Protocol 0.5 acquisition windows; fixed orchestration, semantic edits by Runner."""
from dataclasses import dataclass, replace
import json
from pathlib import Path
import sys
import time
import uuid

from .._verification import save_evaluation
from ..adapters.ollama import OllamaModel
from ..adapters.platform import execute
from ..artifacts import atomic_write
from ..contracts import ActionRequest, ActionResult, CheckpointRef, EvaluationResult, Observation, canonical, digest
from ..control import ControlSupervisor
from ..orchestration import OrchestrationController
from ..telemetry import utc
from .feedback import candidate_signatures, prompt


def observation_dict(value):
    return value.to_dict()


def observation_from(value):
    result = dict(value['result'])
    result.pop('contract_version',None)
    if result.get('checkpoint'):
        result['checkpoint'] = CheckpointRef(result['checkpoint']['hash'],result['checkpoint'].get('parent_hash'))
    return Observation(value['step'],ActionRequest.from_dict(value['action']),ActionResult(**result))


def restore_controller(value):
    c = OrchestrationController('V1',value['sources'],value['read_budget'])
    c.phase, c.epoch = value['phase'],value['epoch']
    c.reads, c.observed = value['successful_reads'],dict(value['observed_epochs'])
    c.visible, c.accepted_edits = set(value['visible_paths']),value['accepted_edits']
    if c.snapshot() != value:
        raise ValueError('Inconsistent restored controller')
    return c


class FeedbackModel(OllamaModel):
    def __init__(self, config, identity, controller, mode, tokenizer, client=None):
        super().__init__(config,identity,client)
        self.controller,self.mode,self.tokenizer = controller,mode,tokenizer

    def prompt(self, task, observations, state):
        return prompt(task,observations,state,self.config,self.controller,self.mode)

    def response_format(self, protocol, edit):
        from ..interfaces import action_schema
        schema = action_schema(edit)
        schema['anyOf'] = [b for b in schema['anyOf'] if b['properties']['tool']['enum'][0] in self.controller.actions()]
        return schema

    def admission(self, task, observations, state):
        messages,_ = self.prompt(task,observations,state)
        upper = self.tokenizer.prompt_upper_bound(messages)
        if upper + self.config['num_predict'] > self.config['num_ctx']:
            return None
        return upper + self.config['num_predict']


class CaseVerifier:
    execution_policy = 'bounded-python-1'

    def __init__(self, artifacts, run_id, cases, test_id, split='public'):
        self.artifacts,self.run_id,self.cases,self.test_id,self.split = artifacts,run_id,cases,test_id,split
        self.test_hash = digest(cases)

    def check(self, checkpoint, timeout, output_limit, cancelled=lambda:False):
        folder = self.artifacts.store.state/'evaluations'/self.run_id/(self.split+'-'+str(uuid.uuid4()))
        self.artifacts.restore(checkpoint,folder)
        cases = folder/'cases.json'
        atomic_write(cases,canonical(self.cases))
        output = folder/'structured.json'
        command = (sys.executable,'-I','-B',str(Path(__file__).with_name('case_harness.py')),
                   str(folder/'src/solution.py'),str(cases),str(output))
        process = execute(command,folder,timeout,output_limit,cancelled)
        structured = None
        if process.outcome in ('pass','fail'):
            if not output.is_file() or output.stat().st_size > 65536:
                raise ValueError('Missing/oversized structured case evidence')
            structured = json.loads(output.read_bytes())
            if [c['id'] for c in structured['cases']] != [c['id'] for c in self.cases]:
                raise ValueError('Public case order changed')
            if structured['outcome'] != process.outcome:
                raise ValueError('Verifier process/result disagreement')
        return EvaluationResult(self.split,process.outcome,{'pass':1.,'fail':0.}.get(process.outcome),
                                self.test_id,command,process.duration,process.output,process.truncated,process.exit_code,
                                {'version':1,'cleanup':process.cleanup,'cleanup_error':process.cleanup_error,
                                 'execution_policy':self.execution_policy,'structured_public':structured})


@dataclass(frozen=True)
class InitialPrefix:
    prefix_version: int
    task_id: str
    task_hash: str
    campaign_id: str
    manifest_hash: str
    scaffold_hash: str
    protocol: str
    original_checkpoint: str
    candidate_checkpoint: str | None
    transcript_hash: str
    public_result_hash: str | None
    acquisition_run: str
    state_artifact: str
    physical_receipts: tuple
    created_utc: str

    @property
    def id(self):
        return digest(self)


class Window(ControlSupervisor):
    def __init__(self, *args, controller, campaign, candidate_index, history=(), **kwargs):
        super().__init__(*args,controller=controller,**kwargs)
        if self.protocol != '0.5':
            raise ValueError('Acquisition windows require protocol 0.5')
        self.campaign,self.candidate_index = campaign,candidate_index
        self.observations = list(history)
        self.candidate = None
        self.receipts = []
        self.usage['token_usage_kind'] = campaign.usage_kind
        self.usage.update(candidate_attempts=0,accepted_edits=0,rejected_edits=0,inference_seconds=0.,verification_seconds=0.)
        self.step_offset = max((o.step for o in history),default=0)
        self.pending = None

    def cancelled(self):
        return super().cancelled() or self.campaign.cancelled()

    def state(self):
        state = super().state()
        remaining = self.campaign.remaining_limits(self.clock()-self.started)
        return replace(state,remaining_wall_seconds=min(state.remaining_wall_seconds,remaining['wall_seconds']),
                       remaining_tokens=min(state.remaining_tokens,remaining['tokens']))

    def receipt(self, identity, kind, payload):
        artifact = self.artifacts.put(canonical({'version':1,**payload}),'physical_cost','research')
        with self.store.db:
            self.store.db.execute('INSERT INTO m08_receipts VALUES(?,?,?,?)',(identity,self.run_id,kind,artifact))
        self.receipts.append(identity)
        self.store.event(self.run_id,'supervisor','physical_receipt',{'receipt_id':identity,'kind':kind,'payload_hash':artifact})

    def verify_candidate(self, source_call):
        checkpoint = self.artifacts.checkpoint(self.workspace,self.selected.hash)
        call,attempt = str(uuid.uuid4()),str(uuid.uuid4())
        self.selected = checkpoint
        self.usage['attempts'] += 1
        self.usage['candidate_attempts'] += 1
        self.usage['tool_calls'] += 1
        self.persist_usage()
        self.store.update_run(self.run_id,selected_checkpoint=checkpoint.hash)
        with self.store.db:
            self.store.db.execute('INSERT INTO attempts VALUES(?,?,?,?,?,?,?)',
                                 (attempt,self.run_id,1,checkpoint.hash,checkpoint.parent_hash,'pending',None))
        self.store.event(self.run_id,'control_plane','candidate_checkpoint',
                         {'version':1,'candidate_index':self.candidate_index,'checkpoint':checkpoint.to_dict(),'source_call_id':source_call})
        self.store.event(self.run_id,'control_plane','automatic_public_verification',{'call_id':call,'attempt_id':attempt})
        began = self.clock()
        result = self.verifier.check(checkpoint,min(5,self.state().remaining_wall_seconds),4096,self.cancelled)
        record = save_evaluation(self.store,self.artifacts,self.run_id,attempt,checkpoint,self.verifier.test_hash,result)
        structured = result.capabilities['structured_public']
        public_result = {'version':1,'outcome':result.outcome,'cases':structured['cases'] if structured else []}
        raw_hash = self.artifacts.put(canonical(public_result),'public_case_result','public')
        with self.store.db:
            self.store.db.execute('UPDATE attempts SET outcome=?,result_json=? WHERE id=?',
                                 (result.outcome,canonical(record).decode(),attempt))
        duration = self.clock()-began
        self.usage['verification_seconds'] += duration
        self.receipt(call,'tool',{'tool':'run_public_tests','candidates':1,'tool_calls':1,
                                 'verification_seconds':duration,'result_hash':raw_hash})
        observation = Observation(self.step_offset+self.usage['model_decisions'],ActionRequest('run_public_tests',{}),
                                  ActionResult('run_public_tests',result.outcome=='pass',
                                               {'structured_public':public_result},checkpoint=checkpoint))
        self.observations.append(observation)
        self.candidate = {'version':1,'index':self.candidate_index,'checkpoint':checkpoint.hash,
                          'outcome':result.outcome,'public_result_hash':raw_hash,
                          'workspace_hash':checkpoint.hash,
                          'transcript_hash':digest(self.campaign.transcript(self.run_id,[o.to_dict() for o in self.observations])),
                          'feedback_mode':'outcome_only' if self.store.db.execute('SELECT arm FROM m08_windows WHERE run_id=?',(self.run_id,)).fetchone()[0]=='O' else 'detailed',
                          **candidate_signatures((self.workspace/'src/solution.py').read_text(encoding='utf-8'))}
        self.store.event(self.run_id,'supervisor','candidate_completed',self.candidate)
        return result.outcome

    def finish(self, status, reason):
        self.persist_usage()
        self.store.update_run(self.run_id,status=status,stop_reason=reason,selected_checkpoint=self.selected.hash,
                              ended_utc=utc(),evaluation_status='pending' if status=='finished' else 'not_evaluated')
        self.store.event(self.run_id,'supervisor','runner_terminated',{'version':1,'reason':reason,'status':status,'usage':self.usage})

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
                    if action.tool == 'edit_file' and (self.state().remaining_tool_calls < 1 or self.state().remaining_wall_seconds < 5):
                        raise ValueError('Automatic verification reservation exhausted')
                    result = super().perform(action,call)
                except (ValueError,OSError,UnicodeError) as exc:
                    result = ActionResult(action.tool,False,error=str(exc))
                self.receipt(call+'-tool','tool',{'tool':action.tool,'tool_calls':1,'accepted':result.ok,
                    'error':result.error,'action_hash':digest(action),'checkpoint':self.selected.hash,
                    'duration_seconds':self.clock()-began})
                self.observations.append(Observation(self.step_offset+self.usage['model_decisions'],action,result))
                self.store.event(self.run_id,'supervisor','action_completed',{'call_id':call,'action':action.to_dict(),'result':result.to_dict()})
                if action.tool == 'edit_file':
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
