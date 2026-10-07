"""M0.8D development-only edit-primitive acquisition experiment."""
from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import time
import zipfile

from ..adapters.ollama import discover
from ..artifacts import atomic_write
from ..contracts import Budget, DecisionState, TaskView, canonical, digest
from ..export import export
from ..interfaces import action_schema, authorize_interface
from ..runner import Runner
from ..telemetry import utc
from .acquisition_analysis import analyze as original_analysis, diagnostics as original_diagnostics
from .acquisition_pilot import (DevelopmentTask, LEGACY, Ledger, PilotCampaign, PilotCeiling,
                                PilotFreeze, events_for, git, history_audit, save, schedule)
from .freeze import checksum, freeze_paths
from .primitive_runtime import PrimitiveController, PrimitiveModel, PrimitiveWindow, project, restore
from .runtime import CaseVerifier, Window, observation_from
from .tokenizer import FrozenTokenizer

PREVIOUS = 'cb08346991784a381d5363cb50198e6f4b31722b'
PRIMITIVES = {'A':'E0', 'B':'E1'}
TOOLS = {'A':'edit_file', 'B':'replace_file'}


def prior_audit(root):
    result = {'M0.8B': history_audit(root)}
    folder = Path(root)/'docs/research-records/m08c'
    checks = json.loads((folder/'checksums.json').read_bytes())
    for name, expected in checks.items():
        if checksum(folder/name) != expected:
            raise ValueError('M0.8C archive changed: '+name)
        raw = subprocess.run(['git', '-C', str(root), 'show', PREVIOUS+':docs/research-records/m08c/'+name],
                             check=True, capture_output=True).stdout
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('M0.8C differs from evidence commit: '+name)
    observed = json.loads((folder/'results.json').read_bytes())
    if observed['analysis']['gate']['qualifies'] or observed['analysis']['gate']['A_formations'] != 7 or observed['analysis']['gate']['B_formations'] != 6:
        raise ValueError('M0.8C preserved outcome mismatch')
    for arm in PRIMITIVES:
        with sqlite3.connect((folder/(arm+'.sqlite')).resolve().as_uri()+'?mode=ro&immutable=1', uri=True) as db:
            if db.execute("SELECT COUNT(*) FROM runs WHERE mode!='development'").fetchone()[0] or db.execute(
                    "SELECT COUNT(*) FROM evaluations WHERE split!='public'").fetchone()[0] or db.execute(
                    'SELECT COUNT(*) FROM m08_scores').fetchone()[0]:
                raise ValueError('Prior evaluation/hidden execution')
    result['M0.8C'] = {'commit':PREVIOUS, 'checksums':checks, 'formations':{'A':7,'B':6}, 'gate':False,
                       'evaluation_runs':0, 'hidden_scores':0}
    return result


def selection(metadata, previously_selected):
    pool = [r for r in metadata if r['tier'] == 'L2']
    groups = {}
    for row in pool:
        groups.setdefault(row['template'], []).append(row)
    old = set(previously_selected)
    if len(pool)!=32 or len(groups)!=16 or len(old)!=16 or not old <= {r['task_id'] for r in pool}:
        raise ValueError('Require the complete paired L2 development metadata')
    chosen = []
    for template in sorted(groups):
        pair = groups[template]
        fresh = [r for r in pair if r['task_id'] not in old]
        if len(pair)!=2 or len(fresh)!=1:
            raise ValueError('Require exactly the other instance per development template')
        chosen.extend(fresh)
    if len({r['family'] for r in chosen})!=8:
        raise ValueError('Eight development families required')
    return chosen


