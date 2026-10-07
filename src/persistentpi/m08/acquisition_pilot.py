"""Isolated M0.8C pilot using unchanged M0.8B acquisition execution."""
from dataclasses import dataclass, replace
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
from ..orchestration import OrchestrationController
from ..telemetry import utc
from .acquisition_analysis import analyze, diagnostics
from .analysis import COSTS
from .campaign import Campaign, summed_cost
from .feedback import prompt
from .freeze import checksum, freeze_paths
from .runtime import FeedbackModel, observation_from, restore_controller
from .tokenizer import FrozenTokenizer

HISTORY = '038c370ce410c07b93e07cfba1cc93467dd1fac4'
LEGACY = 'Edit is empty, unchanged or too large'
PRECISE = 'Edit is unchanged: old and new are identical.'


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def save(path, value):
    path = Path(path)
    if path.exists():
        raise ValueError('Research artifact already exists: '+str(path))
    atomic_write(path, canonical(value))
    return value


def history_audit(root):
    folder = Path(root)/'docs/research-records/m08b'
    checks = json.loads((folder/'checksums.json').read_bytes())
    if any(checksum(folder/name) != expected for name, expected in checks.items()):
        raise ValueError('Historical M0.8B archive checksum mismatch')
    for name in checks:
        if hashlib.sha256(subprocess.run(['git', '-C', str(root), 'show', HISTORY+':docs/research-records/m08b/'+name],
                                        check=True, capture_output=True).stdout).hexdigest() != checks[name]:
            raise ValueError('Historical M0.8B differs from evidence commit: '+name)
    summary = json.loads((folder/'summary.json').read_bytes())
    if not summary['selection']['stop'] or summary['selection']['selected_tier'] is not None:
        raise ValueError('Historical calibration-stop outcome changed')
    with sqlite3.connect((folder/'raw/experiments.sqlite').resolve().as_uri()+'?mode=ro&immutable=1', uri=True) as db:
        db.row_factory = sqlite3.Row
        runs = list(db.execute('SELECT * FROM runs'))
        evaluations = list(db.execute('SELECT split FROM evaluations'))
        if len(runs) != 96 or any(r['mode'] != 'development' or r['status'] != 'finished' for r in runs):
            raise ValueError('Historical run cohort mismatch')
        if len(evaluations) != 24 or any(r['split'] != 'public' for r in evaluations):
            raise ValueError('Historical private/evaluation execution detected')
        if db.execute('SELECT COUNT(*) FROM m08_scores').fetchone()[0] or db.execute(
                'SELECT COUNT(*) FROM m08_retired_cohorts').fetchone()[0]:
            raise ValueError('Historical scoring/retirement detected')
    return {'commit': HISTORY, 'checksums': checks, 'development_windows': 96,
            'public_verifications': 24, 'hidden_scores': 0, 'evaluation_runs': 0,
            'outcome': 'no difficulty tier qualified'}


def selection(metadata):
    pool = [r for r in metadata if r['tier'] == 'L2']
    if len(pool) != 32 or len({r['task_id'] for r in pool}) != 32:
        raise ValueError('Require exactly the 32 L2 development records')
    groups = {}
    for row in pool:
        groups.setdefault(row['template'], []).append(row)
    if len(groups) != 16 or any(len(g) != 2 for g in groups.values()):
        raise ValueError('Require two instances in each of 16 development templates')
    chosen = [min(groups[t], key=lambda r: r['task_id']) for t in sorted(groups)]
    if len({r['family'] for r in chosen}) != 8:
        raise ValueError('Require eight fixed development families')
    return chosen


def schedule(tasks):
    entries = []
    for i, task in enumerate(sorted(tasks, key=lambda t: t.template)):
        for arm in ('A', 'B') if i % 2 == 0 else ('B', 'A'):
            entries.append({'ordinal': len(entries)+1, 'pair': i+1, 'condition': arm,
                            'task_id': task.task_id, 'task_hash': task.hash,
                            'family': task.family, 'template': task.template})
    return {'version': 1, 'entries': entries, 'hash': digest(entries)}


@dataclass(frozen=True)
class DevelopmentTask:
    task_id: str
    hash: str
    family: str
    template: str
    mutant: str
    public: tuple
    view: TaskView
    original_checkpoint: str
    tier: str = 'L2'
    split: str = 'development'


