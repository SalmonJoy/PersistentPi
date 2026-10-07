"""Public-only diagnostic interpretation, followed by separate private measurement."""
from collections import Counter,defaultdict
import json
import re

from .analysis import nullable_sum
from .artifacts import Artifacts
from .calibration import public_records


def public_rows(store):
    result=[]
    artifacts=Artifacts(store)
    for row in public_records(store):
        manifest=json.loads(store.db.execute('SELECT json FROM manifests WHERE hash=(SELECT manifest_hash FROM runs WHERE id=?)',(row['run_id'],)).fetchone()[0])
        if 'm05_condition' not in manifest:continue
        events=[(r['type'],json.loads(r['payload_json'])) for r in store.db.execute(
            "SELECT type,payload_json FROM events WHERE run_id=? AND actor != 'hidden_evaluator' ORDER BY sequence",(row['run_id'],))]
        choices=Counter();length_stops=0;malformed=0;parse_failures=0;schema_failures=0
        previous=None;repeats=0
        for kind,value in events:
            if kind!='model_call_completed':continue
            telemetry=value['telemetry']
            length_stops+=telemetry.get('done_reason')=='length'
            if not value['valid_structured_output']:
                malformed+=telemetry['status']=='malformed_model_output'
                stages=telemetry.get('interface_parse',{})
                parse_failures+=telemetry['status']=='malformed_model_output' and not stages.get('parse_valid')
                schema_failures+=telemetry['status']=='malformed_model_output' and stages.get('parse_valid',False) and not stages.get('schema_valid')
                previous=None;continue
            raw=artifacts.get(value['raw_output_artifact']).decode()
            parsed=json.loads(raw)
            choice=parsed['tool'] if manifest['m05_condition']=='A1' else parsed['decision']
            choices[choice]+=1
            repeats+=parsed==previous;previous=parsed
        qualities=[p for k,p in events if k=='diagnostic_candidate']
        verifies=[p for k,p in events if k=='verification_completed']
        failures=[]
        unittest_failures=[];unittest_errors=[]
        for value in verifies:
            record=value['result'];output=artifacts.get(record['output_artifact']).decode('utf-8')
            match=re.search(r'FAILED \(([^)]+)\)',output)
            if record['outcome']=='pass':unit_fail=unit_error=0
            elif match:
                numbers=dict(re.findall(r'(failures|errors)=(\d+)',match[1]))
                unit_fail=int(numbers.get('failures',0));unit_error=int(numbers.get('errors',0))
            else:unit_fail=unit_error=None
            unittest_failures.append(unit_fail);unittest_errors.append(unit_error)
            if record['outcome']!='pass':failures.append({'outcome':record['outcome'],'output':output,
                'unittest_failures':unit_fail,'unittest_errors':unit_error})
        changed=any(q['actually_changed'] for q in qualities)
        row.update(model=manifest['m05_model'],condition=manifest['m05_condition'],choices=dict(choices),
            read_selected=choices['read_file'],edit_selected=choices['edit_file']+choices['EDIT'],
            replacement_selected=choices['REPLACE'],give_up_selected=choices['GIVE_UP'],finish_selected=choices['finish'],
            read_tasks=choices['read_file']>0,edit_generation=any(q['valid_modification_generated'] for q in qualities),
            actually_changed=changed,writes=sum(q['actually_changed'] for q in qualities),
            syntax_valid_proposals=sum(q['syntax_valid'] is True for q in qualities),
            syntax_failures=sum(q['syntax_valid'] is False for q in qualities),
            bounded_policy_failures=sum(q['syntax_valid'] is True and q['bounded_policy_valid'] is False for q in qualities),
            unmatched_or_protected_proposals=sum(q['syntax_valid'] is None for q in qualities),
            unchanged_proposals=sum(q['syntax_valid'] is not None and not q['proposed_change'] for q in qualities),
            checkpoint_created=bool(verifies or any(k=='diagnostic_candidate_checkpoint' for k,p in events)),
            test_executable=changed and any(p['result']['outcome'] in ('pass','fail') for p in verifies),
            public_failures=failures,unittest_failures=nullable_sum(unittest_failures),unittest_errors=nullable_sum(unittest_errors),
            public_infrastructure_outcomes=sum(p['result']['outcome'] in ('error','timeout','stopped') for p in verifies),
            automatic_verifications=sum(k=='automatic_public_verification' for k,p in events),
            length_stops=length_stops,malformed=malformed,parse_failures=parse_failures,schema_failures=schema_failures,
            identical_consecutive_decisions=repeats,qualities=qualities,model_identity=manifest['model']['identity'])
        result.append(row)
    return result