def public_inputs(root):
    folder = Path(root)/'docs/research-records/m08b'
    metadata = json.loads((folder/'difficulty.json').read_bytes())['per_task']
    old = json.loads((Path(root)/'docs/research-records/m08c/manifest.json').read_bytes())['task_hashes']
    selected = selection(metadata, old)
    tasks, provenance = [], []
    with sqlite3.connect((folder/'raw/experiments.sqlite').resolve().as_uri()+'?mode=ro&immutable=1', uri=True) as db, \
            zipfile.ZipFile(folder/'raw/research.zip') as archive:
        db.row_factory = sqlite3.Row
        def blob(key):
            row = db.execute('SELECT kind,visibility FROM artifacts WHERE hash=?', (key,)).fetchone()
            if not row or row['visibility']!='public' or row['kind'] not in ('checkpoint','workspace_file','model_request'):
                raise ValueError('Only whitelisted historical development public inputs permitted')
            raw = archive.read('artifacts/'+key)
            if hashlib.sha256(raw).hexdigest()!=key:
                raise ValueError('Public input hash mismatch')
            return raw
        for meta in selected:
            runs = list(db.execute("SELECT * FROM runs WHERE task_id=? AND mode='development'", (meta['task_id'],)))
            if len(runs)!=1:
                raise ValueError('Ambiguous development provenance')
            run = runs[0]
            checkpoint = json.loads(blob(run['initial_checkpoint']))
            if set(checkpoint['files'])!={'src/solution.py','public_tests/cases.json'}:
                raise ValueError('Undeclared initial public workspace')
            source = blob(checkpoint['files']['src/solution.py']).decode()
            cases = tuple(json.loads(blob(checkpoint['files']['public_tests/cases.json'])))
            req = db.execute("SELECT payload_json FROM events WHERE run_id=? AND type='model_request' ORDER BY sequence LIMIT 1", (run['id'],)).fetchone()
            key = json.loads(req[0])['request_artifact']
            data = json.loads(json.loads(blob(key))['payload']['messages'][1]['content'])['task']
            data.pop('contract_version', None)
            data['editable_paths'], data['readable_paths'] = tuple(data['editable_paths']), tuple(data['readable_paths'])
            view = TaskView(**data)
            if view.task_id!=meta['task_id'] or len(cases)!=8:
                raise ValueError('Public development identity mismatch')
            tasks.append(DevelopmentTask(meta['task_id'], run['task_hash'], meta['family'], meta['template'],
                                         source, cases, view, run['initial_checkpoint']))
            provenance.append({'task_id':meta['task_id'], 'source_run':run['id'], 'checkpoint':run['initial_checkpoint'],
                               'taskview_request':key, 'files':checkpoint['files']})
    return tasks, provenance


def implementation_paths(root):
    return sorted(set(freeze_paths(root)+[Path(root)/p for p in
        ('configs/m08c-preregistered.json','docs/m08c-preregistration.md','scripts/m08c.py',
         'configs/m08d-preregistered.json','docs/m08d-preregistration.md','scripts/m08d.py')]))


class PrimitiveFreeze(PilotFreeze):
    def validate(self):
        if checksum(self.path)!=self.hash or self.data['milestone']!='M0.8D':
            raise ValueError('Primitive freeze changed')
        if not self.historical_audit and set(self.data['files'])!={p.relative_to(self.root).as_posix() for p in implementation_paths(self.root)}:
            raise ValueError('Implementation file set changed')
        for name, expected in self.data['files'].items():
            if self.historical_audit:
                raw = subprocess.run(['git','-C',str(self.root),'show',self.commit+':'+name], check=True, capture_output=True).stdout
                actual = hashlib.sha256(raw).hexdigest()
            else:
                actual = checksum(self.root/name)
            if actual!=expected:
                raise ValueError('Frozen implementation changed: '+name)
        for name, expected in self.data['inputs'].items():
            if checksum(self.path.parent/name)!=expected:
                raise ValueError('Frozen input changed: '+name)
        plan = json.loads((self.root/'configs/m08-preregistered.json').read_bytes())
        if digest(plan)!=self.data['preregistration_hash'] or digest(json.loads(
                (self.root/'configs/m08d-preregistered.json').read_bytes()))!=self.data['pilot_config_hash']:
            raise ValueError('Window or pilot configuration changed')
        return plan

    def tasks(self):
        tasks = super().tasks()
        old = json.loads((self.root/'docs/research-records/m08c/manifest.json').read_bytes())['task_hashes']
        if set(old) & {t.task_id for t in tasks}:
            raise ValueError('Previously M0.8C-exposed instance prohibited')
        return tasks


