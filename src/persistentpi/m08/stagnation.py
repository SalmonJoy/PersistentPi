"""Post-execution measurements only. No stagnation intervention."""
from collections import Counter
import json

from ..contracts import digest
from ..contracts import ActionRequest
from ..interfaces import authorize_interface
from .feedback import sanitized


def acquisition_signature(state):
    candidate = state['candidate']
    public = next((o['result']['data']['structured_public'] for o in reversed(state['observations'])
                   if o['action']['tool']=='run_public_tests'),None)
    value = {'version':1,'actions':[o['action'] for o in state['observations'] if o['action']['tool']!='run_public_tests'],
             'checkpoint':candidate['checkpoint'] if candidate else None,
             'outcome':candidate['outcome'] if candidate else None,'stop_reason':state['stop_reason'],
             'public':[(c['id'],c['outcome'],c['type'],sanitized(c['message'])) for c in public['cases']] if public else None}
    return digest(value)


def metrics(campaign, run_ids):
    actions,rejected,candidates,failures,purposes = [],[],[],[],[]
    for run in run_ids:
        for e in campaign.store.db.execute('SELECT type,payload_json FROM events WHERE run_id=? ORDER BY sequence',(run,)):
            payload = json.loads(e['payload_json'])
            if e['type']=='action_completed':
                action,result = payload['action'],payload['result']
                try:
                    authorize_interface(ActionRequest.from_dict(action),'E0')
                    valid_contract = True
                except ValueError:
                    valid_contract = False
                actions.append((digest(action),action['tool'],result['ok'],valid_contract))
                if action['tool']=='edit_file' and not result['ok']:
                    error = result['error'] or ''
                    category = ('no_match' if 'matching occurrence' in error else
                                'no_op' if 'unchanged' in error else
                                'permission' if 'Protected' in error else 'contract')
                    receipt = campaign.store.db.execute('SELECT payload_hash FROM m08_receipts WHERE id=?',(payload['call_id']+'-tool',)).fetchone()
                    checkpoint = json.loads(campaign.artifacts.get(receipt[0]))['checkpoint']
                    rejected.append(digest([action,category,checkpoint]))
            elif e['type']=='decision_completed' and payload['action']['tool']=='finish':
                action = payload['action']
                if not set(action['arguments'])-{'reason'} and isinstance(action['arguments'].get('reason',''),str):
                    actions.append((digest(action),'finish',True,True))
            elif e['type']=='candidate_completed':
                candidates.append(payload)
                result = json.loads(campaign.artifacts.get(payload['public_result_hash']))
                if result['outcome']=='fail':
                    signature = [(c['id'],c['type'],sanitized(c['message'])) for c in result['cases'] if c['outcome']=='fail']
                    failures.append(digest(signature))
        for receipt in campaign.store.db.execute("SELECT payload_hash FROM m08_receipts WHERE run_id=? AND kind='model'",(run,)):
            purposes.append(json.loads(campaign.artifacts.get(receipt[0])))
    # These are parsed requests with a valid tool contract, including edits which
    # failed applicability. Their repetition is a central stagnation observation.
    valid = [a for a in actions if a[3]]
    edits = [a[0] for a in actions if a[1]=='edit_file']
    longest,current,last = 0,0,None
    for key,_,_,_ in actions:
        current = current+1 if key==last else 1
        longest,last = max(longest,current),key
    def repeats(values):
        return sum(n-1 for n in Counter(values).values())
    buckets = {}
    for receipt in purposes:
        action = receipt['semantic_action']
        label = ('inspection' if receipt['control_phase']=='INSPECT' else
                 'edit_generation' if action=='edit_file' else 'other_decision')
        b = buckets.setdefault(label,{'calls':0,'input_tokens':0,'output_tokens':0,'inference_seconds':0.})
        b['calls'] += 1
        for field in ('input_tokens','output_tokens','inference_seconds'):
            b[field] += receipt[field]
    accepted = sum(a[1]=='edit_file' and a[2] for a in actions)
    return {'version':1,'edit_proposals':len(edits),'accepted_edits':accepted,
            'rejected_edits':len(rejected),'repeated_canonical_edits':repeats(edits),
            'accepted_edit_rate':accepted/len(edits) if edits else None,
            'rejected_edit_rate':len(rejected)/len(edits) if edits else None,
            'repeated_edit_rate':repeats(edits)/len(edits) if edits else None,
            'repeated_rejected_tuples':repeats(rejected),'longest_repeated_action_streak':longest,
            'repeated_public_failures':repeats(failures),'unique_candidate_bytes':len({c['byte_hash'] for c in candidates}),
            'unique_candidate_ast':len({c['ast_hash'] for c in candidates}),
            'action_diversity':len({a[0] for a in valid})/len(valid) if valid else None,
            'inference_by_observed_purpose':buckets}
