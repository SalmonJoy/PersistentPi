"""Research control plane: trial identity, lifecycle and private final scoring."""
import json
import os
from pathlib import Path
import time
import uuid
from dataclasses import replace

from ._verification import save_evaluation
from .adapters.platform import owner_state, process_identity
from .adapters.scripted import ScriptedModel
from .artifacts import Artifacts, atomic_write, file_map
from .config import tree_hash
from .contracts import Budget, canonical, digest
from .evaluation import HiddenEvaluator
from .runner import Runner
from .supervisor import Supervisor
from .telemetry import Store, utc
from .verification import PublicVerifier


class ExperimentManager:
    def __init__(self, state, model_client=None):
        self.store = Store(Path(state))
        self.artifacts = Artifacts(self.store)
        self.model_client = model_client

    def close(self):
        self.store.close()

    def reserve(self, resolved):
        if resolved.manifest['protocol_version'] == '0.5':
            raise ValueError('Protocol 0.5 requires the M0.8 campaign manager and frozen preregistration')
        if (resolved.manifest['protocol_version'] == '0.4' and
                resolved.manifest['model'].get('orchestration_condition') not in ('V0', 'V1')):
            raise ValueError('Protocol 0.4 requires a configured candidate-orchestration condition')
        if resolved.manifest['model'].get('backend') == 'ollama':
            from .adapters.ollama import discover
            model = resolved.manifest['model']
            identity = discover(model, self.model_client)
            resolved = replace(resolved, manifest={**resolved.manifest, 'model': {**model, 'identity': identity}})
        manifest_hash = self.store.manifest('experiment', resolved.manifest)
        authored = self.artifacts.put(resolved.authored, 'authored_config', 'research')
        experiment_id = str(uuid.uuid4())
        scaffold = resolved.manifest['scaffold']
        planned = []
        for task in resolved.tasks:
            for count in resolved.attempt_budgets:
                budget = Budget(max_attempts=count, **resolved.budget_config)
                key = digest({'manifest': manifest_hash, 'task': task.hash, 'budget': budget.to_dict(),
                              'seed': resolved.seed, 'replicate': resolved.replicate})
                planned.append((str(uuid.uuid4()), task, budget, key))
        self.store.db.execute('BEGIN IMMEDIATE')
        try:
            if resolved.mode == 'formal':
                for _, _, _, key in planned:
                    if self.store.db.execute("SELECT 1 FROM runs WHERE trial_key=? AND mode='formal'", (key,)).fetchone():
                        raise ValueError('Duplicate formal trial; choose an explicit new replicate')
            self.store.db.execute('INSERT INTO experiments VALUES(?,?,?,?)',
                                  (experiment_id, manifest_hash, resolved.manifest['protocol_version'], utc()))
            columns = ('id','experiment_id','trial_key','mode','task_id','task_hash','fixture_version',
                       'protocol_version','scaffold_id','scaffold_hash','parent_scaffold_id','scaffold_version',
                       'seed','replicate','manifest_hash','git_commit','dirty','status','budget_json',
                       'usage_json','platform_json','owner_pid','owner_identity','created_utc')
            for run_id, task, budget, key in planned:
                values = (run_id, experiment_id, key, resolved.mode, task.view.task_id, task.hash,
                          task.view.fixture_version, resolved.manifest['protocol_version'], scaffold['scaffold_id'],
                          scaffold['scaffold_hash'], scaffold['parent_scaffold_id'], scaffold['scaffold_version'],
                          resolved.seed, resolved.replicate, manifest_hash, resolved.manifest['git']['commit'],
                          int(resolved.manifest['git']['dirty']), 'queued', canonical(budget).decode(), '{}',
                          canonical(resolved.manifest['execution_profile']).decode(), os.getpid(),
                          process_identity(os.getpid()), utc())
                self.store.db.execute('INSERT INTO runs(' + ','.join(columns) + ') VALUES(' +
                                      ','.join('?' for _ in columns) + ')', values)
            self.store.db.commit()
        except BaseException:
            self.store.db.rollback()
            raise
        for run_id, _, _, _ in planned:
            self.store.event(run_id, 'control_plane', 'trial_reserved',
                             {'experiment_id': experiment_id, 'manifest_hash': manifest_hash,
                              'authored_config_artifact': authored})
        return planned

    def execute(self, run_id, task, budget, runner=None):
        began = time.monotonic()
        self.store.update_run(run_id, status='running')
        self.store.event(run_id, 'control_plane', 'trial_started', {})
        try:
            if tree_hash(task.source) != task.source_hash:
                raise ValueError('Task source changed after manifest resolution')
            workspace = self.store.state / 'workspaces' / run_id
            workspace.mkdir(parents=True)
            for name, raw in file_map(task.source).items():
                atomic_write(workspace / name, raw)
            for name, raw in file_map(task.public_tests).items():
                atomic_write(workspace / 'public_tests' / name, raw)
            if sum(map(len, file_map(workspace).values())) > budget.max_workspace_bytes:
                raise ValueError('Initial workspace exceeds configured byte budget')
            initial = self.artifacts.checkpoint(workspace)
            self.store.update_run(run_id, initial_checkpoint=initial.hash, selected_checkpoint=initial.hash)
            self.store.event(run_id, 'supervisor', 'initial_checkpoint', {'checkpoint': initial.to_dict()})
            public = PublicVerifier(self.artifacts, run_id, task.public_tests,
                                    task.view.public_test_id, task.public_hash, task.execution_policy)
            supervisor = Supervisor(self.store, self.artifacts, run_id, workspace, task.view, budget, public)
            if supervisor.protocol == '0.4':
                from .orchestration import OrchestrationController, OrchestrationSupervisor
                manifest = json.loads(self.store.db.execute('SELECT json FROM manifests WHERE hash=?',
                    (self.store.row(run_id)['manifest_hash'],)).fetchone()[0])
                model = manifest['model']
                controller = OrchestrationController(model['orchestration_condition'],
                    task.view.editable_paths, model['read_budget'])
                supervisor = OrchestrationSupervisor(self.store, self.artifacts, run_id, workspace,
                    task.view, budget, public, controller=controller)
            if runner is None:
                manifest_hash = self.store.row(run_id)['manifest_hash']
                manifest = json.loads(self.store.db.execute('SELECT json FROM manifests WHERE hash=?', (manifest_hash,)).fetchone()[0])
                model = manifest['model']
                if model.get('backend') == 'ollama':
                    from .adapters.ollama import OllamaModel
                    if task.execution_policy != 'bounded-python-1':
                        raise ValueError('Live generation requires bounded Python execution')
                    if 'orchestration_condition' in model:
                        from .control import ControlModel
                        runner = Runner(ControlModel(model, model['identity'], controller, self.model_client))
                    elif 'control_policy' in model:
                        from .control import Controller, ControlModel, ControlSupervisor
                        controller = Controller(model['control_policy'], task.view.editable_paths,
                                                model['read_budget'])
                        supervisor = ControlSupervisor(self.store, self.artifacts, run_id, workspace,
                            task.view, budget, public, controller=controller)
                        runner = Runner(ControlModel(model, model['identity'], controller, self.model_client))
                    elif 'diagnostic_condition' in model:
                        from .diagnostic import DiagnosticModel, DiagnosticSupervisor, preload
                        supervisor = DiagnosticSupervisor(self.store, self.artifacts, run_id, workspace,
                            task.view, budget, public, condition=model['diagnostic_condition'])
                        files = preload(supervisor)
                        runner = Runner(DiagnosticModel(model, model['identity'], files, self.model_client))
                    else:
                        runner = Runner(OllamaModel(model, model['identity'], self.model_client))
                else:
                    runner = Runner(ScriptedModel(task.steps))
            supervisor.run(runner)
            row = self.store.row(run_id)
            if row['status'] == 'finished':
                self.store.event(run_id, 'hidden_evaluator', 'evaluation_started',
                                 {'checkpoint': row['selected_checkpoint'], 'test_hash': task.hidden_hash})
                self.store.update_run(run_id, evaluation_status='running')
                evaluator = HiddenEvaluator(self.artifacts, run_id, task.hidden_tests,
                                            task.view.task_id + ':hidden:v1', task.hidden_hash, task.execution_policy)
                result = evaluator.evaluate(supervisor.selected, budget.test_timeout_seconds, budget.max_output_bytes)
                record = save_evaluation(self.store, self.artifacts, run_id, None,
                                         supervisor.selected, task.hidden_hash, result)
                self.store.update_run(run_id, evaluation_status=result.outcome, benchmark_score=result.score)
                self.store.event(run_id, 'hidden_evaluator', 'evaluation_completed', {'result': record})
                if row['protocol_version'] in ('0.3', '0.4'):
                    # Attribute final hidden measurement only to submissions of the selected checkpoint.
                    submissions = [json.loads(e['payload_json']) for e in self.store.db.execute(
                        "SELECT payload_json FROM events WHERE run_id=? AND type='verification_started' ORDER BY sequence", (run_id,))]
                    selected_calls = [s['call_id'] for s in submissions if s['checkpoint']['hash'] == row['selected_checkpoint']]
                    self.store.event(run_id, 'hidden_evaluator', 'hidden_funnel_result',
                        {'call_id': selected_calls[-1] if selected_calls else None,
                         'hidden_evaluation_passed': result.outcome == 'pass',
                         'checkpoint': row['selected_checkpoint'], 'outcome': result.outcome})
                if row['protocol_version'] == '0.2' and result.outcome == 'fail':
                    self.store.event(run_id, 'hidden_evaluator', 'failure_classified',
                                     {'taxonomy_version': '0.2', 'category': 'hidden_test_failure',
                                      'evidence': {'checkpoint': supervisor.selected.hash}})
        except (Exception, KeyboardInterrupt) as exc:
            self.store.update_run(run_id, status='interrupted', stop_reason='control_plane_error',
                                  evaluation_status='incomplete', benchmark_score=None, ended_utc=utc())
            self.store.event(run_id, 'control_plane', 'trial_interrupted',
                             {'exception_type': type(exc).__name__, 'message': str(exc)[:2048]})
        self.store.event(run_id, 'control_plane', 'trial_completed',
                         {'end_to_end_seconds': time.monotonic() - began})
        return self.store.row(run_id)

    def run(self, resolved):
        return [self.execute(run_id, task, budget) for run_id, task, budget, _ in self.reserve(resolved)]

    def status(self, run_id=None):
        rows = list(self.store.db.execute('SELECT * FROM runs ORDER BY created_utc,id'))
        for row in rows:
            unfinished = row['status'] in ('queued', 'running') or (
                row['status'] == 'finished' and row['evaluation_status'] in ('pending', 'running'))
            if row['protocol_version']=='0.5':
                # Finished acquisition windows deliberately await campaign-level
                # sealing/scoring; they are not abandoned legacy private trials.
                unfinished = row['status'] in ('queued','running')
            if unfinished and owner_state(row['owner_pid'], row['owner_identity']) == 'dead':
                self.store.update_run(row['id'], status='interrupted', stop_reason='owner_process_lost',
                                      evaluation_status='incomplete', benchmark_score=None, ended_utc=utc())
                self.store.event(row['id'], 'control_plane', 'owner_lost',
                                 {'previous_status': row['status'], 'automatic_resume': False})
        if run_id:
            return [self.store.row(run_id)]
        return [dict(row) for row in self.store.db.execute('SELECT * FROM runs ORDER BY created_utc,id')]


def summary(row):
    usage, budget = json.loads(row['usage_json']), json.loads(row['budget_json'])
    return {'experiment_id': row['experiment_id'], 'run_id': row['id'], 'task': row['task_id'],
            'attempt_budget': budget['max_attempts'], 'attempts': usage.get('attempts', 0),
            'status': row['status'], 'stop_reason': row['stop_reason'],
            'hidden_outcome': row['evaluation_status'], 'score': row['benchmark_score']}