def summaries(rows,private=False):
    grouped=defaultdict(list)
    for row in rows:grouped[(row['model'],row['condition'])].append(row)
    result=[]
    for (model,condition),cohort in sorted(grouped.items()):
        row={'model':model,'condition':condition,'tasks':len(cohort),'output_ceiling':512,
            'identity':cohort[0]['model_identity'],'public_passes':sum(r['public_pass'] for r in cohort),
            'verification_tasks':sum(r['verification_reached'] for r in cohort),
            'edit_generation_tasks':sum(r['edit_generation'] for r in cohort),
            'changed_tasks':sum(r['actually_changed'] for r in cohort),
            'checkpoint_tasks':sum(r['checkpoint_created'] for r in cohort),
            'test_executable_tasks':sum(r['test_executable'] for r in cohort),
            'read_tasks':sum(r['read_tasks'] for r in cohort),
            'incomplete_runs':sum(r['status']!='finished' for r in cohort)}
        for key in ('read_selected','edit_selected','replacement_selected','give_up_selected','finish_selected','writes',
            'syntax_valid_proposals','syntax_failures','bounded_policy_failures','unmatched_or_protected_proposals','unchanged_proposals',
            'length_stops','malformed','parse_failures','schema_failures','automatic_verifications','identical_consecutive_decisions',
            'public_infrastructure_outcomes','model_decisions','tool_calls','attempts'):
            row[key]=sum(r[key] for r in cohort)
        for key in ('input_tokens','output_tokens','inference_seconds','wall_seconds','unittest_failures','unittest_errors'):
            row[key]=nullable_sum(r[key] for r in cohort)
        row['edit_generation_rate']=row['edit_generation_tasks']/len(cohort)
        row['verification_reach_rate']=row['verification_tasks']/len(cohort)
        row['public_solve_rate']=row['public_passes']/len(cohort)
        if private:
            row['hidden_passes']=sum(r['hidden_pass'] for r in cohort)
            row['hidden_solve_rate']=row['hidden_passes']/len(cohort)
        result.append(row)
    return result


def interpret(aggregates):
    by_model=defaultdict(dict)
    for row in aggregates:by_model[row['model']][row['condition']]=row
    cases=[]
    successes=[]
    for model,rows in sorted(by_model.items()):
        if set(rows)!=set(('A1','A2','A3')):raise ValueError('Complete diagnostic matrix required')
        a,b,c=(rows[k] for k in ('A1','A2','A3'))
        read_only=a['read_tasks']==a['tasks'] and a['edit_selected']==0 and a['public_passes']==0
        cases.append({'model':model,'A1_read_only':read_only,
            'case1':read_only and (b['public_passes']>0 or c['public_passes']>0),
            'case2':a['public_passes']==b['public_passes']==0 and c['public_passes']>0,
            'case3':b['public_passes']==c['public_passes']==0 and max(b['edit_generation_rate'],c['edit_generation_rate'])>=.5})
        successes.append(b['public_passes']>0 or c['public_passes']>0)
    return {'version':1,'per_model':cases,'case4':all(r['edit_generation_tasks']==0 for r in aggregates if r['condition']=='A3'),
        'case5':any(successes) and not all(successes),'public_capability_demonstrated':any(r['public_passes'] for r in aggregates),
        'hidden_results_used':False,'selection_performed':False,'additional_attempts_authorized':False}


def final_report(store,interpretation):
    rows=public_rows(store)
    for r in rows:
        r['hidden_outcome']=store.db.execute('SELECT evaluation_status FROM runs WHERE id=?',(r['run_id'],)).fetchone()[0]
        r['hidden_pass']=r['hidden_outcome']=='pass'
    return {'version':1,'interpretation':interpretation,'aggregates':summaries(rows,private=True),'runs':rows}
