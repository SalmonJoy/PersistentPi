"""Protocol 0.4: deterministic lifecycle, not semantic coding assistance."""
from dataclasses import replace
import time
import uuid

from .contracts import ActionRequest, Observation, canonical, digest
from .control import Controller, ControlSupervisor
from .interfaces import authorize_interface
from .orchestration_suite import suite_manifest
from .supervisor import Supervisor

VERSIONS = {'V0': 'explicit-C3-1', 'V1': 'automatic-edit-verify-1'}


class OrchestrationController(Controller):
    def __init__(self, condition, sources, read_budget=2):
        if condition not in VERSIONS:
            raise ValueError('Unknown orchestration condition')
        self.condition = condition
        super().__init__('C3', sources, read_budget)

    def actions(self):
        actions = super().actions()
        return tuple(a for a in actions if a != 'run_public_tests') if self.condition == 'V1' else actions


class OrchestrationSupervisor(ControlSupervisor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.protocol != '0.4':
            raise ValueError('Candidate orchestration requires protocol 0.4')
        self.condition = self.controller.condition
        self.latest_edit = None
        self.pending_automatic = None
        self.completed_sources = set()
        self.terminal = None
        self.usage['candidate_attempts'] = 0

    def perform(self, action, call_id):
        if action.tool == 'run_public_tests' and self.condition == 'V0':
            return self.verify_candidate(action, call_id, automatic=False)
        if action.tool == 'edit_file' and self.condition == 'V1':
            # run() has already charged the proposed EDIT tool call. Reserve one
            # additional call before writing so its verification cannot be starved.
            if self.state().remaining_tool_calls < 1:
                raise ValueError('Automatic verification tool reservation exhausted')
        result = super().perform(action, call_id)
        if action.tool == 'edit_file' and result.ok:
            self.latest_edit = {'source_call_id': call_id, 'step': self.usage['model_decisions']}
            self.store.event(self.run_id, 'supervisor', 'candidate_edit_accepted', self.latest_edit)
            if self.condition == 'V1':
                self.pending_automatic = dict(self.latest_edit)
        return result

    def verify_candidate(self, action, call_id, automatic):
        authorize_interface(action, self.interface['edit_primitive'])
        if action.tool != 'run_public_tests' or not self.latest_edit:
            raise ValueError('Verification requires an accepted candidate edit')
        source = self.latest_edit['source_call_id']
        if source in self.completed_sources:
            raise ValueError('Candidate edit already verified')
        if self.state().remaining_attempts <= 0:
            raise ValueError('Candidate-attempt budget exhausted')
        checkpoint = self.artifacts.checkpoint(self.workspace, self.selected.hash)
        candidate = {'source_call_id': source, 'call_id': call_id, 'automatic': automatic,
                     'number': self.usage['attempts'] + 1, 'checkpoint': checkpoint.to_dict()}
        self.store.event(self.run_id, 'supervisor', 'candidate_checkpoint', candidate)
        if automatic:
            self.store.event(self.run_id, 'control_plane', 'automatic_public_verification', candidate)
        self.store.event(self.run_id, 'supervisor', 'candidate_attempt_started', candidate)
        # Both conditions use exactly the same immutable fixed-purpose verifier.
        result = (Supervisor.perform(self, action, call_id) if automatic
                  else ControlSupervisor.perform(self, action, call_id))
        if result.checkpoint.hash != checkpoint.hash:
            raise RuntimeError('Workspace changed during candidate submission')
        self.completed_sources.add(source)
        self.usage['candidate_attempts'] = self.usage['attempts']
        self.persist_usage()
        self.store.event(self.run_id, 'supervisor', 'candidate_attempt_completed',
                         {**candidate, 'outcome': result.data['outcome']})
        return result

    def flush_funnel(self, reason, evidence=None):
        super().flush_funnel(reason, evidence)
        if not self.pending_automatic:
            return
        pending, self.pending_automatic = self.pending_automatic, None
        if self.cancelled() or self.state().remaining_wall_seconds <= 0:
            self.store.event(self.run_id, 'supervisor', 'candidate_unverified',
                {**pending, 'reason': 'manual_stop' if self.cancelled() else 'wall_budget_exhausted'})
            return
        action = ActionRequest('run_public_tests', {})
        call_id = str(uuid.uuid4())
        request = self.artifacts.put(canonical(action), 'action_request', 'public')
        self.usage['tool_calls'] += 1
        self.persist_usage()
        self.store.event(self.run_id, 'supervisor', 'action_started',
                         {'call_id': call_id, 'action_artifact': request, 'origin': 'controller'})
        began = time.monotonic()
        result = self.verify_candidate(action, call_id, automatic=True)
        artifact = self.artifacts.put(canonical(result), 'action_result', 'public')
        self.store.event(self.run_id, 'supervisor', 'action_completed',
                         {'call_id': call_id, 'ok': result.ok, 'result_artifact': artifact,
                          'origin': 'controller', 'duration_seconds': time.monotonic() - began, 'usage': self.usage})
        self.observations.append(Observation(pending['step'], action, result))
        outcome = result.data['outcome']
        if outcome == 'pass':
            self.terminal = 'public_success'
        elif outcome not in ('fail', 'stopped'):
            self.terminal = 'public_infrastructure_' + outcome
        elif outcome == 'stopped':
            self.terminal = 'manual_stop'

    def exhausted(self):
        return self.terminal or super().exhausted()

    def finish(self, status, reason):
        if reason.startswith('public_infrastructure_'):
            status = 'interrupted'
        elif reason == 'manual_stop':
            status = 'stopped'
        super().finish(status, reason)


def configured(base, condition, phase, suite, plan, identity, candidate_budget=1):
    if condition not in VERSIONS or phase not in ('calibration', 'primary', 'scaling'):
        raise ValueError('Unknown condition/cohort')
    if condition == 'V0' and candidate_budget != 1:
        raise ValueError('V0 is only a one-candidate baseline')
    if phase in ('calibration', 'primary') and candidate_budget != 1:
        raise ValueError('Primary/calibration cohorts require candidate budget one')
    if candidate_budget not in plan['candidate_budgets'] or base.manifest['protocol_version'] != '0.4':
        raise ValueError('Invalid candidate protocol/budget')
    if suite_manifest(base.tasks) != suite or plan['read_budget'] != 2:
        raise ValueError('Frozen suite or inspection policy changed')
    task_ids = suite['calibration' if phase == 'calibration' else 'evaluation']
    tasks = tuple(t for t in base.tasks if t.view.task_id in task_ids)
    model = {**base.manifest['model'], 'orchestration_condition': condition, 'read_budget': plan['read_budget'],
             'thinking_policy': 'explicit-false-1', 'think': False,
             'expected_digest': identity['digest'], 'expected_runtime_version': identity['runtime_version']}
    scaffold = {'scaffold_id': 'm07-' + condition, 'parent_scaffold_id': 'm06-C3',
                'scaffold_version': VERSIONS[condition], 'scaffold_hash': digest({
                    'parent': base.manifest['scaffold'], 'condition': condition, 'plan_hash': digest(plan),
                    'orchestration': base.manifest['code_hashes']['src/persistentpi/orchestration.py'],
                    'C3': base.manifest['code_hashes']['src/persistentpi/control.py']})}
    manifest = {**base.manifest, 'model': model, 'scaffold': scaffold,
                'attempt_semantics': 'accepted-edit-checkpoint-public-verification-1',
                'candidate_attempt_budget': candidate_budget, 'attempt_budgets': [candidate_budget],
                'm07_condition': condition, 'm07_phase': phase, 'm07_plan_hash': digest(plan),
                'm07_suite_hash': digest(suite),
                'tasks': [t for t in base.manifest['tasks'] if t['task_id'] in task_ids]}
    return replace(base, manifest=manifest, tasks=tasks, attempt_budgets=(candidate_budget,))