def public_inputs(root):
    """Only selected historical dev public checkpoints; no suite/task-file loader."""
    folder = Path(root)/'docs/research-records/m08b'
    metadata = json.loads((folder/'difficulty.json').read_bytes())['per_task']
    selected = selection(metadata)
    tasks, provenance = [], []
    with sqlite3.connect((folder/'raw/experiments.sqlite').resolve().as_uri()+'?mode=ro&immutable=1', uri=True) as db, \
            zipfile.ZipFile(folder/'raw/research.zip') as archive:
        db.row_factory = sqlite3.Row

        def blob(key):
            row = db.execute('SELECT kind,visibility FROM artifacts WHERE hash=?', (key,)).fetchone()
            if not row or row['visibility'] != 'public' or row['kind'] not in ('checkpoint', 'workspace_file', 'model_request'):
                raise ValueError('Pilot input is not a whitelisted public artifact')
            raw = archive.read('artifacts/'+key)
            if hashlib.sha256(raw).hexdigest() != key:
                raise ValueError('Public input artifact checksum mismatch')
            return raw

        for meta in selected:
            runs = list(db.execute("SELECT * FROM runs WHERE task_id=? AND mode='development'", (meta['task_id'],)))
            if len(runs) != 1:
                raise ValueError('Development provenance is ambiguous')
            run = runs[0]
            checkpoint = json.loads(blob(run['initial_checkpoint']))
            if set(checkpoint['files']) != {'src/solution.py', 'public_tests/cases.json'}:
                raise ValueError('Public checkpoint contains undeclared files')
            source = blob(checkpoint['files']['src/solution.py']).decode('utf-8')
            cases = tuple(json.loads(blob(checkpoint['files']['public_tests/cases.json'])))
            request = db.execute("SELECT payload_json FROM events WHERE run_id=? AND type='model_request' ORDER BY sequence LIMIT 1",
                                 (run['id'],)).fetchone()
            key = json.loads(request[0])['request_artifact']
            task_data = json.loads(json.loads(blob(key))['payload']['messages'][1]['content'])['task']
            task_data.pop('contract_version', None)
            task_data['editable_paths'] = tuple(task_data['editable_paths'])
            task_data['readable_paths'] = tuple(task_data['readable_paths'])
            view = TaskView(**task_data)
            if view.task_id != meta['task_id'] or len(cases) != 8:
                raise ValueError('Development public task identity mismatch')
            tasks.append(DevelopmentTask(meta['task_id'], run['task_hash'], meta['family'], meta['template'],
                                         source, cases, view, run['initial_checkpoint']))
            provenance.append({'task_id': meta['task_id'], 'task_hash': run['task_hash'],
                               'source_run': run['id'], 'checkpoint': run['initial_checkpoint'],
                               'taskview_request': key, 'files': checkpoint['files']})
    return tasks, provenance


def project(observation, condition, max_edit_bytes):
    if condition not in ('A', 'B'):
        raise ValueError('Unknown pilot feedback condition')
    if condition == 'A' or observation.action.tool != 'edit_file' or observation.result.ok or observation.result.error != LEGACY:
        return observation
    args = observation.action.arguments
    old, new = args.get('old'), args.get('new')
    if (set(args) == {'path', 'old', 'new'} and isinstance(args['path'], str)
            and isinstance(old, str) and isinstance(new, str) and old and old == new
            and len(canonical(args)) <= max_edit_bytes):
        return replace(observation, result=replace(observation.result, error=PRECISE))
    return observation


class PilotModel(FeedbackModel):
    def __init__(self, config, identity, controller, tokenizer, condition, max_edit_bytes, client=None):
        super().__init__(config, identity, controller, 'detailed', tokenizer, client)
        self.condition, self.max_edit_bytes = condition, max_edit_bytes

    def prompt(self, task, observations, state):
        observations = tuple(project(o, self.condition, self.max_edit_bytes) for o in observations)
        return super().prompt(task, observations, state)


def implementation_paths(root):
    return sorted(set(freeze_paths(root)+[Path(root)/p for p in
        ('configs/m08c-preregistered.json', 'docs/m08c-preregistration.md', 'scripts/m08c.py')]))


