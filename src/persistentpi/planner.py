"""No optimization in M0.1. This interface accepts public summaries only."""
def public_development_summary(observations):
    return {'public_observations': [o.to_dict() for o in observations]}


class NoOpPlanner:
    def propose(self, public_summary, incumbent_ref, search_budget):
        return None