def prepare(root, destination):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    if destination.exists() or git(root, 'status', '--porcelain'):
        raise ValueError('Freeze requires clean code commit and new output')
    history = prior_audit(root)
    for name in json.loads((root/'docs/research-records/m08c/freeze.json').read_bytes())['files']:
        raw = subprocess.run(['git','-C',str(root),'show',PREVIOUS+':'+name], check=True, capture_output=True).stdout
        expected = hashlib.sha256(raw).hexdigest()
        if checksum(root/name)!=expected:
            raise ValueError('Historical acquisition implementation changed: '+name)
    if git(root,'cat-file','-t','m0.8c')!='tag' or git(root,'rev-parse','m0.8c^{}')!=PREVIOUS:
        raise ValueError('Annotated M0.8C tag mismatch')
    tasks, provenance = public_inputs(root)
    plan = json.loads((root/'configs/m08-preregistered.json').read_bytes())
    config = json.loads((root/'configs/m08d-preregistered.json').read_bytes())
    identity, tokenizer = discover(plan['model']), FrozenTokenizer.installed(plan['model'])
    previous = json.loads((root/'docs/research-records/m08c/model.json').read_bytes())
    if identity!=previous['identity'] or tokenizer.identity!=previous['tokenizer']:
        raise ValueError('Runner or tokenizer changed since M0.8C')
    serialized = {t.task_id:json.loads(canonical(t)) for t in tasks}
    manifest = {'version':1, 'tier':'L2', 'split':'development', 'selection':config['selection'],
                'freshness':'not_exposed_to_M0.8C; already_M0.8B_calibrated',
                'task_hashes':{t.task_id:t.hash for t in tasks},
                'public_input_hashes':{key:digest(value) for key,value in serialized.items()}, 'provenance':provenance}
    frozen_schedule = schedule(tasks)
    configs = {a:{**plan,'model':{**plan['model'],'edit_primitive':PRIMITIVES[a]}} for a in PRIMITIVES}
    prompts = {}
    for task in tasks:
        prompts[task.task_id] = {}
        for arm in PRIMITIVES:
            model = PrimitiveModel(configs[arm]['model'], identity, PrimitiveController(task.view.editable_paths, PRIMITIVES[arm]),
                                   'detailed', tokenizer)
            messages, metadata = model.prompt(task.view, (), DecisionState(1,14,15,16000,120))
            prompts[task.task_id][arm] = {'hash':digest(messages), 'metadata':metadata,
                                        'prompt_token_upper_bound':tokenizer.prompt_upper_bound(messages),
                                        'system_hash':digest(messages[0]), 'messages':messages}
    inputs = {'history.json':history, 'tasks.json':serialized, 'manifest.json':manifest,
              'schedule.json':frozen_schedule, 'configs.json':{**configs,'pilot':config},
              'model.json':{'identity':identity,'tokenizer':tokenizer.identity},
              'initial-prompts.json':prompts,
              'contracts.json':{'A':action_schema('E0'),'B':action_schema('E1'),
                                'identities':{'A':'E0-old-new-1','B':'E1-replace-file-1'},
                                'common_noop_feedback':LEGACY,
                                'projection':{'Replacement is unchanged':LEGACY,'Replacement file size limit exceeded':LEGACY}}}
    for name, value in inputs.items():
        save(destination/name, value)
    data = {'milestone':'M0.8D', 'version':1, 'created_utc':utc(), 'implementation_commit':git(root,'rev-parse','HEAD'),
            'preregistration_hash':digest(plan), 'pilot_config_hash':digest(config),
            'suite_manifest':manifest, 'suite_manifest_hash':digest(manifest), 'schedule_hash':frozen_schedule['hash'],
            'model':identity, 'tokenizer_identity':tokenizer.identity,
            'files':{p.relative_to(root).as_posix():checksum(p) for p in implementation_paths(root)},
            'inputs':{name:checksum(destination/name) for name in inputs}, 'live_inference_calls':0}
    save(destination/'freeze.json', data)
    return {'sha256':checksum(destination/'freeze.json'), 'manifest_hash':digest(manifest),
            'schedule_hash':frozen_schedule['hash'], 'commit':data['implementation_commit']}


