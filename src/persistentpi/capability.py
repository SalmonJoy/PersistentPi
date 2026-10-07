"""Passive public-trace metrics and public-only model viability/selection."""
from collections import defaultdict
from itertools import combinations
import json
from statistics import pvariance

from .calibration import aggregate, public_records
from .contracts import digest


def progress_trace(decisions):
    """Pure state machine; never affects the Runner, commands, budgets or feedback."""
    epoch, consecutive, previous = 0, 0, None
    read_evidence, verification_evidence, inspected = set(), set(), set()
    result=[]
    for d in decisions:
        action=d.get('action')
        stages=d['stages']
        output=d.get('result') or {}
        tool=action['tool'] if action else None
        arguments=action['arguments'] if action else {}
        action_hash=digest(action) if action else None
        repeated=action_hash is not None and action_hash==previous
        previous=action_hash
        write_requested=tool=='edit_file'
        write_authorized=write_requested and stages['action_authorized']
        changed=write_requested and stages['action_executed'] and output.get('ok') is True
        productive=False
        reread=False
        reason='no new public evidence or source change'
        if changed:
            epoch+=1
            consecutive=0
            productive=True
            reason='successful source edit'
        else:
            consecutive+=1
            if tool=='read_file' and stages['action_executed'] and output.get('ok') is True:
                path=arguments['path']
                data=output.get('data',{})
                fingerprint=digest({'text':data.get('text'), 'truncated':data.get('truncated')})
                key=(epoch,path,fingerprint)
                reread=key in read_evidence
                productive=not reread
                read_evidence.add(key)
                inspected.add(path)
                reason='repeated same-file evidence at unchanged source' if reread else 'new file evidence at current source'
            elif stages['public_verification_reached']:
                checkpoint=output.get('checkpoint') or {}
                key=(checkpoint.get('hash'),output.get('data',{}).get('outcome'))
                productive=key not in verification_evidence
                verification_evidence.add(key)
                reason='new public checkpoint/outcome evidence' if productive else 'repeated public checkpoint/outcome evidence'
        result.append({'call_id':d['call_id'],'productive':productive,'productive_reason':reason,
            'write_requested':write_requested,'write_authorized':write_authorized,
            'source_state_changed':changed,'source_epoch':epoch,'same_file_reread':reread,
            'identical_action_repeated':repeated,'consecutive_non_state_changing':consecutive,
            'unique_files_inspected':len(inspected)})
    return result


def records(store):
    """Public-only view: no hidden columns, events or test evidence queried."""
    rows=public_records(store)
    result=[]
    for row in rows:
        run=store.db.execute('SELECT manifest_hash FROM runs WHERE id=?',(row['run_id'],)).fetchone()
        manifest=json.loads(store.db.execute('SELECT json FROM manifests WHERE hash=?',(run[0],)).fetchone()[0])
        if 'm04_model' not in manifest:
            continue
        events=[(e['type'],json.loads(e['payload_json'])) for e in store.db.execute(
            "SELECT type,payload_json FROM events WHERE run_id=? AND actor != 'hidden_evaluator' ORDER BY sequence",(row['run_id'],))]
        def blob(h):
            # Artifacts.get verifies hashes; traces are public action artifacts only.
            from .artifacts import Artifacts
            return json.loads(Artifacts(store).get(h))
        actions={p['call_id']:blob(p['action_artifact']) for k,p in events if k=='decision_completed'}
        outputs={p['call_id']:blob(p['result_artifact']) for k,p in events if k=='action_completed'}
        funnels=[p for k,p in events if k=='decision_funnel']
        trace=progress_trace([{**f,'action':actions.get(f['call_id']),'result':outputs.get(f['call_id'])} for f in funnels])
        row.update(model_tag=manifest['m04_model'],model_identity=manifest['model']['identity'],
            progress=trace,productive_decisions=sum(d['productive'] for d in trace),
            write_requests=sum(d['write_requested'] for d in trace),
            authorized_write_requests=sum(d['write_authorized'] for d in trace),
            writes=sum(d['source_state_changed'] for d in trace),
            write_attempt_task=any(d['write_authorized'] for d in trace),
            rereads=sum(d['same_file_reread'] for d in trace),
            successful_reads=sum(f['tool']=='read_file' and f['stages']['action_executed'] for f in funnels),
            repeated_actions=sum(d['identical_action_repeated'] for d in trace),
            max_consecutive_non_state_changing=max((d['consecutive_non_state_changing'] for d in trace),default=0),
            unique_files_inspected=trace[-1]['unique_files_inspected'] if trace else 0,
            public_failure_count=sum(f['reason']=='public_fail' for f in funnels),
            edit_applicability_failures=sum(f['tool']=='edit_file' and f['stages']['action_authorized'] and not f['stages']['action_applicable'] for f in funnels))
        result.append(row)
    return result


def summarize(rows):
    if len({r['model_tag'] for r in rows})!=1:
        raise ValueError('Model identity comparison must keep conditions isolated')
    result=aggregate(rows)
    result.update(model=rows[0]['model_tag'],identity=rows[0]['model_identity'])
    for k in ('productive_decisions','write_requests','authorized_write_requests','writes','rereads','successful_reads','repeated_actions','unique_files_inspected','edit_applicability_failures'):
        result[k]=sum(r[k] for r in rows)
    result['productive_action_rate']=result['productive_decisions']/result['model_decisions'] if result['model_decisions'] else 0
    result['write_attempt_tasks']=sum(r['write_attempt_task'] for r in rows)
    result['write_attempt_rate']=result['write_attempt_tasks']/len(rows)
    result['reread_rate_per_decision']=result['rereads']/result['model_decisions'] if result['model_decisions'] else 0
    result['reread_rate_per_read']=result['rereads']/result['successful_reads'] if result['successful_reads'] else None
    result['max_consecutive_non_state_changing']=max(r['max_consecutive_non_state_changing'] for r in rows)
    result['source_state_changing_actions']=result['writes']
    edits=result['authorized_write_requests']
    result['edit_applicability_failure_rate']=result['edit_applicability_failures']/edits if edits else None
    result['significant_E0_applicability_failures']=bool(edits and result['edit_applicability_failures']>=2
        and result['edit_applicability_failures']/edits>=.25)
    return result


