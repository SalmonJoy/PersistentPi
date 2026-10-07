"""Strategy-facing interface: receives only a task view and public observations."""
class Runner:
    def __init__(self, model):
        self.model = model

    def next_action(self, task, observations, state, record_request=None):
        if getattr(self.model, 'request_receipts', False):
            return self.model.generate(task, tuple(observations), state, record_request)
        return self.model.generate(task, tuple(observations), state)