class PilotFreeze:
    def __init__(self, path, root, expected, *, historical_audit=False):
        self.path, self.root = Path(path), Path(root).resolve()
        self.hash = checksum(self.path)
        if self.hash != expected:
            raise ValueError('Pilot freeze hash mismatch')
        self.data = json.loads(self.path.read_bytes())
        self.commit = self.data['implementation_commit']
        self.historical_audit = historical_audit
        self.validate()

    def validate(self):
        if checksum(self.path) != self.hash or self.data['milestone'] != 'M0.8C':
            raise ValueError('Pilot freeze changed')
        expected = {p.relative_to(self.root).as_posix() for p in implementation_paths(self.root)}
        if expected != set(self.data['files']):
            raise ValueError('Pilot implementation file set changed')
        for name, sha in self.data['files'].items():
            actual = checksum(self.root/name)
            if self.historical_audit:
                raw = subprocess.run(['git', '-C', str(self.root), 'show', self.commit+':'+name],
                                     check=True, capture_output=True).stdout
                actual = hashlib.sha256(raw).hexdigest()
            if actual != sha:
                raise ValueError('Pilot frozen implementation changed: '+name)
        for name, sha in self.data['inputs'].items():
            if checksum(self.path.parent/name) != sha:
                raise ValueError('Pilot frozen input changed: '+name)
        plan = json.loads((self.root/'configs/m08-preregistered.json').read_bytes())
        if digest(plan) != self.data['preregistration_hash']:
            raise ValueError('Original model/window configuration changed')
        if digest(json.loads((self.root/'configs/m08c-preregistered.json').read_bytes())) != self.data['pilot_config_hash']:
            raise ValueError('Pilot preregistration changed')
        return plan

    def tasks(self):
        data = json.loads((self.path.parent/'tasks.json').read_bytes())
        manifest = json.loads((self.path.parent/'manifest.json').read_bytes())
        if digest(manifest) != self.data['suite_manifest_hash'] or set(data) != set(manifest['task_hashes']):
            raise ValueError('Pilot selected task set changed')
        tasks = []
        for identity, row in data.items():
            if row['tier'] != 'L2' or row['split'] != 'development' or identity != row['task_id']:
                raise ValueError('Evaluation/other-tier task access prohibited')
            if digest(row) != manifest['public_input_hashes'][identity] or row['hash'] != manifest['task_hashes'][identity]:
                raise ValueError('Pilot public task snapshot mismatch')
            view = dict(row['view'])
            view.pop('contract_version', None)
            view['editable_paths'], view['readable_paths'] = tuple(view['editable_paths']), tuple(view['readable_paths'])
            tasks.append(DevelopmentTask(**{**row, 'public': tuple(row['public']), 'view': TaskView(**view)}))
        if len(tasks) != 16 or len({t.template for t in tasks}) != 16 or len({t.family for t in tasks}) != 8:
            raise ValueError('Pilot cohort cardinality changed')
        return sorted(tasks, key=lambda t: t.template)


