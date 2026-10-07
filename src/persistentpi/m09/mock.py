"""Synthetic outcome fixtures: no model inference and no claims of measured success."""
from dataclasses import replace

from ..contracts import digest
from .analysis import Result
from .planner import FakePlanner
from .spec import compile_scaffold, references


class FakeEvaluator:
    offline = True

    def __init__(self, scenario='A'):
        self.scenario, self.calls = scenario, []
        self.reference_ids = {compile_scaffold(s).scaffold_id for s in references().values()}

    def evaluate(self, configuration, task, cohort_hash, job_id, store):
        self.calls.append((configuration.scaffold_id, task.task_id, cohort_hash))
        if self.scenario == 'D':
            raise RuntimeError('Synthetic infrastructure/identity stop')
        generated = configuration.scaffold_id not in self.reference_ids
        qualification = task.task_id.startswith('q')
        index = int(digest(task.task_id)[:8], 16) % 8
        success = generated or index == 0
        if qualification and self.scenario == 'C':
            success = not generated or index < 3
        return Result(configuration.scaffold_id, cohort_hash, task.task_id, task.task_hash, task.family,
                      task.template, True, 'pass' if success else 'fail', 2, 100, 50, .01, .02, job_id)


def proposals(scenario='A'):
    def valid(index):
        def build(bundle, archive, remaining):
            spec = replace(bundle['parent'].spec, system_text=bundle['parent'].spec.system_text + f'\nGeneral fixture policy {index}.')
            return {'parents': [bundle['parent'].scaffold_id], 'scaffold': spec.to_dict(),
                    'mutation': 'Generic offline prompt fixture', 'rationale': 'Tests scheduling only',
                    'targeted_categories': ['NO_OP']}
        return build
    if scenario == 'B':
        def duplicate(bundle, archive, remaining):
            return {'parents': [bundle['parent'].scaffold_id], 'scaffold': bundle['parent'].spec.to_dict(),
                    'mutation': 'Duplicate', 'rationale': 'Fixture', 'targeted_categories': []}
        def oversized(bundle, archive, remaining):
            value = duplicate(bundle, archive, remaining)
            value['scaffold']['system_text'] = 'x' * 4097
            return value
        return FakePlanner(['broken', duplicate, '```json\n{}\n```', '{}', duplicate,
                            '{"code":"run"}', '[]', oversized])
    return FakePlanner([valid(i) for i in range(8)])
