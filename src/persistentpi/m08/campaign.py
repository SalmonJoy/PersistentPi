"""Experiment manager for shared-prefix generation and deferred private scoring."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid

from .._verification import save_evaluation
from ..adapters.platform import hardware, process_identity
from ..artifacts import atomic_write
from ..contracts import Budget, CheckpointRef, canonical, digest
from ..experiments import ExperimentManager
from ..orchestration import OrchestrationController
from ..runner import Runner
from ..telemetry import utc
from .analysis import COSTS
from .design import forecast as calculate_forecast, schedule
from .runtime import CaseVerifier, FeedbackModel, InitialPrefix, Window, observation_from, restore_controller


def summed_cost(payloads):
    return {name:sum(p.get(name,0) for p in payloads) for name in COSTS}


class Campaign(ExperimentManager):
    def __init__(self, state, plan, tasks, *, phase='dry_run', model_factory=None,
                 tokenizer=None, identity=None, freeze=None, spent=None, frozen_schedule=None,
                 calibration_receipt=None):
        super().__init__(state)
        self.plan,self.tasks,self.phase = plan,{t.task_id:t for t in tasks},phase
        self.model_factory,self.tokenizer,self.identity,self.freeze = model_factory,tokenizer,identity,freeze
        self.usage_kind = 'simulated' if model_factory else 'measured'
        self.spent = spent or {'wall_seconds':0.,'tokens':0}
        self.schedule = frozen_schedule or schedule(tasks)
        if set(e['task_id'] for e in self.schedule['entries']) != set(self.tasks):
            raise ValueError('Schedule task cohort mismatch')
        for entry in self.schedule['entries']:
            if self.tasks[entry['task_id']].hash != entry['task_hash'] or sorted(entry['order']) != ['D','O','R']:
                raise ValueError('Schedule identity/order mismatch')
        if digest(self.schedule['entries']) != self.schedule['hash']:
            raise ValueError('Schedule checksum mismatch')
        if phase not in ('dry_run','calibration','audit','evaluation'):
            raise ValueError('Unknown M0.8 phase')
        if not model_factory:
            if not freeze or not tokenizer or not identity:
                raise ValueError('Live generation requires verified freeze, tokenizer and model identity')
            freeze.validate()
            if digest(plan)!=freeze.data['preregistration_hash']:
                raise ValueError('In-memory preregistration differs from frozen expected hash')
            expected_tasks = freeze.data['suite_manifest']['task_hashes']
            if any(expected_tasks.get(t.task_id)!=t.hash for t in tasks):
                raise ValueError('Task differs from frozen suite')
            if (identity['digest'],identity['runtime_version'],identity['quantization'])!=(
                    plan['model']['expected_digest'],plan['model']['expected_runtime_version'],plan['model']['quantization']):
                raise ValueError('Live model identity differs from frozen Runner')
        if phase=='evaluation':
            if not freeze:
                raise ValueError('Evaluation requires immutable preregistration freeze')
            freeze.validate()
            if model_factory:
                raise ValueError('Formal evaluation cannot use a mocked Runner')
            if not calibration_receipt:
                raise ValueError('Evaluation requires complete calibration/audit/forecast receipt')
            if calibration_receipt['freeze_hash']!=freeze.hash or calibration_receipt['preregistration_hash']!=digest(plan):
                raise ValueError('Calibration freeze identity mismatch')
            predicted = calculate_forecast(calibration_receipt['selected_calibration'],calibration_receipt['forecast']['already_spent'])
            if predicted!=calibration_receipt['forecast'] or not predicted['launch_allowed']:
                raise ValueError('Evaluation physical forecast gate failed')
            if self.spent != predicted['already_spent']:
                raise ValueError('Evaluation cumulative expenditure was reset')
            if len(tasks)!=96 or any(t.split!='evaluation' for t in tasks) or len({t.template for t in tasks})!=32:
                raise ValueError('Evaluation must use all 96 tasks and 32 templates')
            if len({t.tier for t in tasks})!=1:
                raise ValueError('Evaluation tier must be selected wholesale')
            if next(iter(tasks)).tier!=calibration_receipt['tier']:
                raise ValueError('Evaluation differs from development-selected tier')
        suite_hash = digest({t.task_id:t.hash for t in tasks})
        if phase=='evaluation' and self.store.db.execute('SELECT 1 FROM m08_retired_cohorts WHERE suite_hash=?',(suite_hash,)).fetchone():
            raise ValueError('Evaluation cohort is retired')
        self.suite_hash = suite_hash
        self.id = str(uuid.uuid4())
        if phase=='evaluation':
            # Registry survives choosing a new campaign database/state directory.
            registry = freeze.root/'.local/m08-cohort-registry.sqlite'
            registry.parent.mkdir(parents=True,exist_ok=True)
            with sqlite3.connect(registry) as db:
                db.execute('CREATE TABLE IF NOT EXISTS retired(suite_hash TEXT PRIMARY KEY, campaign_id TEXT NOT NULL, freeze_hash TEXT NOT NULL, utc TEXT NOT NULL)')
                try:
                    db.execute('INSERT INTO retired VALUES(?,?,?,?)',
                        (freeze.data['suite_manifest_hash'],self.id,freeze.hash,utc()))
                except sqlite3.IntegrityError as exc:
                    raise ValueError('Frozen evaluation cohort already retired, including other state directories') from exc
        manifest = {'version':1,'protocol_version':'0.5','interface':{'output_protocol':'runner-json-schema-1','edit_primitive':'E0'},
                    'plan_hash':digest(plan),'phase':phase,'suite_hash':suite_hash,'model':plan['model'],
                    'scaffold_hash':digest({'plan':plan,'freeze':freeze.hash if freeze else 'mock'}),
                    'schedule':self.schedule['hash'],'usage_kind':self.usage_kind,'hardware':hardware()}
        self.manifest_hash = self.store.manifest('m08_campaign',manifest)
        self.manifest = manifest
        schedule_hash = self.artifacts.put(canonical(self.schedule),'m08_schedule','research')
        with self.store.db:
            self.store.db.execute('INSERT INTO experiments VALUES(?,?,?,?)',(self.id,self.manifest_hash,'0.5',utc()))
            self.store.db.execute('INSERT INTO m08_campaigns VALUES(?,?,?,?,?,?,?,?,?,?)',
                (self.id,phase,digest(plan),freeze.hash if freeze else None,suite_hash,schedule_hash,None,'running',utc(),None))
            if phase=='evaluation':
                self.store.db.execute('INSERT INTO m08_retired_cohorts VALUES(?,?,?)',(suite_hash,self.id,utc()))
        self.generation_started = time.monotonic()

    def cancelled(self):
        return (self.store.state/'STOP').exists()

    def physical_payloads(self, runs=None):
        records = self.store.db.execute('SELECT r.id,r.run_id,r.payload_hash FROM m08_receipts r JOIN m08_windows w ON w.run_id=r.run_id WHERE w.campaign_id=?',(self.id,))
        return [json.loads(self.artifacts.get(r['payload_hash'])) for r in records if runs is None or r['run_id'] in runs]

    def physical_cost(self, runs=None, include_overhead=True):
        payloads = self.physical_payloads(runs)
        if runs is None and include_overhead:
            payloads += [json.loads(self.artifacts.get(r[0])) for r in self.store.db.execute(
                'SELECT payload_hash FROM m08_overhead WHERE campaign_id=?',(self.id,))]
        return summed_cost(payloads)

    def overhead(self, kind, wall_seconds, run_id=None):
        key = self.artifacts.put(canonical({'version':1,'wall_seconds':wall_seconds,'run_id':run_id}),'physical_overhead','research')
        with self.store.db:
            self.store.db.execute('INSERT INTO m08_overhead VALUES(?,?,?,?)',(str(uuid.uuid4()),self.id,kind,key))

    def physical_bundle_cost(self, task):
        windows = list(self.store.db.execute('SELECT run_id,task_id FROM m08_windows WHERE campaign_id=?',(self.id,)))
        runs = {w['run_id'] for w in windows if w['task_id']==task.task_id}
        if not runs:
            raise ValueError('Task has no physical acquisition windows')
        payloads = self.physical_payloads(runs)
        for row in self.store.db.execute('SELECT payload_hash FROM m08_overhead WHERE campaign_id=?',(self.id,)):
            overhead = json.loads(self.artifacts.get(row[0]))
            if overhead.get('run_id') in runs:
                payloads.append(overhead)
            elif overhead.get('run_id') is None:
                # Common control-plane cost is allocated by executed windows,
                # never by outcomes or the sum of logical D/O/R policy costs.
                payloads.append({'wall_seconds':overhead['wall_seconds']*len(runs)/len(windows)})
        return summed_cost(payloads)

    def remaining_limits(self, active_wall=0):
        cost = self.physical_cost()
        elapsed = max(cost['wall_seconds']+active_wall,time.monotonic()-self.generation_started)
        return {'tokens':max(0,12000000-self.spent['tokens']-cost['tokens']),
                'wall_seconds':max(0,12*3600-self.spent['wall_seconds']-elapsed)}

    def check_limits(self, reserve_tokens=0, active_wall=0):
        cost = self.physical_cost()
        if self.spent['tokens']+cost['tokens']+reserve_tokens > 12000000:
            raise RuntimeError('Hard physical campaign token ceiling')
        elapsed = max(cost['wall_seconds']+active_wall,time.monotonic()-self.generation_started)
        if self.spent['wall_seconds']+elapsed >= 12*3600:
            raise RuntimeError('Hard physical campaign wall ceiling')

    def new_run(self, task, arm, index, parent=None):
        run = str(uuid.uuid4())
        budget = Budget(**self.plan['window'])
        columns = ('id','experiment_id','trial_key','mode','task_id','task_hash','fixture_version',
                   'protocol_version','scaffold_id','scaffold_hash','parent_scaffold_id','scaffold_version',
                   'seed','replicate','manifest_hash','git_commit','dirty','status','budget_json','usage_json',
                   'platform_json','owner_pid','owner_identity','created_utc')
        values = (run,self.id,digest([self.id,task.hash,arm,index]),'development' if self.phase!='evaluation' else 'formal',
                  task.task_id,task.hash,'m08-1','0.5','m08-fixed-C3',self.manifest['scaffold_hash'],'m07-V1','1',42,0,
                  self.manifest_hash,self.freeze.commit if self.freeze else None,0 if self.freeze else 1,'running',
                  canonical(budget).decode(),'{}',canonical(self.manifest['hardware']).decode(),os.getpid(),
                  process_identity(os.getpid()),utc())
        with self.store.db:
            self.store.db.execute('INSERT INTO runs('+','.join(columns)+') VALUES('+','.join('?' for _ in columns)+')',values)
            self.store.db.execute('INSERT INTO m08_windows VALUES(?,?,?,?,?,?,?)',
                                  (run,self.id,task.task_id,arm,index,parent,None))
        self.store.event(run,'control_plane','window_reserved',{'version':1,'arm':arm,'candidate_index':index,'parent_prefix':parent})
        return run,budget

    def acquire(self, task, arm='I', index=1, prefix=None, previous=None):
        preparation_began = time.monotonic()
        status = self.store.db.execute('SELECT state FROM m08_campaigns WHERE id=?',(self.id,)).fetchone()[0]
        if status!='running':
            raise ValueError('Generation cannot resume after sealing/interruption')
        if task.task_id not in self.tasks or self.tasks[task.task_id].hash!=task.hash:
            raise ValueError('Acquisition task is outside this campaign')
        if arm=='I':
            if index!=1 or prefix is not None or previous is not None:
                raise ValueError('Initial acquisition must be one clean first window')
        elif arm not in ('D','O','R') or prefix is None or not 2<=index<=5:
            raise ValueError('Invalid continuation window identity')
        if self.freeze:
            self.freeze.validate()
        if prefix:
            initial_state = self.validate_prefix(prefix,task)
            if index==2:
                required = initial_state
            else:
                prior = self.store.db.execute('SELECT state_artifact FROM m08_windows WHERE campaign_id=? AND task_id=? AND arm=? AND candidate_index=?',
                                             (self.id,task.task_id,arm,index-1)).fetchone()
                if not prior or not prior[0]:
                    raise ValueError('Previous verified candidate window is missing')
                required = json.loads(self.artifacts.get(prior[0]))
            if required['status']!='finished' or not required['candidate'] or required['candidate']['outcome']!='fail':
                raise ValueError('Only prior verified FAIL permits continuation')
            if previous is not None and digest(previous)!=digest(required):
                raise ValueError('Continuation state differs from its exact predecessor')
            previous = required
        self.check_limits()
        run,budget = self.new_run(task,arm,index,prefix.id if prefix else None)
        workspace = self.store.state/'workspaces'/run
        if not prefix or arm=='R':
            if prefix:
                original = prefix.original_checkpoint
                self.artifacts.restore(CheckpointRef(original),workspace)
            else:
                workspace.mkdir(parents=True)
                atomic_write(workspace/'src/solution.py',task.mutant.encode())
                atomic_write(workspace/'public_tests/cases.json',canonical(task.public))
            controller = OrchestrationController('V1',task.view.editable_paths,2)
            observations = ()
        else:
            state = previous or json.loads(self.artifacts.get(prefix.state_artifact))
            self.artifacts.restore(CheckpointRef(state['selected_checkpoint']),workspace)
            controller = restore_controller(state['controller'])
            observations = tuple(observation_from(o) for o in state['observations'])
        initial = self.artifacts.checkpoint(workspace)
        self.store.update_run(run,initial_checkpoint=initial.hash,selected_checkpoint=initial.hash)
        self.store.event(run,'control_plane','initial_checkpoint',{'checkpoint':initial.to_dict()})
        verifier = CaseVerifier(self.artifacts,run,task.public,task.view.public_test_id)
        self.overhead('window_preparation',time.monotonic()-preparation_began,run)
        mode = 'outcome_only' if arm=='O' else 'detailed'
        window = Window(self.store,self.artifacts,run,workspace,task.view,budget,verifier,
                        controller=controller,campaign=self,candidate_index=index,history=observations)
        if self.model_factory:
            model = self.model_factory(task,arm,index,controller,mode)
        else:
            model = FeedbackModel(self.plan['model'],self.identity,controller,mode,self.tokenizer)
        state,artifact = window.run(Runner(model))
        if state['status']!='finished':
            with self.store.db:
                self.store.db.execute("UPDATE m08_campaigns SET state='incomplete' WHERE id=?",(self.id,))
            raise RuntimeError('Campaign interrupted; no automatic retry: '+state['stop_reason'])
        return run,initial.hash,state,artifact

    def transcript(self, run, observations):
        calls = [json.loads(e[0]) for e in self.store.db.execute(
            "SELECT payload_json FROM events WHERE run_id=? AND type IN ('model_request','model_call_completed') ORDER BY sequence",(run,))]
        return {'version':1,'observations':observations,'model_call_records':calls}

    def acquire_prefix(self, task):
        run,original,state,state_artifact = self.acquire(task)
        candidate = state['candidate']
        transcript = self.artifacts.put(canonical(self.transcript(run,state['observations'])),'initial_transcript','public')
        prefix = InitialPrefix(1,task.task_id,task.hash,self.id,self.manifest_hash,self.manifest['scaffold_hash'],
            '0.5',original,candidate['checkpoint'] if candidate else None,transcript,
            candidate['public_result_hash'] if candidate else None,run,state_artifact,tuple(state['receipt_ids']),utc())
        key = self.artifacts.put(canonical(prefix),'initial_prefix','research')
        if key != prefix.id:
            raise ValueError('Prefix identity mismatch')
        with self.store.db:
            self.store.db.execute('INSERT INTO m08_initial_prefixes VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
                (prefix.id,self.id,task.task_id,task.hash,self.manifest_hash,run,original,prefix.candidate_checkpoint,
                 transcript,prefix.public_result_hash,state_artifact,prefix.created_utc))
        self.store.event(run,'control_plane','initial_prefix_created',{'prefix_id':prefix.id,'physical_receipts':prefix.physical_receipts})
        return prefix

    def validate_prefix(self, prefix, task):
        row = self.store.db.execute('SELECT * FROM m08_initial_prefixes WHERE id=?',(prefix.id,)).fetchone()
        if row is None or self.artifacts.get(prefix.id) != canonical(prefix):
            raise ValueError('InitialPrefix acquisition/transcript/result lineage mismatch')
        if (prefix.task_id,prefix.task_hash,prefix.campaign_id,prefix.manifest_hash,prefix.scaffold_hash,prefix.protocol) != (
                task.task_id,task.hash,self.id,self.manifest_hash,self.manifest['scaffold_hash'],'0.5'):
            raise ValueError('InitialPrefix task/manifest/scaffold mismatch')
        comparisons = {'acquisition_run':prefix.acquisition_run,'original_checkpoint':prefix.original_checkpoint,
                       'candidate_checkpoint':prefix.candidate_checkpoint,'transcript_hash':prefix.transcript_hash,
                       'public_result_hash':prefix.public_result_hash,'state_artifact':prefix.state_artifact}
        if any(row[k]!=v for k,v in comparisons.items()):
            raise ValueError('InitialPrefix database lineage mismatch')
        state = json.loads(self.artifacts.get(prefix.state_artifact))
        if digest(self.transcript(prefix.acquisition_run,state['observations'])) != prefix.transcript_hash or tuple(state['receipt_ids']) != prefix.physical_receipts:
            raise ValueError('Prefix transcript/receipt mismatch')
        candidate = state['candidate']
        if (candidate['checkpoint'] if candidate else None)!=prefix.candidate_checkpoint or (
                candidate['public_result_hash'] if candidate else None)!=prefix.public_result_hash:
            raise ValueError('Prefix candidate/result mismatch')
        physical = tuple(r[0] for r in self.store.db.execute('SELECT id FROM m08_receipts WHERE run_id=? ORDER BY rowid',(prefix.acquisition_run,)))
        if physical != prefix.physical_receipts:
            raise ValueError('Prefix physical receipts changed')
        run = self.store.row(prefix.acquisition_run)
        if (run['task_hash'],run['manifest_hash'],run['initial_checkpoint'],run['protocol_version']) != (
                prefix.task_hash,prefix.manifest_hash,prefix.original_checkpoint,'0.5'):
            raise ValueError('Acquisition run differs from prefix')
        for key in (prefix.original_checkpoint,prefix.candidate_checkpoint,prefix.transcript_hash,prefix.public_result_hash):
            if key:
                self.artifacts.get(key)
        return state

    def branch(self, task, prefix, arm, execute=True):
        state = self.validate_prefix(prefix,task)
        if arm not in ('D','O','R'):
            raise ValueError('Unknown branch')
        identity = digest([prefix.id,arm])
        lineage = self.artifacts.put(canonical({'version':1,'prefix_id':prefix.id,'arm':arm,
                                              'parent':asdict(prefix)}),'branch_lineage','research')
        with self.store.db:
            self.store.db.execute('INSERT INTO m08_branches VALUES(?,?,?,?)',(identity,prefix.id,arm,lineage))
        if not execute or state['candidate'] is None or state['candidate']['outcome']!='fail' or state['status']!='finished':
            return
        for index in range(2,6):
            runs = {prefix.acquisition_run} | {r[0] for r in self.store.db.execute(
                'SELECT run_id FROM m08_windows WHERE campaign_id=? AND task_id=? AND arm=?',(self.id,task.task_id,arm))}
            cost = self.physical_cost(runs)
            if cost['tokens']>=80000 or cost['model_decisions']>=75 or cost['tool_calls']>=75 or cost['wall_seconds']>=600:
                raise RuntimeError('Logical trajectory ceiling violated')
            _,_,state,_ = self.acquire(task,arm,index,prefix,state)
            if not state['candidate'] or state['candidate']['outcome']!='fail' or state['status']!='finished':
                break

    def run_bundle(self, task, order):
        prefix = self.acquire_prefix(task)
        for arm in order:
            self.branch(task,prefix,arm)
        return prefix

    def run_all(self):
        try:
            for entry in self.schedule['entries']:
                self.run_bundle(self.tasks[entry['task_id']],entry['order'])
            self.seal()
        except BaseException:
            with self.store.db:
                self.store.db.execute("UPDATE m08_campaigns SET state='incomplete' WHERE id=?",(self.id,))
            raise

    def seal(self):
        if self.freeze:
            self.freeze.validate()
        state = self.store.db.execute('SELECT state FROM m08_campaigns WHERE id=?',(self.id,)).fetchone()[0]
        if state!='running':
            raise ValueError('Incomplete/terminal campaign cannot be sealed')
        prefixes = list(self.store.db.execute('SELECT * FROM m08_initial_prefixes WHERE campaign_id=?',(self.id,)))
        if {p['task_id'] for p in prefixes} != set(self.tasks):
            raise ValueError('Missing initial acquisitions')
        for p in prefixes:
            arms = {r[0] for r in self.store.db.execute('SELECT arm FROM m08_branches WHERE prefix_id=?',(p['id'],))}
            if arms != {'D','O','R'}:
                raise ValueError('Incomplete D/O/R bundle')
        if self.store.db.execute("SELECT 1 FROM m08_windows w JOIN runs r ON w.run_id=r.id WHERE w.campaign_id=? AND (w.state_artifact IS NULL OR r.status!='finished')",(self.id,)).fetchone():
            raise ValueError('Unfinished windows prevent generation sealing')
        with self.store.db:
            self.store.db.execute("UPDATE m08_campaigns SET state='sealed',sealed_utc=? WHERE id=?",(utc(),self.id))
        residual = time.monotonic()-self.generation_started-self.physical_cost()['wall_seconds']
        self.overhead('generation_control_plane',max(0,residual))

    def reconstruct(self):
        rows = []
        for task in sorted(self.tasks.values(),key=lambda t:t.task_id):
            prefix_row = self.store.db.execute('SELECT * FROM m08_initial_prefixes WHERE campaign_id=? AND task_id=?',(self.id,task.task_id)).fetchone()
            if prefix_row is None:
                raise ValueError('Missing initial prefix')
            data = json.loads(self.artifacts.get(prefix_row['id']))
            data['physical_receipts'] = tuple(data['physical_receipts'])
            prefix = InitialPrefix(**data)
            initial = self.validate_prefix(prefix,task)
            row = {'task_id':task.task_id,'family':task.family,'template':task.template,
                   'tier':task.tier,'split':task.split,'arms':{},'telemetry':{}}
            for arm in ('D','O','R'):
                windows = [(prefix.acquisition_run,initial)] + [(w['run_id'],json.loads(self.artifacts.get(w['state_artifact']))) for w in self.store.db.execute(
                    'SELECT * FROM m08_windows WHERE campaign_id=? AND task_id=? AND arm=? ORDER BY candidate_index',(self.id,task.task_id,arm))]
                horizons = []
                for k in range(1,6):
                    active = windows[:k]
                    candidates = [s['candidate'] for _,s in active if s['candidate']]
                    passed = next((c for c in candidates if c['outcome']=='pass'),None)
                    selected = passed or (candidates[-1] if candidates else None)
                    checkpoint = selected['checkpoint'] if selected else prefix.original_checkpoint
                    score = self.store.db.execute('SELECT outcome FROM m08_scores WHERE campaign_id=? AND task_id=? AND checkpoint_hash=?',(self.id,task.task_id,checkpoint)).fetchone()
                    horizons.append({'k':k,'prefix_id':prefix.id,'checkpoint':checkpoint,
                        'public':selected['outcome'] if selected else None,'hidden':score[0] if score else None,
                        'cost':self.physical_cost({run for run,_ in active}),
                        'stop_reason':active[-1][1]['stop_reason'],'candidate_count':len(candidates)})
                row['arms'][arm] = horizons
                from .stagnation import metrics
                row['telemetry'][arm] = metrics(self,[run for run,_ in windows])
            rows.append(row)
        return rows

    def score(self):
        state = self.store.db.execute('SELECT state FROM m08_campaigns WHERE id=?',(self.id,)).fetchone()[0]
        if state!='sealed' or self.phase not in ('dry_run','evaluation'):
            raise ValueError('Hidden scoring only after sealed dry-run/evaluation generation')
        if self.freeze:
            self.freeze.validate()
        for row in self.reconstruct():
            task = self.tasks[row['task_id']]
            run = self.store.db.execute('SELECT acquisition_run FROM m08_initial_prefixes WHERE campaign_id=? AND task_id=?',(self.id,task.task_id)).fetchone()[0]
            checkpoints = sorted({p['checkpoint'] for arm in row['arms'].values() for p in arm})
            for checkpoint in checkpoints:
                verifier = CaseVerifier(self.artifacts,run,task.hidden,task.task_id+':hidden:v1','hidden')
                self.check_limits()
                began = time.monotonic()
                result = verifier.check(CheckpointRef(checkpoint),min(5,self.remaining_limits()['wall_seconds']),4096,self.cancelled)
                if result.outcome not in ('pass','fail'):
                    raise RuntimeError('Incomplete hidden measurement')
                record = save_evaluation(self.store,self.artifacts,run,None,CheckpointRef(checkpoint),verifier.test_hash,result)
                key = self.artifacts.put(canonical(record),'hidden_prefix_score','hidden')
                with self.store.db:
                    self.store.db.execute('INSERT INTO m08_scores VALUES(?,?,?,?,?)',(self.id,task.task_id,checkpoint,result.outcome,key))
                self.overhead('hidden_scoring',time.monotonic()-began)
        with self.store.db:
            self.store.db.execute("UPDATE m08_campaigns SET state='scored' WHERE id=?",(self.id,))
        return self.reconstruct()

    def costs(self):
        rows = self.reconstruct()
        logical = {arm:summed_cost([r['arms'][arm][4]['cost'] for r in rows]) for arm in ('D','O','R')}
        physical = self.physical_cost(include_overhead=False)
        root_runs = {p[0] for p in self.store.db.execute('SELECT acquisition_run FROM m08_initial_prefixes WHERE campaign_id=?',(self.id,))}
        roots = self.physical_cost(root_runs)
        for name in COSTS:
            if abs(sum(logical[a][name] for a in logical)-physical[name]-2*roots[name])>1e-7:
                raise ValueError('Physical/logical cost reconciliation failed: '+name)
        total = self.physical_cost()
        overhead = {name:total[name]-physical[name] for name in COSTS}
        return {'version':1,'physical_study_cost':total,'physical_generation_cost':physical,
                'physical_overhead_cost':overhead,'logical_policy_cost':logical,
                'shared_prefix_cost':roots,'reconciliation':'sum(logical generation) = physical generation + 2 * shared_prefix'}