def prepare(root, destination):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    if destination.exists() or git(root, 'status', '--porcelain'):
        raise ValueError('Freeze requires a clean commit and new destination')
    history = history_audit(root)
    old_lock = json.loads((root/'docs/research-records/m08a/freeze.json').read_bytes())
    if any(checksum(root/name) != sha for name, sha in old_lock['files'].items()):
        raise ValueError('Existing M0.8 scaffold differs from historical freeze')
    if git(root, 'cat-file', '-t', 'm0.8b-calibration-stop') != 'tag' or git(root, 'rev-parse', 'm0.8b-calibration-stop^{}') != HISTORY:
        raise ValueError('Annotated historical stop tag missing/mismatched')
    tasks, provenance = public_inputs(root)
    plan = json.loads((root/'configs/m08-preregistered.json').read_bytes())
    config = json.loads((root/'configs/m08c-preregistered.json').read_bytes())
    identity = discover(plan['model'])
    baseline = json.loads((root/'docs/research-records/m08b/preflight.json').read_bytes())
    if identity != baseline['model_identity']:
        raise ValueError('Runner identity mismatch prevents pilot')
    tokenizer = FrozenTokenizer.installed(plan['model'])
    if tokenizer.identity != baseline['tokenizer_identity']:
        raise ValueError('Tokenizer identity mismatch prevents pilot')
    serialized = {t.task_id: json.loads(canonical(t)) for t in tasks}
    manifest = {'version': 1, 'tier': 'L2', 'split': 'development', 'selection': config['selection'],
                'task_hashes': {t.task_id: t.hash for t in tasks},
                'public_input_hashes': {key: digest(value) for key, value in serialized.items()},
                'provenance': provenance}
    frozen_schedule = schedule(tasks)
    prompts = {}
    for t in tasks:
        model = PilotModel(plan['model'], identity, OrchestrationController('V1', t.view.editable_paths, 2),
                           tokenizer, 'A', plan['window']['max_edit_bytes'])
        state = DecisionState(1, 14, 15, 16000, 120)
        messages, meta = model.prompt(t.view, (), state)
        prompts[t.task_id] = {'A': digest(messages), 'B': digest(messages), 'prompt_bytes': meta['prompt_bytes']}
    inputs = {'history.json': history, 'tasks.json': serialized, 'manifest.json': manifest,
              'schedule.json': frozen_schedule, 'configs.json': {'A': plan, 'B': plan, 'pilot': config},
              'model.json': {'identity': identity, 'tokenizer': tokenizer.identity}, 'initial-prompts.json': prompts}
    for name, value in inputs.items():
        save(destination/name, value)
    receipt = {'milestone': 'M0.8C', 'version': 1, 'created_utc': utc(),
               'implementation_commit': git(root, 'rev-parse', 'HEAD'), 'historical_commit': HISTORY,
               'preregistration_hash': digest(plan), 'pilot_config_hash': digest(config),
               'suite_manifest': manifest, 'suite_manifest_hash': digest(manifest),
               'schedule_hash': frozen_schedule['hash'], 'model': identity,
               'tokenizer_identity': tokenizer.identity, 'initial_prompts': prompts,
               'files': {p.relative_to(root).as_posix(): checksum(p) for p in implementation_paths(root)},
               'inputs': {name: checksum(destination/name) for name in inputs},
               'feedback_strings': {'A': LEGACY, 'B': PRECISE}, 'live_inference_calls': 0}
    save(destination/'freeze.json', receipt)
    return {'freeze': str(destination/'freeze.json'), 'sha256': checksum(destination/'freeze.json'),
            'manifest_hash': digest(manifest), 'schedule_hash': frozen_schedule['hash'], 'commit': receipt['implementation_commit']}


class PilotCeiling(RuntimeError):
    pass


class Ledger:
    def __init__(self, limits, clock=time.monotonic):
        self.limits, self.clock, self.started = limits, clock, clock()
        self.campaigns = []

    def cost(self):
        return summed_cost([c.physical_cost() for c in self.campaigns])

    def elapsed(self, active_wall=0):
        return max(self.clock()-self.started, self.cost()['wall_seconds']+active_wall)

    def remaining(self, active_wall=0):
        return {'tokens': max(0, self.limits['tokens']-self.cost()['tokens']),
                'wall_seconds': max(0, self.limits['wall_seconds']-self.elapsed(active_wall))}

    def check(self, reserve_tokens=0, active_wall=0):
        cost = self.cost()
        if cost['tokens']+reserve_tokens > self.limits['tokens']:
            raise PilotCeiling('Pilot token ceiling')
        if cost['model_decisions'] >= self.limits['model_calls']:
            raise PilotCeiling('Pilot model-call ceiling')
        if self.elapsed(active_wall) >= self.limits['wall_seconds']:
            raise PilotCeiling('Pilot execution wall ceiling')


