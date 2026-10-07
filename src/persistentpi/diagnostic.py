"""Versioned M0.5 diagnostic interventions; existing Supervisor mediates every write."""
import ast
from dataclasses import replace
import json
import time
import uuid

from .adapters.ollama import OllamaModel
from .calibration import condition as original_condition
from .contracts import ActionRequest,ActionResult,canonical,digest
from .interfaces import STAGES
from .prompts import SYSTEM,build_prompt
from .supervisor import Supervisor

CONDITIONS=('A1','A2','A3')


def model_metadata(show):
    finetune=show.get('model_info',{}).get('general.finetune')
    return {'instruction_metadata':finetune,'chat_template_present':'.Messages' in show.get('template',''),
        'instruction_status':'metadata_declares_instruct' if finetune=='Instruct' else 'not_established',
        'training_provenance_independently_verified':False}


def decision_schema(label):
    if label not in ('A2','A3'):raise ValueError('Restricted decision condition required')
    properties={'decision':{'type':'string','const':'EDIT' if label=='A2' else 'REPLACE'}}
    required=['decision']
    for field in (('path','old','new') if label=='A2' else ('content',)):
        properties[field]={'type':'string'};required.append(field)
    return {'oneOf':[{'type':'object','properties':properties,'required':required,'additionalProperties':False},
        {'type':'object','properties':{'decision':{'type':'string','const':'GIVE_UP'}},
            'required':['decision'],'additionalProperties':False}]}


def parse_decision(content,label,target):
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('Duplicate key')
            result[k]=v
        return result
    def reject(value):raise ValueError('Nonfinite JSON')
    stages={'parse_valid':False,'schema_valid':False}
    try:
        value=json.loads(content,object_pairs_hook=pairs,parse_constant=reject)
        stages['parse_valid']=True
        if not isinstance(value,dict):raise ValueError('Object required')
        fields={'decision'} if value.get('decision')=='GIVE_UP' else (
            {'decision','path','old','new'} if label=='A2' else {'decision','content'})
        if set(value)!=fields or any(not isinstance(v,str) for v in value.values()):raise ValueError('Wrong decision fields')
        if value['decision']=='GIVE_UP':action=ActionRequest('finish',{'reason':'GIVE_UP'})
        elif label=='A2' and value['decision']=='EDIT':action=ActionRequest('edit_file',{k:value[k] for k in ('path','old','new')})
        elif label=='A3' and value['decision']=='REPLACE':action=ActionRequest('replace_file',{'path':target,'content':value['content']})
        else:raise ValueError('Decision is unavailable in this condition')
        stages['schema_valid']=True
        return action,stages,None,None
    except (ValueError,TypeError,RecursionError) as exc:
        return None,stages,'schema_valid' if stages['parse_valid'] else 'parse_valid',str(exc)


def preload(supervisor):
    files={name:supervisor.path(name).read_bytes().decode('utf-8') for name in supervisor.task.readable_paths}
    artifact=supervisor.artifacts.put(canonical(files),'initial_visible_files','public')
    supervisor.store.event(supervisor.run_id,'control_plane','diagnostic_preload',
        {'policy':'complete-initial-readable-files-1','artifact':artifact,'files':{k:digest(v) for k,v in files.items()}})
    return files


