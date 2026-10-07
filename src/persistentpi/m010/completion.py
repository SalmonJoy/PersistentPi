"""Completion meaning must be documented; unfamiliar literal names are not guessed."""
from .config import DEFAULT


def complete(response, evidence=None):
    if response.get('done') is not True:
        raise ValueError('M010_INCOMPLETE')
    reason = response.get('done_reason')
    if not isinstance(reason, str) or not reason:
        raise ValueError('M010_COMPLETION_REASON_MISSING')
    if reason in ('length', 'max_tokens', 'output_limit', 'token_limit', 'truncated'):
        raise ValueError('M010_TRUNCATED')
    catalog = evidence if evidence is not None else DEFAULT['completion']
    item = catalog.get(reason)
    if (not isinstance(item, dict) or item.get('meaning') not in ('complete', 'truncated')
            or not isinstance(item.get('source'), str) or not item['source']):
        raise ValueError('M010_COMPLETION_UNESTABLISHED')
    if item['meaning'] == 'truncated':
        raise ValueError('M010_TRUNCATED')
    return {'done_reason': reason, 'documented_meaning': item['meaning'], 'source': item['source']}