class PilotCampaign(Campaign):
    def __init__(self, state, plan, tasks, condition, ledger, *, tokenizer=None, identity=None, freeze=None,
                 model_factory=None, frozen_schedule=None):
        if condition not in ('A', 'B') or any(t.split != 'development' or t.tier != 'L2' for t in tasks):
            raise ValueError('Pilot only accepts A/B L2 development acquisitions')
        self.condition, self.ledger = condition, ledger
        super().__init__(state, plan, tasks, phase='calibration', tokenizer=tokenizer, identity=identity,
                         freeze=freeze, model_factory=model_factory)
        self.manifest = {**self.manifest, 'milestone': 'M0.8C', 'condition': condition,
                         'pilot_schedule': frozen_schedule, 'candidate_horizon': 1,
                         'rejection_feedback': LEGACY if condition == 'A' else PRECISE}
        self.manifest['scaffold_hash'] = digest(self.manifest)
        self.manifest_hash = self.store.manifest('m08c_acquisition', self.manifest)
        with self.store.db:
            self.store.db.execute('UPDATE experiments SET manifest_hash=? WHERE id=?', (self.manifest_hash, self.id))
            self.store.db.executescript("""
                CREATE TRIGGER pilot_no_hidden BEFORE INSERT ON evaluations WHEN NEW.split!='public'
                BEGIN SELECT RAISE(ABORT,'Pilot prohibits hidden scoring'); END;
                CREATE TRIGGER pilot_no_scores BEFORE INSERT ON m08_scores
                BEGIN SELECT RAISE(ABORT,'Pilot prohibits hidden scores'); END;
                CREATE TRIGGER pilot_no_retirement BEFORE INSERT ON m08_retired_cohorts
                BEGIN SELECT RAISE(ABORT,'Pilot prohibits evaluation retirement'); END;
                CREATE TRIGGER pilot_no_formal BEFORE INSERT ON runs WHEN NEW.mode!='development'
                BEGIN SELECT RAISE(ABORT,'Pilot prohibits evaluation runs'); END;
            """)
        if model_factory is None:
            self.model_factory = lambda task, arm, index, controller, mode: PilotModel(
                plan['model'], identity, controller, tokenizer, condition, plan['window']['max_edit_bytes'])
        ledger.campaigns.append(self)

    def remaining_limits(self, active_wall=0):
        return self.ledger.remaining(active_wall)

    def cancelled(self):
        return super().cancelled() or (self.store.state.parent/'STOP').exists()

    def check_limits(self, reserve_tokens=0, active_wall=0):
        self.ledger.check(reserve_tokens, active_wall)

    def acquire(self, task, arm='I', index=1, prefix=None, previous=None):
        if arm != 'I' or index != 1 or prefix is not None or previous is not None:
            raise ValueError('Pilot prohibits repair/continuation windows')
        if task.split != 'development' or task.tier != 'L2':
            raise ValueError('Pilot prohibits evaluation/other-tier acquisition')
        windows = sum(c.store.db.execute('SELECT COUNT(*) FROM m08_windows').fetchone()[0] for c in self.ledger.campaigns)
        if windows >= self.ledger.limits['windows']:
            raise PilotCeiling('Pilot window ceiling')
        return super().acquire(task, arm, index, prefix, previous)

    def branch(self, *args, **kwargs):
        raise ValueError('Pilot prohibits repair branches')

    def score(self):
        raise ValueError('Pilot prohibits hidden scoring')

    def run_all(self):
        raise ValueError('Pilot must follow its frozen A/B schedule')


def events_for(campaign, run):
    return [{'type': r['type'], 'payload': json.loads(r['payload_json'])} for r in campaign.store.db.execute(
        'SELECT * FROM events WHERE run_id=? ORDER BY sequence', (run,))]


def window_record(campaign, task, run, state):
    candidate = state['candidate']
    formed = candidate is not None and candidate['outcome'] in ('pass', 'fail') and state['status'] == 'finished'
    usage = state['usage']
    cost = {**usage, 'tokens': usage['input_tokens']+usage['output_tokens'], 'candidates': usage['candidate_attempts']}
    return {'run_id': run, 'condition': campaign.condition, 'formed': formed,
            'candidate_checkpoint': candidate['checkpoint'] if candidate else None,
            'public_verification_reached': candidate is not None,
            'public': candidate['outcome'] if candidate else None,
            'status': state['status'], 'termination': state['stop_reason'], 'cost': cost,
            'original_checkpoint': campaign.store.row(run)['initial_checkpoint'],
            'diagnostics': diagnostics(events_for(campaign, run), task.mutant)}