class DiagnosticModel(OllamaModel):
    def __init__(self,config,identity,files,client=None):
        super().__init__(config,identity,client)
        self.files=dict(files)
        self.label=config['diagnostic_condition']
        if self.label not in CONDITIONS:raise ValueError('Unknown diagnostic condition')

    def prompt(self,task,observations,state):
        if set(self.files)!=set(task.readable_paths):raise ValueError('Complete permitted files required')
        if len(task.editable_paths)!=1:raise ValueError('Diagnostic requires one explicit target')
        self.target=task.editable_paths[0]
        messages,metadata=build_prompt(task,observations,state,self.config['context'],'runner-json-schema-1','E0')
        public=json.loads(messages[1]['content'])
        public.update(initial_visible_files=self.files,target_file=self.target)
        if self.label!='A1':
            del public['tools']
            contract=('Return exactly one JSON decision: {"decision":"EDIT","path":"'+self.target+'","old":"exact existing text","new":"replacement text"} or {"decision":"GIVE_UP"}.'
                if self.label=='A2' else 'Return exactly one JSON decision: {"decision":"REPLACE","content":"complete replacement file text"} or {"decision":"GIVE_UP"}.')
            messages[0]['content']=('You are solving a coding task. '+contract+'\nNo prose, markdown or reasoning. '
                'There is one coding decision. The trusted harness applies a valid nonempty change and runs public tests.\n'
                +SYSTEM[SYSTEM.index('Code runs as bounded'):])
        messages[0]['content']+='\nComplete initial visible files are supplied as data. No hidden information is supplied.'
        while True:
            messages[1]['content']=canonical(public).decode()
            if len(canonical(messages))<=self.config['context']['max_bytes']:break
            if not public['observations']:raise ValueError('Complete preload exceeds context byte limit; never truncate source')
            public['observations'].pop(0)
        metadata.update(prompt_version='m05-'+self.label+'-1',prompt_hash=digest(messages),prompt_bytes=len(canonical(messages)),
            observations_included=len(public['observations']),observations_dropped=len(observations)-len(public['observations']),
            diagnostic_condition=self.label,initial_visible_files_hash=digest(self.files))
        return messages,metadata

    def response_format(self,protocol,edit):
        return super().response_format(protocol,edit) if self.label=='A1' else decision_schema(self.label)

    def parse_response(self,content,protocol,edit):
        return super().parse_response(content,protocol,edit) if self.label=='A1' else parse_decision(content,self.label,self.target)


def configured(base,tag,label,tasks,split,plan,entry):
    if label not in CONDITIONS or plan['output_ceiling']!=512:raise ValueError('Unknown condition/output configuration')
    edit='E1' if label=='A3' else 'E0'
    resolved=original_condition(base,tasks,'runner-json-schema-1',edit,tag+':'+label,'m05',split,(1,))
    model={**resolved.manifest['model'],'model':tag,'num_predict':plan['output_ceiling'],
        'diagnostic_condition':label,'prompt_version':'m05-'+label+'-1','thinking_policy':'explicit-false-1','think':False,
        'expected_digest':entry['identity']['digest'],'expected_runtime_version':entry['identity']['runtime_version']}
    scaffold={**resolved.manifest['scaffold'],'scaffold_id':'m05-'+label,'parent_scaffold_id':'interface-calibration-v1',
        'scaffold_hash':digest({'parent':resolved.manifest['scaffold'],'condition':label,'plan':digest(plan),
            'diagnostic_code':base.manifest['code_hashes']['src/persistentpi/diagnostic.py']})}
    return replace(resolved,manifest={**resolved.manifest,'model':model,'scaffold':scaffold,
        'm05_condition':label,'m05_model':tag,'m05_plan_hash':digest(plan),'diagnostic_protocol':'m05-'+label+'-1'})


