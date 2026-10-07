"""Deterministic protocol smoke checks before any candidate evaluation."""
from ..contracts import TaskView, DecisionState
from .render import controller_for, wire_request


def validate_candidate(configuration, runner):
    configuration.spec.validate()
    view = TaskView('offline-smoke', 'Return the input unchanged.', ('src/solution.py',),
                    ('src/solution.py', 'public_tests/cases.json'), 'offline-smoke:public', 'fixture')
    controller = controller_for(configuration, view.editable_paths)
    phases = []
    for phase in ('INSPECT', 'ACT'):
        if controller.phase is not None:
            controller.phase = phase
        payload, _ = wire_request(configuration, view, (), DecisionState(1, 15, 15, 16000, 120),
                                  controller, runner, 'def solve(value):\n    return value\n', ())
        if payload['options']['num_ctx'] != 4096 or payload['options']['num_predict'] > 1024:
            raise ValueError('Smoke resource contract changed')
        if 'run_public_tests' in controller.actions():
            raise ValueError('Model-directed verification is not authorized')
        phases.append(phase)
    return {'passed': True, 'version': 'offline-smoke-1', 'phases': phases, 'inference': False}
