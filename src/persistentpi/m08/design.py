"""Development-only calibration, fixed scheduling, and physical forecast gates."""
import itertools
import random

from ..contracts import digest
from .analysis import quantile, resample_clusters
from .benchmark import FAMILIES, TIERS


def select_tier(records):
    if {r['tier'] for r in records} != set(TIERS):
        raise ValueError('Calibration must cover all three pre-generated tiers')
    summaries = []
    for tier in TIERS:
        rows = [r for r in records if r['tier']==tier]
        if len(rows)!=32 or len({r['task_id'] for r in rows})!=32 or any(r['split']!='development' for r in rows):
            raise ValueError('Calibration requires 32 distinct development tasks per tier')
        verified = sum(r['public'] in ('pass','fail') for r in rows)
        successes = sum(r['public']=='pass' for r in rows)
        failures = [r for r in rows if r['public']=='fail']
        families = len({r['family'] for r in failures})
        qualifies = 10<=successes<=22 and verified>=26 and len(failures)>=8 and families>=6
        summaries.append({'tier':tier,'verified':verified,'successes':successes,'failures':len(failures),
                          'failure_families':families,'qualifies':qualifies})
    eligible = [s for s in summaries if s['qualifies']]
    selected = min(eligible,key=lambda s:(abs(s['successes']-16),-s['failures'],TIERS.index(s['tier'])))['tier'] if eligible else None
    return {'version':1,'selected_tier':selected,'summaries':summaries,'stop':selected is None}


def schedule(tasks):
    tasks = sorted(tasks,key=lambda t:t.task_id)
    rng = random.Random(8005)
    rng.shuffle(tasks)
    orders = list(itertools.permutations(('D','O','R')))
    rng.shuffle(orders)
    entries = [{'task_id':t.task_id,'task_hash':t.hash,'order':list(orders[i%6])} for i,t in enumerate(tasks)]
    return {'version':1,'seed':8005,'entries':entries,'hash':digest(entries)}


def audit_selection(tasks):
    selected = []
    for family in FAMILIES:
        candidates = sorted((t for t in tasks if t.split=='development' and t.family==family),key=lambda t:t.task_id)
        if not candidates:
            raise ValueError('Audit family missing')
        selected.append(candidates[0].task_id)
    return {'version':1,'selected':selected,'additional_repetitions':2,'windows':16}


def development_design(tasks):
    tasks = tuple(tasks)
    if len(tasks)!=96 or any(t.split!='development' for t in tasks):
        raise ValueError('Preflight requires all 96 development tasks across three tiers')
    groups = {tier:[t for t in tasks if t.tier==tier] for tier in TIERS}
    if any(len(group)!=32 for group in groups.values()):
        raise ValueError('Each development tier must have 32 tasks')
    return {'version':1,'initial_schedule':schedule(tasks),
            'continuations':{tier:schedule(group) for tier,group in groups.items()},
            'audit':{tier:audit_selection(group) for tier,group in groups.items()}}


def forecast(calibration, already_spent, replicates=10000):
    """Each row is a whole task bundle's physical cost, never logical arm sum."""
    if len(calibration)!=32 or any(r.get('usage_kind')!='measured' for r in calibration):
        raise ValueError('Forecast requires 32 measured selected-tier development bundles')
    if len({r['template'] for r in calibration})!=16 or len({r['family'] for r in calibration})!=8:
        raise ValueError('Forecast calibration clusters are incomplete')
    if any(len([r for r in calibration if r['template']==t])!=2 for t in {r['template'] for r in calibration}):
        raise ValueError('Forecast requires both development instances per template')
    rng = random.Random(8006)
    times,tokens = [],[]
    for _ in range(replicates):
        sampled = resample_clusters(calibration,rng)
        # Development has 32 tasks; the final cohort has 96.
        # Private candidate scores are forbidden in development. Reserve the
        # fixed worst-case 13 unique selected checkpoints/task at 5 seconds each.
        hidden_bound = 96*13*5
        times.append(already_spent['wall_seconds']+3*sum(r['wall_seconds'] for r in sampled)+hidden_bound)
        tokens.append(already_spent['tokens']+3*sum(r['tokens'] for r in sampled))
    ptime,ptokens = quantile(times,.9),quantile(tokens,.9)
    return {'version':1,'seed':8006,'replicates':replicates,'quantile':.9,
            'forecast_wall_seconds':ptime,'forecast_tokens':ptokens,'already_spent':already_spent,
            'hidden_measurement_wall_reserve':96*13*5,
            'launch_allowed':ptime<9*3600 and ptokens<9000000,
            'hard_wall_seconds':12*3600,'hard_tokens':12000000}
