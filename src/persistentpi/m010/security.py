"""Submission-key leakage and offline access instrumentation."""
from .config import DEFAULT


def leakage(value):
    found = set()
    prohibited = set(DEFAULT['prohibited_fields'])
    def visit(item):
        if isinstance(item, dict):
            for key, val in item.items():
                if isinstance(key, str) and key in prohibited:
                    found.add(key)
                if key == 'field' and isinstance(val, str) and val in prohibited:
                    found.add(val)
                # Authored text is inert; words inside prose do not become fields.
                visit(val)
        elif isinstance(item, list):
            for val in item:
                visit(val)
    visit(value)
    return sorted(found)