class PrimitiveCampaign(PilotCampaign):
    def __init__(self, state, plan, tasks, condition, ledger, **kwargs):
        super().__init__(state, plan, tasks, condition, ledger, **kwargs)
        self.model_config = {**plan['model'], 'edit_primitive':PRIMITIVES[condition]}
        self.manifest = {**self.manifest,'milestone':'M0.8D', 'model':self.model_config,
                         'interface':{'output_protocol':plan['model']['output_protocol'],'edit_primitive':PRIMITIVES[condition]},
                         'rejection_feedback':LEGACY, 'primitive_identity':PRIMITIVES[condition]+'-1'}
        self.manifest['scaffold_hash'] = digest(self.manifest)
        self.manifest_hash = self.store.manifest('m08d_acquisition', self.manifest)
        with self.store.db:
            self.store.db.execute('UPDATE experiments SET manifest_hash=? WHERE id=?', (self.manifest_hash,self.id))
        if kwargs.get('model_factory') is None:
            self.model_factory = lambda task,arm,index,controller,mode: PrimitiveModel(
                self.model_config, self.identity, controller, 'detailed', self.tokenizer)

    def acquire(self, task, arm='I', index=1, prefix=None, previous=None):
        began = time.monotonic()
        if arm!='I' or index!=1 or prefix is not None or previous is not None:
            raise ValueError('M0.8D prohibits continuation')
        if task.split!='development' or task.tier!='L2' or task.task_id not in self.tasks or self.tasks[task.task_id].hash!=task.hash:
            raise ValueError('M0.8D prohibits evaluation/foreign tasks')
        if sum(c.store.db.execute('SELECT COUNT(*) FROM m08_windows').fetchone()[0] for c in self.ledger.campaigns)>=self.ledger.limits['windows']:
            raise PilotCeiling('Pilot window ceiling')
        if self.store.db.execute('SELECT state FROM m08_campaigns WHERE id=?',(self.id,)).fetchone()[0]!='running':
            raise ValueError('No resume after sealing/interruption')
        if self.store.db.execute('SELECT 1 FROM m08_windows WHERE campaign_id=? AND task_id=?',(self.id,task.task_id)).fetchone():
            raise ValueError('No repeated task acquisition in an arm')
        if self.freeze:
            self.freeze.validate()
        self.check_limits()
        run,budget = self.new_run(task,arm,index)
        workspace = self.store.state/'workspaces'/run
        workspace.mkdir(parents=True)
        atomic_write(workspace/'src/solution.py',task.mutant.encode())
        atomic_write(workspace/'public_tests/cases.json',canonical(task.public))
        primitive = PRIMITIVES[self.condition]
        controller = PrimitiveController(task.view.editable_paths, primitive)
        initial = self.artifacts.checkpoint(workspace)
        if initial.hash!=task.original_checkpoint:
            raise ValueError('Original public workspace does not match historical checkpoint')
        self.store.update_run(run,initial_checkpoint=initial.hash,selected_checkpoint=initial.hash)
        self.store.event(run,'control_plane','initial_checkpoint',{'checkpoint':initial.to_dict()})
        verifier = CaseVerifier(self.artifacts,run,task.public,task.view.public_test_id)
        self.overhead('window_preparation',time.monotonic()-began,run)
        window_type = Window if primitive=='E0' else PrimitiveWindow
        window = window_type(self.store,self.artifacts,run,workspace,task.view,budget,verifier,
                             controller=controller,campaign=self,candidate_index=1)
        window.edit_tool = TOOLS[self.condition]
        model = self.model_factory(task,arm,index,controller,'detailed')
        state, artifact = window.run(Runner(model))
        if state['status']!='finished':
            with self.store.db:
                self.store.db.execute("UPDATE m08_campaigns SET state='incomplete' WHERE id=?",(self.id,))
            raise RuntimeError('Campaign interrupted; no automatic retry: '+state['stop_reason'])
        return run,initial.hash,state,artifact


