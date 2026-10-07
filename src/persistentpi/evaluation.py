"""Research-only final evaluator. No Runner or Planner callback exists here."""
from ._verification import verify


class HiddenEvaluator:
    def __init__(self, artifacts, run_id, tests, test_id, test_hash, execution_policy='reviewed_python'):
        self.artifacts, self.run_id = artifacts, run_id
        self.tests, self.test_id, self.test_hash = tests, test_id, test_hash
        self.execution_policy = execution_policy

    def evaluate(self, checkpoint, timeout, output_limit):
        if self.artifacts.store.row(self.run_id)['status'] != 'finished':
            raise ValueError('Hidden evaluation requires a terminated Runner')
        return verify(self.artifacts, self.run_id, checkpoint, self.tests,
                      self.test_id, self.test_hash, 'hidden', timeout, output_limit, lambda: False, self.execution_policy)
