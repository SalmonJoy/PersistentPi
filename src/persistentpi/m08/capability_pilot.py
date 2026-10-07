"""Public development-only model capability control; historical E0 execution."""
from collections import Counter
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from ..adapters.ollama import HTTPClient, discover
from ..adapters.platform import hardware
from ..contracts import DecisionState, digest
from ..export import export
from ..telemetry import utc
from .acquisition_pilot import Ledger, PilotCeiling, PilotFreeze, events_for, git, save
from .analysis import COSTS
from .freeze import checksum
from .primitive_pilot import (PrimitiveCampaign, audit_campaign, implementation_paths as old_paths,
                             prior_audit as older_audit, window_record)
from .primitive_runtime import PrimitiveController, PrimitiveModel
from .tokenizer import FrozenTokenizer, metadata

HISTORY = '7c9c803c6acc84e62fd7a721498632478a625f9a'


def read(path):
    return json.loads(Path(path).read_bytes())


def host_metadata(root, client):
    value = {**hardware(),'utc':utc(),'disk_free_bytes':shutil.disk_usage(root).free,
             'seven_b_inference':False,'seven_b_feasibility':'not_load_or_performance_tested'}
    if os.name=='nt':
        class Memory(ctypes.Structure):
            _fields_ = [('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in
                ('total_physical','available_physical','total_page','available_page','total_virtual','available_virtual','extended')]
        memory = Memory();memory.length=ctypes.sizeof(memory)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
            value.update(ram_bytes=memory.total_physical,available_ram_bytes=memory.available_physical)
    tags = client.request('GET','/api/tags',timeout=5)['models']
    value['seven_b_locally_installed'] = any(m['name'].startswith('qwen2.5-coder:7b') for m in tags)
    value['loaded_models'] = client.request('GET','/api/ps',timeout=5)
    return value


def plan_for(root):
    baseline = read(Path(root)/'configs/m08-preregistered.json')
    config = read(Path(root)/'configs/m08e-preregistered.json')
    return {**baseline, 'model':{**baseline['model'], 'model':config['model'],
                               'expected_digest':config['expected_digest']}}


def historical(root):
    history = older_audit(root)
    folder = Path(root)/'docs/research-records/m08d'
    checks = read(folder/'checksums.json')
    for name, expected in checks.items():
        raw = subprocess.run(['git','-C',str(root),'show',HISTORY+':docs/research-records/m08d/'+name],
                             check=True,capture_output=True).stdout
        if checksum(folder/name)!=expected or hashlib.sha256(raw).hexdigest()!=expected:
            raise ValueError('M0.8D historical evidence changed: '+name)
    result = read(folder/'results.json')
    if not result['complete'] or result['analysis']['gate']['qualifies'] or result['analysis']['conditions']['A']['formations']!=7:
        raise ValueError('Historical E0 reference changed')
    if result['hidden_scores'] or result['evaluation_tasks_executed']:
        raise ValueError('Historical isolation failed')
    # Frozen old execution files must remain identical; only new isolated files are added.
    for name in read(folder/'freeze.json')['files']:
        raw = subprocess.run(['git','-C',str(root),'show',HISTORY+':'+name],check=True,capture_output=True).stdout
        if checksum(Path(root)/name)!=hashlib.sha256(raw).hexdigest():
            raise ValueError('Historical E0 implementation changed: '+name)
    history['M0.8D'] = {'commit':HISTORY,'checksums':checks,'E0_formations':7,'E1_formations':6,
                       'gate':False,'hidden_scores':0,'evaluation_runs':0}
    return history


def tokenizer_for(config, directory=None):
    if config['model']!='qwen2.5-coder:3b':
        raise ValueError('Only intended 3B tag permitted')
    directory = Path(directory or Path.home()/'.ollama/models')
    manifest = directory/'manifests/registry.ollama.ai/library/qwen2.5-coder/3b'
    if checksum(manifest)!=config['expected_digest']:
        raise ValueError('3B manifest identity mismatch')
    layer = next(x for x in read(manifest)['layers'] if x['mediaType']=='application/vnd.ollama.image.model')
    blob = directory/'blobs'/layer['digest'].replace(':','-')
    hasher = hashlib.sha256()
    with blob.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            hasher.update(block)
    if 'sha256:'+hasher.hexdigest()!=layer['digest']:
        raise ValueError('3B GGUF checksum mismatch')
    info = metadata(blob)
    return FrozenTokenizer(info,{'version':1,'model_digest':config['expected_digest'],
        'blob_digest':layer['digest'],'tokenizer_hash':digest({k:v for k,v in info.items() if k.startswith('tokenizer.')}),
        'pretokenizer':'qwen2-ascii-1','gguf_pre':info['tokenizer.ggml.pre']})


def implementation_paths(root):
    return sorted(set(old_paths(root)+[Path(root)/p for p in
        ('configs/m08e-preregistered.json','docs/m08e-preregistration.md','scripts/m08e.py')]))


class CapabilityFreeze(PilotFreeze):
    def validate(self):
        if checksum(self.path)!=self.hash or self.data['milestone']!='M0.8E':
            raise ValueError('Capability freeze changed')
        if set(self.data['files'])!={p.relative_to(self.root).as_posix() for p in implementation_paths(self.root)}:
            raise ValueError('Implementation file set changed')
        for name, expected in self.data['files'].items():
            actual = checksum(self.root/name)
            if self.historical_audit:
                actual = hashlib.sha256(subprocess.run(['git','-C',str(self.root),'show',self.commit+':'+name],
                                                      check=True,capture_output=True).stdout).hexdigest()
            if actual!=expected:
                raise ValueError('Frozen implementation changed: '+name)
        for name, expected in self.data['inputs'].items():
            if checksum(self.path.parent/name)!=expected:
                raise ValueError('Frozen public input changed: '+name)
        plan = plan_for(self.root)
        if digest(plan)!=self.data['preregistration_hash'] or digest(read(self.root/'configs/m08e-preregistered.json'))!=self.data['pilot_config_hash']:
            raise ValueError('Preregistration changed')
        return plan

    def tasks(self):
        tasks = super().tasks()
        original = read(self.root/'docs/research-records/m08d/manifest.json')
        if self.data['suite_manifest']!=original or read(self.path.parent/'tasks.json')!=read(self.root/'docs/research-records/m08d/tasks.json'):
            raise ValueError('Must reuse exact M0.8D development inputs')
        return tasks


class CapabilityCampaign(PrimitiveCampaign):
    def __init__(self, state, plan, tasks, ledger, **kwargs):
        super().__init__(state,plan,tasks,'A',ledger,**kwargs)
        self.manifest = {**self.manifest,'milestone':'M0.8E','reference_commit':HISTORY,
                         'comparison':'historical_non_concurrent_descriptive'}
        self.manifest['scaffold_hash'] = digest(self.manifest)
        self.manifest_hash = self.store.manifest('m08e_acquisition',self.manifest)
        with self.store.db:
            self.store.db.execute('UPDATE experiments SET manifest_hash=? WHERE id=?',(self.manifest_hash,self.id))


def record(campaign, task, run, state):
    result = window_record(campaign,task,run,state)
    es = events_for(campaign,run)
    result['diagnostics']['funnel']['act'] = any(e['type']=='control_action' and e['payload']['after']['phase']=='ACT' for e in es)
    return result


def analyze(rows, complete=True):
    conditions = {}
    for arm in ('reference','control'):
        records = [r[arm] for r in rows if r.get(arm)]
        n = sum(r['formed'] for r in records)
        edits = sum(r['diagnostics']['edit_proposals'] for r in records)
        noops = sum(r['diagnostics']['old_equals_new'] for r in records)
        counts = {'tasks':len(records)}
        stages = ('source_inspected','act','edit_generated','schema_valid_edit','authorized_edit','state_changing_edit','checkpoint','public_verification')
        for s in stages+('public_pass','public_fail'):
            # Historical ACT follows a successful READ under the unchanged C3 controller.
            counts[s] = sum(r['diagnostics']['funnel'].get(s,r['diagnostics']['funnel']['source_inspected'] if s=='act' else False) for r in records)
        order = ('tasks',)+stages
        rates = {a+' -> '+b:counts[b]/counts[a] if counts[a] else None for a,b in zip(order,order[1:])}
        rates.update({'public_verification -> '+s:counts[s]/counts['public_verification'] if counts['public_verification'] else None for s in ('public_pass','public_fail')})
        cost = {k:sum(r['cost'].get(k,0) for r in records) for k in COSTS}
        conditions[arm] = {'windows':len(records),'formations':n,'formation_rate':n/16,
            'families':dict(Counter(r['family'] for r in rows if r.get(arm) and r[arm]['formed'])),
            'public':dict(Counter(r['public'] for r in records if r['formed'])),
            'funnel':{'counts':counts,'conversion_rates':rates},'edit_proposals':edits,'noops':noops,
            'unchanged_edit_fraction':noops/edits if edits else None,
            'repeated_proposals':sum(r['diagnostics']['repeated_proposals'] for r in records),
            'rejections':dict(sum((Counter(r['diagnostics']['rejection_reasons']) for r in records),Counter())),
            'terminations':dict(Counter(r['termination'] for r in records)),
            'cost':cost,'cost_per_formation':{k:v/n if n else None for k,v in cost.items()},
            'first_change_decisions':[r['diagnostics']['decisions_to_first_changed_edit'] for r in records],
            'first_change_tokens':[r['diagnostics']['tokens_to_first_changed_edit'] for r in records]}
    ref,control = conditions['reference'],conditions['control']
    difference = control['formations']-ref['formations']
    strong = complete and control['windows']==16 and control['formations']>=13 and difference>=4 and len(control['families'])>=6
    paired = Counter('control_only' if r['control']['formed'] and not r['reference']['formed'] else
        'reference_only' if r['reference']['formed'] and not r['control']['formed'] else
        'both' if r['reference']['formed'] else 'neither' for r in rows if r.get('control'))
    return {'conditions':conditions,'net_formations':difference,'paired':dict(paired),'strong_signal':strong,
            'interpretation':'incomplete' if not complete else 'strong' if strong else 'intermediate' if difference>0 else 'no_improvement'}


def prepare(root, destination):
    root,destination = Path(root).resolve(),Path(destination).resolve()
    if destination.exists() or git(root,'status','--porcelain'):
        raise ValueError('Clean committed implementation/new output required')
    history = historical(root)
    if git(root,'cat-file','-t','m0.8d')!='tag' or git(root,'rev-parse','m0.8d^{}')!=HISTORY:
        raise ValueError('Annotated M0.8D tag mismatch')
    folder = root/'docs/research-records/m08d'
    plan,config = plan_for(root),read(root/'configs/m08e-preregistered.json')
    identity,tokenizer = discover(plan['model']),tokenizer_for(plan['model'])
    baseline = read(folder/'model.json')
    if discover(read(root/'configs/m08-preregistered.json')['model'])!=baseline['identity']:
        raise ValueError('Historical runtime/model reference identity changed')
    for key in ('template_hash','system_hash'):
        if identity[key]!=baseline['identity'][key]:
            raise ValueError('Model serialization differs: '+key)
    if tokenizer.identity['tokenizer_hash']!=baseline['tokenizer']['tokenizer_hash']:
        raise ValueError('Tokenizer/context policy differs')
    manifest = read(folder/'manifest.json')
    inputs = {'history.json':history,'manifest.json':manifest,'tasks.json':read(folder/'tasks.json'),
              'configs.json':{'plan':plan,'pilot':config},'model.json':{'identity':identity,'tokenizer':tokenizer.identity},
              'reference.json':read(folder/'results.json')}
    client = HTTPClient(plan['model']['endpoint'])
    inputs['show.json'] = client.request('POST','/api/show',{'model':plan['model']['model']},timeout=5)
    inputs['host.json'] = host_metadata(root,client)
    order = [{'ordinal':i+1,'task_id':r['task_id'],'task_hash':r['hash'],'template':r['template'],'family':r['family']}
             for i,r in enumerate(sorted(inputs['tasks.json'].values(),key=lambda r:r['template']))]
    inputs['schedule.json'] = {'entries':order,'hash':digest(order)}
    inputs['initial-prompts.json'] = read(folder/'initial-prompts.json')
    for name,value in inputs.items():
        save(destination/name,value)
    data = {'milestone':'M0.8E','version':1,'created_utc':utc(),'implementation_commit':git(root,'rev-parse','HEAD'),
        'preregistration_hash':digest(plan),'pilot_config_hash':digest(config),'suite_manifest':manifest,
        'suite_manifest_hash':digest(manifest),'schedule_hash':digest(order),'model':identity,
        'tokenizer_identity':tokenizer.identity,'files':{p.relative_to(root).as_posix():checksum(p) for p in implementation_paths(root)},
        'inputs':{name:checksum(destination/name) for name in inputs},'live_inference_calls':0}
    save(destination/'freeze.json',data)
    lock = CapabilityFreeze(destination/'freeze.json',root,checksum(destination/'freeze.json'))
    for task in lock.tasks():
        model = PrimitiveModel(plan['model'],identity,PrimitiveController(task.view.editable_paths,'E0'),'detailed',tokenizer)
        messages,meta = model.prompt(task.view,(),DecisionState(1,14,15,16000,120))
        if digest(messages)!=inputs['initial-prompts.json'][task.task_id]['A']['hash']:
            raise ValueError('Historical E0 prompt changed')
    return {'sha256':lock.hash,'implementation_commit':lock.commit,'manifest_hash':data['suite_manifest_hash']}


def execute(root, lock, destination):
    root,destination = Path(root).resolve(),Path(destination).resolve()
    if lock.historical_audit or destination.exists() or git(root,'status','--porcelain') or git(root,'rev-parse','HEAD')!=lock.commit:
        raise ValueError('Clean live freeze/new state required')
    plan,tasks = lock.validate(),lock.tasks()
    history = historical(root)
    identity,tokenizer = discover(plan['model']),tokenizer_for(plan['model'])
    if identity!=lock.data['model'] or tokenizer.identity!=lock.data['tokenizer_identity']:
        raise ValueError('Live identity differs from freeze')
    config = read(root/'configs/m08e-preregistered.json')
    ledger = Ledger(config['ceilings'])
    order = read(lock.path.parent/'schedule.json')
    expected = [{'ordinal':i+1,'task_id':t.task_id,'task_hash':t.hash,'template':t.template,'family':t.family} for i,t in enumerate(tasks)]
    if order!={'entries':expected,'hash':digest(expected)}:
        raise ValueError('Frozen ordering changed')
    references = {r['task_id']:r for r in read(lock.path.parent/'reference.json')['rows']}
    rows = [{'task_id':t.task_id,'family':t.family,'template':t.template,'reference':references[t.task_id]['A'],'control':None} for t in tasks]
    destination.mkdir(parents=True)
    c = CapabilityCampaign(destination/'control',plan,tasks,ledger,identity=identity,tokenizer=tokenizer,
                           freeze=lock,frozen_schedule=order['hash'])
    completed,interruption,error = [],None,None
    try:
        for entry,task,row in zip(order['entries'],tasks,rows):
            if (destination/'STOP').exists():
                raise PilotCeiling('Manual STOP')
            ledger.check()
            print(json.dumps({'event':'window_start',**entry}),flush=True)
            run,original,state,artifact = c.acquire(task)
            row['control'] = record(c,task,run,state)
            completed.append({**entry,'run_id':run,'state_artifact':artifact})
            save(destination/f"window-{entry['ordinal']:02}.json",completed[-1])
            print(json.dumps({'event':'window_done','ordinal':entry['ordinal'],'formed':row['control']['formed'],
                              'public':row['control']['public'],'termination':state['stop_reason']}),flush=True)
    except (Exception,KeyboardInterrupt) as exc:
        interruption,error = type(exc).__name__,str(exc)
    finally:
        try:
            task_map = {t.task_id:t for t in tasks}
            for window in c.store.db.execute('SELECT * FROM m08_windows'):
                row = next(r for r in rows if r['task_id']==window['task_id'])
                if window['state_artifact'] and row['control'] is None:
                    row['control'] = record(c,task_map[window['task_id']],window['run_id'],read_artifact(c,window['state_artifact']))
            complete = interruption is None and len(completed)==16
            try:
                audit = audit_campaign(c,task_map,complete)
            except Exception as exc:
                audit = {'passed':False,'error':str(exc)}
                complete,interruption = False,interruption or 'audit_failed'
            c.overhead('shared_control_plane',max(0,ledger.clock()-ledger.started-ledger.cost()['wall_seconds']))
            with c.store.db:
                c.store.db.execute('UPDATE m08_campaigns SET state=?,sealed_utc=? WHERE id=?',('sealed' if complete else 'incomplete',utc(),c.id))
            archive = export(c,destination/'control-research.zip')
            final_identity = discover(plan['model'])
            if identity!=final_identity:
                complete,interruption = False,'post_identity_changed'
            cost = ledger.cost()
            if cost['tokens']>256000 or cost['model_decisions']>240 or ledger.elapsed()>2400:
                complete,interruption = False,'campaign_ceiling_violated'
            lock.validate()
            result = {'milestone':'M0.8E','complete':complete,'interruption':interruption,'error':error,
                'implementation_commit':lock.commit,'freeze_hash':lock.hash,'manifest_hash':lock.data['suite_manifest_hash'],
                'schedule_hash':order['hash'],'schedule_executed':completed,'rows':rows,'analysis':analyze(rows,complete),
                'model_identity':identity,'post_generation_identity':final_identity,'physical_cost':cost,
                'execution_elapsed_seconds':ledger.elapsed(),'audit':audit,'export':archive,'history':historical(root),
                'evaluation_tasks_executed':0,'hidden_scores':0,'baseline_windows_executed':0,
                'comparison':'historical_non_concurrent_descriptive'}
            save(destination/'results.json',result)
            return result
        finally:
            c.close()


def read_artifact(campaign, key):
    return json.loads(campaign.artifacts.get(key))