def diagnostics(events, original, primitive):
    source, proposals, reads, repeated, seen = original, [], 0, 0, set()
    remapped = []
    stages = {name:False for name in ('source_inspected','edit_generated','schema_valid_edit','authorized_edit',
                                     'state_changing_edit','checkpoint','public_verification','public_pass','public_fail')}
    for event in events:
        kind, payload = event['type'], event['payload']
        value = event
        if kind=='action_completed':
            action, result = payload['action'], payload['result']
            args = action['arguments']
            if action['tool']=='read_file' and result['ok'] and not result['data'].get('truncated'):
                stages['source_inspected'] = True
                reads += 1
            if action['tool'] in ('edit_file','replace_file'):
                valid = True
                try:
                    from ..contracts import ActionRequest
                    authorize_interface(ActionRequest.from_dict(action), primitive)
                except (ValueError,TypeError):
                    valid = False
                stages['edit_generated'] = True
                stages['schema_valid_edit'] |= valid
                stages['authorized_edit'] |= valid and args.get('path')=='src/solution.py'
                noop = (args.get('old')==args.get('new') if primitive=='E0' else args.get('content')==source)
                key = digest(action)
                repeated += key in seen
                seen.add(key)
                proposals.append({'call_id':payload['call_id'],'hash':key,'noop':noop,'accepted':result['ok'],'error':result['error']})
                if primitive=='E1':
                    new_action = {**action,'tool':'edit_file','arguments':{'path':args.get('path'),'old':source,'new':args.get('content')}}
                    value = {'type':kind,'payload':{**payload,'action':new_action}}
                if result['ok']:
                    after = source.replace(args['old'],args['new'],1) if primitive=='E0' else args['content']
                    stages['state_changing_edit'] |= after!=source
                    source = after
        elif kind=='decision_completed' and primitive=='E1' and payload['action']['tool']=='replace_file':
            action = payload['action']
            value = {'type':kind,'payload':{**payload,'action':{**action,'tool':'edit_file',
                     'arguments':{'path':action['arguments'].get('path'),'old':source,'new':action['arguments'].get('content')}}}}
        elif kind=='candidate_checkpoint':
            stages['checkpoint'] = True
        elif kind=='automatic_public_verification':
            stages['public_verification'] = True
        elif kind=='candidate_completed':
            stages['public_pass'], stages['public_fail'] = payload['outcome']=='pass',payload['outcome']=='fail'
        remapped.append(value)
    result = original_diagnostics(remapped, original)
    return {**result,'funnel':stages, 'reads':reads,'edit_proposals':len(proposals),
            'repeated_proposals':repeated,'unique_proposals':len(seen),
            'rejection_reasons':dict(Counter(p['error'] for p in proposals if not p['accepted'])),
            'old_equals_new' if primitive=='E0' else 'replacement_equals_current':sum(p['noop'] for p in proposals),
            'proposals':proposals}


