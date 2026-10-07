"""M0.6 control facts only; no inspection of source semantics or patch generation."""
from dataclasses import replace
import json

from .adapters.ollama import OllamaModel
from .config import tree_hash
from .contracts import canonical, digest
from .control_suite import suite_manifest
from .interfaces import action_schema, registry
from .supervisor import Supervisor

VERSIONS = {'C0': 'autonomous-1', 'C1': 'visible-no-redundant-1',
            'C2': 'successful-read-budget-1', 'C3': 'inspect-act-1'}
ALL_ACTIONS = ('read_file', 'edit_file', 'run_public_tests', 'finish')
REDUNDANT = 'File already observed; choose another action.'


class Controller:
    def __init__(self, policy, sources, read_budget=2):
        if policy not in VERSIONS or type(read_budget) is not int or read_budget <= 0:
            raise ValueError('Invalid control policy')
        self.policy, self.sources, self.read_budget = policy, tuple(sorted(sources)), read_budget
        self.phase = 'INSPECT' if policy == 'C3' else None
        self.epoch = 0
        self.reads = 0
        self.observed = {}
        self.visible = set()
        self.accepted_edits = 0

    def actions(self):
        if self.policy == 'C3' and self.phase == 'INSPECT':
            return ('read_file', 'finish')
        restricted = self.policy == 'C3' or (self.policy == 'C2' and self.reads >= self.read_budget)
        if restricted:
            return ('edit_file', 'run_public_tests', 'finish') if self.accepted_edits else ('edit_file', 'finish')
        return ALL_ACTIONS

    def rejection(self, action):
        if action.tool not in self.actions():
            return 'Action unavailable in current control state.'
        path = action.arguments.get('path')
        if (self.policy == 'C1' and action.tool == 'read_file'
                and self.observed.get(path) == self.epoch and path in self.visible):
            return REDUNDANT
        return None

    def observe(self, action, successful):
        if not successful:
            return
        if action.tool == 'read_file':
            self.reads += 1
            self.observed[action.arguments['path']] = self.epoch
            self.visible.add(action.arguments['path'])
            if (self.policy == 'C3' and self.phase == 'INSPECT'
                    and (self.reads >= self.read_budget or set(self.sources) <= set(self.observed))):
                self.phase = 'ACT'
        elif action.tool == 'edit_file':
            self.accepted_edits += 1
            self.epoch += 1
            self.visible.clear()

    def context(self, included):
        self.visible = {o['action']['arguments']['path'] for o in included
                        if o['action']['tool'] == 'read_file' and o['result']['ok']
                        and self.observed.get(o['action']['arguments']['path']) == self.epoch}
        # Old successful observations after an edit are not evidence of this epoch.
        # The model includes step numbers; read steps are tracked by its adapter.

    def snapshot(self):
        return {'version': VERSIONS[self.policy], 'policy': self.policy, 'sources': list(self.sources),
                'read_budget': self.read_budget, 'phase': self.phase, 'epoch': self.epoch,
                'successful_reads': self.reads, 'observed_epochs': dict(self.observed),
                'visible_paths': sorted(self.visible), 'accepted_edits': self.accepted_edits,
                'available_actions': list(self.actions())}

    @classmethod
    def restore(cls, value):
        controller = cls(value['policy'], value['sources'], value['read_budget'])
        if value['version'] != VERSIONS[controller.policy]:
            raise ValueError('Controller version changed')
        controller.phase, controller.epoch = value['phase'], value['epoch']
        controller.reads = value['successful_reads']
        controller.observed = dict(value['observed_epochs'])
        controller.visible = set(value['visible_paths'])
        controller.accepted_edits = value['accepted_edits']
        if controller.snapshot() != value:
            raise ValueError('Inconsistent saved action set')
        return controller


