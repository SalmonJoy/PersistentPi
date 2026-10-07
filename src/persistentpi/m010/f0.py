"""Historical control: exact original functions, no Runner calls."""
import hashlib
import json
import zipfile

from ..m09.disclosure import SYSTEM
from ..m09.manager import proposal_contract
from ..m09.spec import parse_proposal
from .config import ROOT
from .frozen import verify_anchors


def parse_f0(raw, allowed_parents):
    verify_anchors()
    return parse_proposal(raw, allowed_parents)


def historical_parity():
    rows = json.loads((ROOT / 'docs/research-records/m09cf/proposals.json').read_bytes())['rows']
    if len(rows) != 8:
        raise ValueError('F0_PARITY_EVIDENCE')
    registry_ids = [
        '3523ba5db8fee37ed9465947970b20ef61a336ee08527c3c9abdf9cda2cf8413',
        '816fe91c71baad3187fa4168f2d5f450c512a14477843d642f0d435992476640']
    output = []
    with zipfile.ZipFile(ROOT / 'docs/research-records/m09c-primary-no-finalist/post-search-export.zip') as archive:
        for row in sorted(rows, key=lambda r: (r['round'], r['slot'])):
            raw = archive.read('artifacts/' + row['response_hash'])
            if hashlib.sha256(raw).hexdigest() != row['response_hash']:
                raise ValueError('F0_RESPONSE_HASH')
            final = json.loads(raw)['message']['content']
            try:
                parse_f0(final, registry_ids)
                reason = 'ACCEPTED'
            except (ValueError, TypeError, KeyError, RecursionError) as exc:
                reason = str(exc) if str(exc).startswith(('PROPOSAL_', 'SPEC_')) else 'MALFORMED'
            if reason != row['recorded_rejection_reason']:
                raise ValueError('F0_PARITY_FAILED')
            output.append({'round': row['round'], 'slot': row['slot'], 'response_hash': row['response_hash'],
                           'final_hash': hashlib.sha256(final.encode()).hexdigest(), 'reason': reason})
    return {'passed': True, 'responses': output, 'system_prompt': SYSTEM, 'contract': proposal_contract(),
            'historical_anchors': verify_anchors(), 'runner_calls': 0, 'repairs': 0}