def window_record(campaign, task, run, state):
    candidate,usage = state['candidate'],state['usage']
    return {'run_id':run,'condition':campaign.condition,
            'formed':candidate is not None and candidate['outcome'] in ('pass','fail') and state['status']=='finished',
            'candidate_checkpoint':candidate['checkpoint'] if candidate else None,
            'public_verification_reached':candidate is not None,'public':candidate['outcome'] if candidate else None,
            'status':state['status'],'termination':state['stop_reason'],
            'cost':{**usage,'tokens':usage['input_tokens']+usage['output_tokens'],'candidates':usage['candidate_attempts']},
            'original_checkpoint':campaign.store.row(run)['initial_checkpoint'],
            'diagnostics':diagnostics(events_for(campaign,run),task.mutant,PRIMITIVES[campaign.condition])}


def analyze(rows, config, complete=True):
    result = original_analysis(rows,config,complete)
    result['paired'] = {k:result['paired'].get(k,0) for k in ('B_win','A_win','both_formed','neither_formed')}
    for arm in PRIMITIVES:
        records = [r[arm] for r in rows if r.get(arm)]
        c = result['conditions'][arm]
        stages = ['tasks','source_inspected','edit_generated','schema_valid_edit','authorized_edit',
                  'state_changing_edit','checkpoint','public_verification']
        counts = {'tasks':len(records), **{s:sum(r['diagnostics']['funnel'][s] for r in records) for s in stages[1:]+['public_pass','public_fail']}}
        rates = {a+' -> '+b:counts[b]/counts[a] if counts[a] else None for a,b in zip(stages,stages[1:])}
        rates.update({'public_verification -> '+b:counts[b]/counts['public_verification'] if counts['public_verification'] else None for b in ('public_pass','public_fail')})
        edits = sum(r['diagnostics']['edit_proposals'] for r in records)
        c.update(funnel={'counts':counts,'conversion_rates':rates},edit_proposals=edits,
                 changed_edit_rate=counts['state_changing_edit']/16,noop_edit_rate=c['noops']/edits if edits else None,
                 repeated_proposals=sum(r['diagnostics']['repeated_proposals'] for r in records),
                 unique_proposals=sum(r['diagnostics']['unique_proposals'] for r in records),
                 rejection_reasons=dict(sum((Counter(r['diagnostics']['rejection_reasons']) for r in records),Counter())))
    return result