class ControlModel(OllamaModel):
    def __init__(self, config, identity, controller, client=None):
        super().__init__(config, identity, client)
        self.controller = controller

    def prompt(self, task, observations, state):
        messages, metadata = super().prompt(task, observations, state)
        c = self.controller
        if c.policy == 'C0':
            return messages, metadata
        public = json.loads(messages[1]['content'])
        public['tools'] = {k: v for k, v in registry('E0').items() if k in c.actions()}
        public['control'] = {'policy': c.policy, 'version': VERSIONS[c.policy], 'phase': c.phase,
                             'successful_reads': c.reads, 'inspection_budget': c.read_budget,
                             'available_actions': list(c.actions())}
        messages[0]['content'] += ('\nThe control state and available_actions below override the general action listing. '
                                   'finish means GIVE_UP. Choose only an available action.')
        while True:
            messages[1]['content'] = canonical(public).decode()
            if len(canonical(messages)) <= self.config['context']['max_bytes']:
                break
            if not public['observations']:
                raise ValueError('Control context exceeds prompt byte bound')
            public['observations'].pop(0)
        # A successful read only remains visible if no successful edit follows it
        # in the full observation history. Context eviction permits neutral refresh.
        latest_edit = max((o.step for o in observations
                           if o.action.tool == 'edit_file' and o.result.ok), default=-1)
        c.context([o for o in public['observations'] if o['step'] > latest_edit])
        metadata.update(prompt_version='m06-' + c.policy + '-' + VERSIONS[c.policy],
                        prompt_hash=digest(messages), prompt_bytes=len(canonical(messages)),
                        observations_included=len(public['observations']),
                        observations_dropped=len(observations) - len(public['observations']),
                        control=c.snapshot())
        return messages, metadata

    def response_format(self, protocol, edit):
        if self.controller.policy == 'C0':
            return super().response_format(protocol, edit)
        schema = action_schema(edit)
        schema['anyOf'] = [b for b in schema['anyOf']
                           if b['properties']['tool']['enum'][0] in self.controller.actions()]
        return schema


class ControlSupervisor(Supervisor):
    def __init__(self, *args, controller, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.workspace_state = tree_hash(self.workspace) if controller.policy == 'C1' else None

    def perform(self, action, call_id):
        before = self.controller.snapshot()
        event = {'call_id': call_id, 'tool': action.tool, 'path': action.arguments.get('path'),
                 'before': before, 'accepted': False, 'rejection': None}
        try:
            # Validate normal tool contracts and path authority before control gating.
            from .interfaces import authorize_interface
            authorize_interface(action, self.interface['edit_primitive'])
            if action.tool in ('read_file', 'edit_file'):
                self.path(action.arguments['path'], write=action.tool == 'edit_file')
            if self.controller.policy == 'C1':
                current = tree_hash(self.workspace)
                if current != self.workspace_state:
                    self.controller.epoch += 1
                    self.controller.visible.clear()
                    self.workspace_state = current
                event['before'] = self.controller.snapshot()
            reason = self.controller.rejection(action)
            if reason:
                event['rejection'] = 'redundant_read' if reason == REDUNDANT else 'unavailable_action'
                raise ValueError(reason)
            result = super().perform(action, call_id)
            event['accepted'] = not bool(result.error)
            self.controller.observe(action, result.ok)
            if self.controller.policy == 'C1' and action.tool == 'edit_file' and result.ok:
                self.workspace_state = tree_hash(self.workspace)
            return result
        except (ValueError, OSError, UnicodeError) as exc:
            event['error'] = str(exc)[:300]
            raise
        finally:
            event['after'] = self.controller.snapshot()
            self.store.event(self.run_id, 'supervisor', 'control_action', event)

    def run(self, runner):
        self.store.event(self.run_id, 'supervisor', 'control_initialized', self.controller.snapshot())
        row = super().run(runner)
        self.store.event(self.run_id, 'supervisor', 'control_final', self.controller.snapshot())
        return row


def configured(base, tag, policy, phase, suite, plan, entry):
    if policy not in VERSIONS or phase not in ('calibration', 'evaluation'):
        raise ValueError('Unknown control condition/cohort')
    if suite_manifest(base.tasks) != suite:
        raise ValueError('Frozen suite changed')
    if base.attempt_budgets != (1,) or plan['read_budget'] != 2 or plan['output_ceiling'] != 512:
        raise ValueError('Preregistered limits changed')
    tasks = tuple(t for t in base.tasks if t.view.task_id in suite[phase])
    model = {**base.manifest['model'], 'model': tag, 'control_policy': policy,
             'read_budget': plan['read_budget'], 'thinking_policy': 'explicit-false-1', 'think': False,
             'expected_digest': entry['identity']['digest'],
             'expected_runtime_version': entry['identity']['runtime_version']}
    scaffold = {'scaffold_id': 'm06-' + policy, 'scaffold_version': VERSIONS[policy],
                'parent_scaffold_id': base.manifest['scaffold']['scaffold_id'],
                'scaffold_hash': digest({'parent': base.manifest['scaffold'], 'policy': policy,
                    'version': VERSIONS[policy], 'plan_hash': digest(plan),
                    'controller_code': base.manifest['code_hashes']['src/persistentpi/control.py']})}
    manifest = {**base.manifest, 'model': model, 'scaffold': scaffold,
                'm06_policy': policy, 'm06_phase': phase, 'm06_model': tag,
                'm06_plan_hash': digest(plan), 'm06_suite_hash': digest(suite),
                'tasks': [t for t in base.manifest['tasks'] if t['task_id'] in suite[phase]]}
    return replace(base, manifest=manifest, tasks=tasks)
