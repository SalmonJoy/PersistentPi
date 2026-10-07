"""Public-only verification; no private task or hidden evaluation input."""
from ._verification import verify


class PublicVerifier:
    def __init__(self, artifacts, run_id, tests, test_id, test_hash, execution_policy='reviewed_python'):
        self.artifacts, self.run_id = artifacts, run_id
        self.tests, self.test_id, self.test_hash = tests, test_id, test_hash
        self.execution_policy = execution_policy

    def check(self, checkpoint, timeout, output_limit, cancelled):
        return verify(self.artifacts, self.run_id, checkpoint, self.tests,
                      self.test_id, self.test_hash, 'public', timeout, output_limit, cancelled, self.execution_policy)