class DiagnosticSupervisor(Supervisor):
    def __init__(self,*args,condition,**kwargs):
        super().__init__(*args,**kwargs)
        if condition not in CONDITIONS:raise ValueError('Unknown diagnostic condition')
        self.condition=condition
        self.auto_verifying=False

    def perform(self,action,call_id):
        if self.condition!='A1':
            allowed='replace_file' if self.condition=='A3' else 'edit_file'
            if action.tool!=allowed and not (action.tool=='run_public_tests' and self.auto_verifying):
                raise ValueError('Action disabled by diagnostic contract')
        if action.tool not in ('edit_file','replace_file'):return super().perform(action,call_id)
        quality={'call_id':call_id,'syntax_valid':None,'bounded_policy_valid':None,'proposed_change':False,
            'valid_modification_generated':False,'actually_changed':False}
        try:
            before=self.path(action.arguments['path'],write=True).read_bytes().decode('utf-8')
            if action.tool=='replace_file':after=action.arguments['content']
            else:
                old=action.arguments['old']
                if not old or before.count(old)!=1:raise ValueError('Unmatched patch')
                after=before.replace(old,action.arguments['new'],1)
            quality['proposed_change']=bool(after) and after!=before
            try:
                ast.parse(after);quality['syntax_valid']=True
            except (SyntaxError,ValueError):quality['syntax_valid']=False
            from .bounded_python import parse
            try:
                parse(after);quality['bounded_policy_valid']=True
            except (ValueError,SyntaxError):quality['bounded_policy_valid']=False
        except (ValueError,OSError,KeyError,TypeError):pass
        try:
            result=super().perform(action,call_id)
            quality['actually_changed']=result.ok
            quality['valid_modification_generated']=result.ok and quality['proposed_change']
            return result
        finally:
            self.store.event(self.run_id,'supervisor','diagnostic_candidate',quality)

    def operation(self,action,call_id):
        request=self.artifacts.put(canonical(action),'action_request','public')
        self.usage['tool_calls']+=1;self.persist_usage()
        self.store.event(self.run_id,'supervisor','action_started',{'call_id':call_id,'action_artifact':request})
        started=self.clock()
        try:result=self.perform(action,call_id)
        except (ValueError,OSError,UnicodeError) as exc:
            if action.tool=='run_public_tests':raise
            result=ActionResult(action.tool,False,error=str(exc))
        artifact=self.artifacts.put(canonical(result),'action_result','public')
        self.store.event(self.run_id,'supervisor','action_completed',{'call_id':call_id,'ok':result.ok,
            'result_artifact':artifact,'duration_seconds':self.clock()-started,'usage':self.usage})
        return result

    def run(self,runner):
        if self.condition=='A1':return super().run(runner)
        self.usage.update(token_usage_kind='measured',valid_structured_outputs=0,invalid_structured_outputs=0,backend_failures=0)
        try:
            if self.cancelled():self.finish('stopped','manual_stop');return self.store.row(self.run_id)
            if self.exhausted():self.finish('finished',self.exhausted());return self.store.row(self.run_id)
            call_id=str(uuid.uuid4())
            self.funnel={'funnel_version':1,'call_id':call_id,'protocol_version':'m05-'+self.condition+'-1',
                'edit_primitive':self.interface['edit_primitive'],'tool':None,'stages':dict.fromkeys(STAGES,False)}
            self.usage['model_decisions']=1;self.persist_usage()
            self.store.event(self.run_id,'runner','decision_started',{'call_id':call_id,'step':1})
            reply=runner.next_action(self.task,[],self.state(),lambda r:self.record_request(call_id,r))
            if self.account_measured(reply,call_id)=='stop':return self.store.row(self.run_id)
            request=self.artifacts.put(canonical(reply.action),'action_request','public')
            self.store.event(self.run_id,'runner','decision_completed',{'call_id':call_id,'action_artifact':request,
                'input_tokens':reply.input_tokens,'output_tokens':reply.output_tokens,'usage_kind':reply.usage_kind})
            self.funnel['tool']=reply.action.tool
            if self.state().remaining_wall_seconds<=0:self.finish('finished','wall_budget_exhausted');return self.store.row(self.run_id)
            if reply.action.tool=='finish':
                for stage in ('action_authorized','action_applicable','action_executed'):self.mark(stage)
                self.finish('finished','give_up');return self.store.row(self.run_id)
            result=self.operation(reply.action,call_id)
            if not result.ok:
                self.flush_funnel('candidate_rejected',result.error);self.finish('finished','candidate_rejected')
                return self.store.row(self.run_id)
            self.mark('action_executed');self.mark('checkpoint_created')
            self.selected=self.artifacts.checkpoint(self.workspace,self.selected.hash)
            self.store.update_run(self.run_id,selected_checkpoint=self.selected.hash)
            self.store.event(self.run_id,'supervisor','diagnostic_candidate_checkpoint',
                {'call_id':call_id,'checkpoint':self.selected.to_dict()})
            self.flush_funnel('candidate_changed')
            if self.cancelled():self.finish('stopped','manual_stop');return self.store.row(self.run_id)
            reason=self.exhausted()
            if reason:self.finish('finished',reason);return self.store.row(self.run_id)
            self.auto_verifying=True
            verify_id=str(uuid.uuid4())
            self.store.event(self.run_id,'control_plane','automatic_public_verification',{'call_id':verify_id,'source_model_call_id':call_id})
            verified=self.operation(ActionRequest('run_public_tests',{}),verify_id)
            self.auto_verifying=False
            outcome=verified.data['outcome']
            self.finish('stopped' if self.cancelled() else 'finished','manual_stop' if self.cancelled() else 'public_'+outcome)
        except KeyboardInterrupt:self.finish('stopped','keyboard_interrupt')
        except Exception as exc:
            self.store.event(self.run_id,'supervisor','execution_error',{'exception_type':type(exc).__name__,'message':str(exc)[:2048]})
            self.finish('interrupted','execution_error')
        return self.store.row(self.run_id)