def audit_campaign(campaign, tasks, complete):
    db = campaign.store.db
    if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or list(db.execute('PRAGMA foreign_key_check')):
        raise ValueError('Database integrity failed')
    for sql in ("SELECT COUNT(*) FROM evaluations WHERE split!='public'", "SELECT COUNT(*) FROM runs WHERE mode!='development'",
                'SELECT COUNT(*) FROM m08_scores','SELECT COUNT(*) FROM m08_retired_cohorts','SELECT COUNT(*) FROM m08_branches'):
        if db.execute(sql).fetchone()[0]:
            raise ValueError('Evaluation/hidden/repair isolation failed')
    request_count, projections = 0, 0
    primitive = PRIMITIVES[campaign.condition]
    for row in db.execute('SELECT * FROM runs ORDER BY created_utc'):
        task = tasks[row['task_id']]
        if row['task_hash']!=task.hash or row['initial_checkpoint']!=task.original_checkpoint or json.loads(row['budget_json'])!=Budget(**campaign.plan['window']).to_dict():
            raise ValueError('Task/checkpoint/budget mismatch')
        observations, calls, tokens, tools = [], 0, 0, 0
        controller = PrimitiveController(task.view.editable_paths,primitive)
        model = PrimitiveModel(campaign.model_config,campaign.identity,controller,'detailed',campaign.tokenizer)
        events = events_for(campaign,row['id'])
        for event in events:
            kind,p = event['type'],event['payload']
            if kind=='decision_started':
                calls += 1
            elif kind=='model_request':
                raw = json.loads(campaign.artifacts.get(p['request_artifact']))
                messages,metadata = model.prompt(task.view,tuple(observations),DecisionState(1,15-calls,15-tools,16000-tokens,120))
                expected = {'model':campaign.plan['model']['model'],'messages':messages,'stream':False,
                            'format':model.response_format('runner-json-schema-1',primitive),
                            'options':{'temperature':0,'seed':42,'num_ctx':4096,'num_predict':512},'keep_alive':'5m','think':False}
                if raw['payload']!=expected or raw['context']!=metadata:
                    raise ValueError('Request/schema/projection/budget replay mismatch')
                request_count += 1
                projections += sum(project(o)!=o for o in observations[-4:])
            elif kind=='model_call_completed':
                t = p['telemetry']
                if t['identity']!=campaign.identity or t['observed_digest']!=campaign.identity['digest'] or t['observed_runtime_version']!=campaign.identity['runtime_version'] or t['edit_primitive']!=primitive:
                    raise ValueError('Model or primitive changed')
                tokens += t['prompt_eval_count']+t['eval_count']
            elif kind=='control_action':
                controller = restore(p['after'],primitive)
                model.controller = controller
            elif kind=='action_completed':
                tools += 1
                if p['action']['tool'] not in ('read_file',TOOLS[campaign.condition]):
                    raise ValueError('Foreign primitive/action executed')
                observations.append(observation_from({'step':calls,'action':p['action'],'result':p['result']}))
        usage = json.loads(row['usage_json'])
        cost = campaign.physical_cost({row['id']},include_overhead=False)
        for name,value in [('model_decisions',calls),('tokens',tokens),('tool_calls',tools+usage['candidate_attempts'])]:
            expected = usage['input_tokens']+usage['output_tokens'] if name=='tokens' else usage[name]
            if value!=expected or value!=cost[name]:
                raise ValueError('Cost receipt mismatch: '+name)
        candidates = sum(e['type']=='candidate_completed' for e in events)
        if candidates!=usage['candidate_attempts'] or candidates>1 or candidates!=sum(e['type']=='automatic_public_verification' for e in events):
            raise ValueError('Single automatic verification invariant failed')
        if usage['model_decisions']>15 or usage['tool_calls']>15 or tokens>16000 or usage['wall_seconds']>120:
            raise ValueError('Window ceiling violated')
    return {'passed':True,'requests_replayed':request_count,'generic_projection_fields':projections,
            'hidden_scores':0,'evaluation_runs':0,'repair_windows':0,'complete':complete}