def audit_campaign(campaign, tasks, complete):
    db = campaign.store.db
    if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or list(db.execute('PRAGMA foreign_key_check')):
        raise ValueError('Pilot database integrity failed')
    if db.execute("SELECT COUNT(*) FROM evaluations WHERE split!='public'").fetchone()[0] or db.execute(
            "SELECT COUNT(*) FROM runs WHERE mode!='development'").fetchone()[0] or db.execute(
            'SELECT COUNT(*) FROM m08_scores').fetchone()[0] or db.execute('SELECT COUNT(*) FROM m08_retired_cohorts').fetchone()[0]:
        raise ValueError('Pilot evaluation/hidden isolation failed')
    request_count, projection_count = 0, 0
    for row in db.execute('SELECT * FROM runs ORDER BY created_utc'):
        task = tasks[row['task_id']]
        if row['task_hash'] != task.hash or json.loads(row['budget_json']) != Budget(**campaign.plan['window']).to_dict():
            raise ValueError('Task/window budget changed')
        events = events_for(campaign, row['id'])
        observations, calls, tokens, tools = [], 0, 0, 0
        controller = OrchestrationController('V1', task.view.editable_paths, 2)
        projected = PilotModel(campaign.plan['model'], campaign.identity, controller, campaign.tokenizer,
                               campaign.condition, campaign.plan['window']['max_edit_bytes'])
        for event in events:
            kind, payload = event['type'], event['payload']
            if kind == 'decision_started':
                calls += 1
            elif kind == 'model_request':
                raw = json.loads(campaign.artifacts.get(payload['request_artifact']))
                actual = raw['payload']
                state = DecisionState(1, 15-calls, 15-tools, 16000-tokens, 120)
                expected, metadata = projected.prompt(task.view, tuple(observations), state)
                if actual['messages'] != expected or raw['context'] != metadata:
                    raise ValueError('Feedback/prompt/budget replay mismatch')
                from ..interfaces import action_schema
                schema = action_schema('E0')
                schema['anyOf'] = [b for b in schema['anyOf'] if b['properties']['tool']['enum'][0] in controller.actions()]
                if actual != {'model': campaign.plan['model']['model'], 'messages': expected, 'stream': False,
                              'format': schema, 'options': {'temperature': 0, 'seed': 42, 'num_ctx': 4096, 'num_predict': 512},
                              'keep_alive': '5m', 'think': False}:
                    raise ValueError('Runner request settings differ from frozen M0.8B')
                request_count += 1
                projection_count += sum(project(o, campaign.condition, 8192) != o for o in observations[-4:])
            elif kind == 'model_call_completed':
                t = payload['telemetry']
                if t.get('identity') != campaign.identity or t.get('observed_digest') != campaign.identity['digest'] or t.get(
                        'observed_runtime_version') != campaign.identity['runtime_version']:
                    raise ValueError('Live Runner identity changed')
                tokens += (t.get('prompt_eval_count') or 0)+(t.get('eval_count') or 0)
            elif kind == 'control_action':
                controller = restore_controller(payload['after'])
                projected.controller = controller
            elif kind == 'action_completed':
                tools += 1
                observations.append(observation_from({'step': calls, 'action': payload['action'], 'result': payload['result']}))
        usage = json.loads(row['usage_json'])
        receipts = campaign.physical_cost({row['id']}, include_overhead=False)
        for name, actual in [('model_decisions', calls), ('tokens', tokens), ('tool_calls', tools+usage['candidate_attempts'])]:
            expected = usage['input_tokens']+usage['output_tokens'] if name == 'tokens' else usage[name]
            if actual != expected or actual != receipts[name]:
                raise ValueError('Call/token/tool accounting mismatch: '+name)
        candidate_events = sum(e['type'] == 'candidate_completed' for e in events)
        verification_events = sum(e['type'] == 'automatic_public_verification' for e in events)
        if candidate_events != usage['candidate_attempts'] or verification_events != candidate_events or candidate_events > 1:
            raise ValueError('Automatic single verification invariant failed')
    return {'passed': True, 'requests_replayed': request_count, 'projected_history_fields': projection_count,
            'hidden_scores': 0, 'evaluation_runs': 0, 'repair_windows': 0, 'complete': complete}