def viable(row, plan):
    return row['incomplete_runs']==0 and row['write_attempt_rate']>=plan['V1_write_task_rate'] and row['verification_task_rate']>=plan['V2_verification_task_rate']


def choose(rows, plan):
    candidates=[r for r in rows if viable(r,plan)]
    if not candidates:
        return None
    resident_known=all(r.get('resident_bytes') is not None for r in candidates)
    def key(r):
        return (-r['public_pass_count'],-r['verification_task_rate'],-r['productive_action_rate'],
                r['resident_bytes'] if resident_known else r['stored_bytes'],r['stored_bytes'],
                r['inference_seconds'] if r['inference_seconds'] is not None else float('inf'),
                r['total_tokens'] if r['total_tokens'] is not None else float('inf'),r['model'])
    return {**sorted(candidates,key=key)[0],'footprint_selection_basis':'resident then stored' if resident_known else 'stored (uniform missing-resident fallback)',
            'selection_hidden_results_used':False}


def efficiency(successes,tokens,inference_seconds,wall_seconds):
    return {'tasks_solved_per_hour':successes*3600/wall_seconds if wall_seconds and wall_seconds>0 else None,
        'tokens_per_solved_task':tokens/successes if successes and tokens is not None else None,
        'inference_seconds_per_solved_task':inference_seconds/successes if successes and inference_seconds is not None else None}


def repetition_measurements(cohort):
    """Exact pairwise trace/result agreement and population variance; no inference."""
    pairs=list(combinations(cohort,2))
    def agreement(key):
        return sum(a[key]==b[key] for a,b in pairs)/len(pairs) if pairs else None
    def result_key(r):
        return (r['public_pass'],r['hidden_pass'],r['stop_reason'])
    result={'replicates':len(cohort),
        'distinct_action_traces':len({tuple(r['action_hashes']) for r in cohort}),
        'distinct_output_traces':len({tuple(r['output_hashes']) for r in cohort}),
        'distinct_results':len({result_key(r) for r in cohort}),
        'pairwise_action_trace_exact_agreement':agreement('action_hashes'),
        'pairwise_output_trace_exact_agreement':agreement('output_hashes'),
        'pairwise_result_exact_agreement':sum(result_key(a)==result_key(b) for a,b in pairs)/len(pairs) if pairs else None,
        'variance_definition':'population variance; null if any replicate measurement is missing',
        'determinism_guaranteed':False}
    for key in ('input_tokens','output_tokens','total_tokens','inference_seconds','wall_seconds'):
        values=[r[key] for r in cohort]
        result[key]=values
        result[key+'_population_variance']=pvariance(values) if values and all(v is not None for v in values) else None
    return result


def final_measurements(store,selection,plan,footprints):
    rows=records(store)
    for r in rows:
        r['hidden_pass']=store.db.execute('SELECT evaluation_status FROM runs WHERE id=?',(r['run_id'],)).fetchone()[0]=='pass'
        measurement=store.db.execute("SELECT payload_json FROM events WHERE run_id=? AND type='hidden_funnel_result'",(r['run_id'],)).fetchone()
        if measurement:
            value=json.loads(measurement[0])
            r['counts']['hidden_evaluation_passed']=int(bool(value['call_id']) and value['hidden_evaluation_passed'])
    grouped=defaultdict(list)
    for r in rows:
        grouped[(r['phase'],r['model_tag'],r['attempt_budget'])].append(r)
    summaries=[]
    for (phase,model,budget),cohort in sorted(grouped.items()):
        summary=summarize(cohort)
        hidden=sum(r['hidden_pass'] for r in cohort)
        summary.update(phase=phase,attempt_budget=budget,hidden_pass_count=hidden,
                       **footprints[model],viable=viable(summary,plan))
        summary['hidden_efficiency']=efficiency(hidden,summary['total_tokens'],summary['inference_seconds'],summary['wall_seconds'])
        summary['public_efficiency']=efficiency(summary['public_pass_count'],summary['total_tokens'],summary['inference_seconds'],summary['wall_seconds'])
        summaries.append(summary)
    repeats=[]
    for model in plan['models']:
        cohort=[r for r in rows if r['phase']=='repeat' and r['model_tag']==model]
        if cohort:
            repeats.append({'model':model,'task':plan['evaluation_tasks'][0],**repetition_measurements(cohort)})
    recovered=[]
    for model in plan['models']:
        scaled=[r for r in rows if r['model_tag']==model and r['phase']=='scaling']
        if scaled:
            for before,after in ((1,3),(3,5)):
                a={r['task'] for r in scaled if r['attempt_budget']==before and r['hidden_pass']}
                b={r['task'] for r in scaled if r['attempt_budget']==after and r['hidden_pass']}
                pa={r['task'] for r in scaled if r['attempt_budget']==before and r['public_pass']}
                pb={r['task'] for r in scaled if r['attempt_budget']==after and r['public_pass']}
                recovered.append({'model':model,'from_budget':before,'to_budget':after,'hidden_recovered':sorted(b-a),'hidden_lost':sorted(a-b),
                    'public_recovered':sorted(pb-pa),'public_lost':sorted(pa-pb)})
    return {'version':1,'selection':selection,'aggregates':summaries,'runs':rows,'repetitions':repeats,'recovered':recovered}