def execute_pilot(root, lock, destination):
    root,destination = Path(root).resolve(),Path(destination).resolve()
    if lock.historical_audit:
        raise ValueError('Historical audit cannot authorize inference')
    plan,tasks = lock.validate(),lock.tasks()
    order = json.loads((lock.path.parent/'schedule.json').read_bytes())
    if order!=schedule(tasks) or destination.exists() or git(root,'status','--porcelain') or git(root,'rev-parse','HEAD')!=lock.commit:
        raise ValueError('Clean frozen code/new state/schedule required')
    prior_audit(root)
    identity,tokenizer = discover(plan['model']),FrozenTokenizer.installed(plan['model'])
    if identity!=lock.data['model'] or tokenizer.identity!=lock.data['tokenizer_identity']:
        raise ValueError('Model/tokenizer mismatch')
    config = json.loads((root/'configs/m08d-preregistered.json').read_bytes())
    destination.mkdir(parents=True)
    save(destination/'started.json',{'utc':utc(),'freeze_hash':lock.hash,'implementation_commit':lock.commit,'schedule_hash':order['hash']})
    ledger,campaigns = Ledger(config['ceilings']),{}
    rows = {t.task_id:{'task_id':t.task_id,'family':t.family,'template':t.template,'A':None,'B':None} for t in tasks}
    task_map = {t.task_id:t for t in tasks}
    completed,interruption,error = [],None,None
    try:
        for arm in PRIMITIVES:
            campaigns[arm] = PrimitiveCampaign(destination/arm,plan,tasks,arm,ledger,tokenizer=tokenizer,identity=identity,
                                               freeze=lock,frozen_schedule=order['hash'])
        for entry in order['entries']:
            if (destination/'STOP').exists():
                raise PilotCeiling('Manual pilot STOP')
            ledger.check()
            campaign,task = campaigns[entry['condition']],task_map[entry['task_id']]
            print(json.dumps({'event':'window_start',**entry}),flush=True)
            run,original,state,artifact = campaign.acquire(task)
            if original!=task.original_checkpoint:
                raise ValueError('Original checkpoint differs from public input')
            rows[task.task_id][entry['condition']] = window_record(campaign,task,run,state)
            completed.append({**entry,'run_id':run,'state_artifact':artifact})
            save(destination/f"window-{entry['ordinal']:02}.json",completed[-1])
            print(json.dumps({'event':'window_done','ordinal':entry['ordinal'],'condition':entry['condition'],
                              'task_id':task.task_id,'formed':state['candidate'] is not None,'termination':state['stop_reason'],
                              'tokens':state['usage']['input_tokens']+state['usage']['output_tokens']}),flush=True)
    except (Exception,KeyboardInterrupt) as exc:
        interruption,error = type(exc).__name__,str(exc)
    finally:
        for arm,campaign in campaigns.items():
            for record in campaign.store.db.execute('SELECT * FROM m08_windows'):
                if record['state_artifact'] and rows[record['task_id']][arm] is None:
                    state = json.loads(campaign.artifacts.get(record['state_artifact']))
                    rows[record['task_id']][arm] = window_record(campaign,task_map[record['task_id']],record['run_id'],state)
        complete = interruption is None and len(completed)==32
        audits,archives = {},{}
        try:
            for arm,campaign in campaigns.items():
                try:
                    audits[arm] = audit_campaign(campaign,task_map,complete)
                except Exception as exc:
                    audits[arm] = {'passed':False,'error':type(exc).__name__+': '+str(exc)}
                    complete,interruption = False,interruption or 'integrity_audit_failed'
            residual = max(0,ledger.clock()-ledger.started-ledger.cost()['wall_seconds'])
            for campaign in campaigns.values():
                campaign.overhead('shared_control_plane',residual/len(campaigns))
            for arm,campaign in campaigns.items():
                with campaign.store.db:
                    campaign.store.db.execute('UPDATE m08_campaigns SET state=?,sealed_utc=? WHERE id=?',
                                              ('sealed' if complete else 'incomplete',utc(),campaign.id))
                archives[arm] = export(campaign,destination/f'{arm}-research.zip')
            ordered = [rows[t.task_id] for t in tasks]
            cost,elapsed = ledger.cost(),ledger.elapsed()
            if cost['tokens']>512000 or cost['model_decisions']>480 or elapsed>4800:
                complete,interruption = False,interruption or 'campaign_ceiling_violated'
            final_identity = discover(plan['model'])
            if final_identity!=identity:
                complete,interruption = False,interruption or 'post_generation_identity_changed'
            result = {'version':1,'milestone':'M0.8D','complete':complete,'interruption':interruption,'error':error,
                      'freeze_hash':lock.hash,'implementation_commit':lock.commit,'manifest_hash':lock.data['suite_manifest_hash'],
                      'schedule_hash':order['hash'],'model_identity':identity,'schedule_executed':completed,'rows':ordered,
                      'analysis':analyze(ordered,config,complete),'physical_cost':cost,'execution_elapsed_seconds':elapsed,
                      'audits':audits,'exports':archives,'evaluation_tasks_executed':0,'hidden_scores':0,'history':prior_audit(root),
                      'post_generation_identity':final_identity,'wall_accounting':'window/preparation/shared control receipts; elapsed also includes final export/report tail'}
            result['execution_elapsed_seconds'] = ledger.elapsed()
            if result['execution_elapsed_seconds']>4800:
                result['complete'],result['interruption'] = False,'campaign_wall_ceiling_violated'
                result['analysis'] = analyze(ordered,config,False)
            lock.validate()
            save(destination/'results.json',result)
            return result
        finally:
            for campaign in campaigns.values():
                campaign.close()