def execute_pilot(root, lock, destination):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    if lock.historical_audit:
        raise ValueError('Historical validation cannot authorize live inference')
    plan = lock.validate()
    tasks = lock.tasks()
    schedule_data = json.loads((lock.path.parent/'schedule.json').read_bytes())
    if schedule_data != schedule(tasks):
        raise ValueError('Pilot schedule changed')
    if destination.exists() or git(root, 'status', '--porcelain') or git(root, 'rev-parse', 'HEAD') != lock.commit:
        raise ValueError('Live pilot requires fresh state and clean frozen implementation commit')
    history_audit(root)
    identity = discover(plan['model'])
    if identity != lock.data['model']:
        raise ValueError('Runner identity mismatch prevents pilot')
    tokenizer = FrozenTokenizer.installed(plan['model'])
    if tokenizer.identity != lock.data['tokenizer_identity']:
        raise ValueError('Tokenizer identity mismatch prevents pilot')
    config = json.loads((root/'configs/m08c-preregistered.json').read_bytes())
    destination.mkdir(parents=True)
    save(destination/'started.json', {'utc': utc(), 'freeze_hash': lock.hash, 'implementation_commit': lock.commit,
                                   'schedule_hash': schedule_data['hash']})
    ledger, campaigns = Ledger(config['ceilings']), {}
    rows = {t.task_id: {'task_id': t.task_id, 'family': t.family, 'template': t.template, 'A': None, 'B': None} for t in tasks}
    task_map = {t.task_id: t for t in tasks}
    completed, interruption, error = [], None, None
    try:
        for arm in ('A', 'B'):
            campaigns[arm] = PilotCampaign(destination/arm, plan, tasks, arm, ledger, tokenizer=tokenizer,
                                           identity=identity, freeze=lock, frozen_schedule=schedule_data['hash'])
        for entry in schedule_data['entries']:
            if (destination/'STOP').exists():
                raise PilotCeiling('Manual pilot STOP')
            ledger.check()
            campaign, task = campaigns[entry['condition']], task_map[entry['task_id']]
            print(json.dumps({'event': 'window_start', **entry}), flush=True)
            run, original, state, artifact = campaign.acquire(task)
            if original != task.original_checkpoint:
                raise ValueError('Fresh original checkpoint differs from M0.8B public input')
            rows[task.task_id][entry['condition']] = window_record(campaign, task, run, state)
            completed.append({**entry, 'run_id': run, 'state_artifact': artifact})
            save(destination/f"window-{entry['ordinal']:02}.json", completed[-1])
            print(json.dumps({'event': 'window_done', 'ordinal': entry['ordinal'], 'condition': entry['condition'],
                              'task_id': task.task_id, 'formed': state['candidate'] is not None,
                              'termination': state['stop_reason'], 'tokens': state['usage']['input_tokens']+state['usage']['output_tokens']}), flush=True)
    except (Exception, KeyboardInterrupt) as exc:
        interruption, error = type(exc).__name__, str(exc)
    finally:
        for arm, campaign in campaigns.items():
            # Include an interrupted current window if it obtained a durable state artifact.
            for record in campaign.store.db.execute('SELECT * FROM m08_windows'):
                if record['state_artifact'] and rows[record['task_id']][arm] is None:
                    state = json.loads(campaign.artifacts.get(record['state_artifact']))
                    rows[record['task_id']][arm] = window_record(campaign, task_map[record['task_id']], record['run_id'], state)
        complete = interruption is None and len(completed) == 32
        audits, archives = {}, {}
        try:
            for arm, campaign in campaigns.items():
                try:
                    audits[arm] = audit_campaign(campaign, task_map, complete)
                except Exception as exc:
                    audits[arm] = {'passed': False, 'error': type(exc).__name__+': '+str(exc)}
                    complete = False
                    interruption = interruption or 'integrity_audit_failed'
                with campaign.store.db:
                    campaign.store.db.execute('UPDATE m08_campaigns SET state=?,sealed_utc=? WHERE id=?',
                                             ('sealed' if complete else 'incomplete', utc(), campaign.id))
                archives[arm] = export(campaign, destination/f'{arm}-research.zip')
            ordered = [rows[t.task_id] for t in tasks]
            cost = ledger.cost()
            result = {'version': 1, 'milestone': 'M0.8C', 'complete': complete, 'interruption': interruption,
                      'error': error, 'freeze_hash': lock.hash, 'implementation_commit': lock.commit,
                      'manifest_hash': lock.data['suite_manifest_hash'], 'schedule_hash': schedule_data['hash'],
                      'model_identity': identity, 'schedule_executed': completed, 'rows': ordered,
                      'analysis': analyze(ordered, config, complete), 'physical_cost': cost,
                      'execution_elapsed_seconds': ledger.elapsed(), 'audits': audits, 'exports': archives,
                      'evaluation_tasks_executed': 0, 'hidden_scores': 0, 'history': history_audit(root)}
            lock.validate()
            save(destination/'results.json', result)
            return result
        finally:
            for campaign in campaigns.values():
                campaign.close()
