"""Fixture-owned actions, interpreted without task-specific solution logic."""
from dataclasses import dataclass

from ..contracts import ActionRequest, canonical


@dataclass(frozen=True)
class ScriptedReply:
    action: ActionRequest
    input_tokens: int
    output_tokens: int
    usage_kind: str = 'simulated'


class ScriptedModel:
    def __init__(self, steps):
        self.steps = tuple(steps)
        self.position = 0

    def generate(self, task, observations, state):
        if self.position >= len(self.steps):
            action = ActionRequest('finish', {})
        else:
            step = self.steps[self.position]
            requirement = step.get('requires_public_outcome')
            previous = [o.result.data.get('outcome') for o in observations if o.result.tool == 'run_public_tests']
            if requirement is not None and (not previous or previous[-1] != requirement):
                action = ActionRequest('finish', {'reason': 'script_condition_unmet'})
            else:
                action = ActionRequest.from_dict(step['action'])
            self.position += 1
        # Synthetic accounting excludes variable timings; it is not a tokenizer.
        return ScriptedReply(action, max(1, (len(canonical(task)) + 3) // 4) + 32 * len(observations),
                             max(1, (len(canonical(action)) + 3) // 4))
