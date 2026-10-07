"""Preregistered family-stratified cluster statistics and full-cohort costs."""
from collections import defaultdict
import math
import random

SEED = 8006
COSTS = ('candidates','model_decisions','tool_calls','input_tokens','output_tokens',
         'tokens','inference_seconds','wall_seconds','verification_seconds')


def quantile(values, probability):
    ordered = sorted(values)
    index = (len(ordered)-1)*probability
    lower = math.floor(index)
    upper = math.ceil(index)
    return ordered[lower] + (ordered[upper]-ordered[lower])*(index-lower)


def cluster_structure(rows):
    families = defaultdict(lambda:defaultdict(list))
    seen = set()
    for row in rows:
        if row['task_id'] in seen:
            raise ValueError('Duplicate task row')
        seen.add(row['task_id'])
        families[row['family']][row['template']].append(row)
    if not seen:
        raise ValueError('Empty cohort')
    if any(len({len(v) for v in clusters.values()}) != 1 for clusters in families.values()):
        raise ValueError('Unequal template sizes within a family')
    template_families = {}
    for family,clusters in families.items():
        for template in clusters:
            if template in template_families and template_families[template] != family:
                raise ValueError('Template appears in multiple families')
            template_families[template] = family
    return families


def resample_clusters(rows, rng):
    families = cluster_structure(rows)
    result = []
    for family in sorted(families):
        clusters = families[family]
        names = sorted(clusters)
        for _ in names:
            result.extend(clusters[rng.choice(names)])
    return result


def bootstrap_difference(rows, left, right, replicates=10000, seed=SEED):
    structure = cluster_structure(rows)
    # Preaggregate clusters without ever independently sampling their instances.
    strata = [[(sum(left(r)-right(r) for r in members),len(members))
               for _,members in sorted(clusters.items())] for _,clusters in sorted(structure.items())]
    rng, samples = random.Random(seed), []
    for _ in range(replicates):
        total, count = 0,0
        for clusters in strata:
            for _ in clusters:
                value,size = rng.choice(clusters)
                total += value
                count += size
        samples.append(total/count)
    return [quantile(samples,.025),quantile(samples,.975)]


def paired_permutation(rows, left, right, permutations=100000, seed=SEED):
    structure = cluster_structure(rows)
    differences = [sum(left(r)-right(r) for r in members)
                   for _,clusters in sorted(structure.items()) for _,members in sorted(clusters.items())]
    observed = abs(sum(differences))
    rng, extreme = random.Random(seed), 0
    for _ in range(permutations):
        statistic = abs(sum(d if rng.getrandbits(1) else -d for d in differences))
        extreme += statistic >= observed
    return {'p_value':(extreme+1)/(permutations+1),'extreme':extreme,
            'permutations':permutations,'plus_one':True,'seed':seed,'two_sided':True}


def validated(row, arm, k):
    item = row['arms'][arm][k-1]
    return int(item['public'] == 'pass' and item['hidden'] == 'pass')


def analyze(rows, bootstrap_replicates=10000, permutations=100000, formal=False):
    structure = cluster_structure(rows)
    n = len(rows)
    if formal and (n!=96 or len({r['template'] for r in rows})!=32 or len({r['family'] for r in rows})!=8
                   or bootstrap_replicates!=10000 or permutations!=100000):
        raise ValueError('Formal analysis must retain frozen cohort and resampling counts')
    if formal and any(len(clusters)!=4 or any(len(members)!=3 for members in clusters.values()) for clusters in structure.values()):
        raise ValueError('Formal analysis requires four clusters/family and three instances/cluster')
    for row in rows:
        if set(row['arms']) != {'D','O','R'} or any(len(v) != 5 for v in row['arms'].values()):
            raise ValueError('Incomplete paired horizons')
        prefixes = {row['arms'][a][0]['prefix_id'] for a in ('D','O','R')}
        if len(prefixes) != 1:
            raise ValueError('D/O/R initial lineage mismatch')
        initial_outcomes = {(row['arms'][a][0]['public'],row['arms'][a][0]['hidden']) for a in ('D','O','R')}
        if len(initial_outcomes)!=1:
            raise ValueError('Shared initial prefix outcomes differ')
        if any(p['hidden'] not in ('pass','fail') for arm in row['arms'].values() for p in arm):
            raise ValueError('Analysis requires completed hidden measurements')
        for arm in ('D','O','R'):
            outcomes = [validated(row,arm,k) for k in range(1,6)]
            if outcomes != sorted(outcomes):
                raise ValueError('Validated success must carry forward after public success')
    curve, recovery, marginals = {}, {}, {}
    initial_failures = [r for r in rows if r['arms']['D'][0]['public'] == 'fail']
    for arm in ('D','O','R'):
        curve[arm] = []
        for k in range(1,6):
            items = [r['arms'][arm][k-1] for r in rows]
            costs = {name:sum(i['cost'].get(name,0) for i in items) for name in COSTS}
            curve[arm].append({'k':k,'public_success':sum(i['public']=='pass' for i in items)/n,
                              'hidden_success':sum(i['hidden']=='pass' for i in items)/n,
                              'validated_success':sum(validated(r,arm,k) for r in rows)/n,
                              'logical_cost':costs})
        public_recovered = sum(r['arms'][arm][4]['public']=='pass' for r in initial_failures)
        recovered = [r for r in initial_failures if validated(r,arm,5)]
        first = {r['task_id']:next(k for k in range(2,6) if validated(r,arm,k)) for r in recovered}
        first_public = {r['task_id']:next((k for k in range(1,6) if r['arms'][arm][k-1]['public']=='pass'),None) for r in rows}
        formation = sum(r['arms'][arm][4]['cost'].get('candidates',0)>=2 for r in initial_failures)
        recovery[arm] = {'initial_verified_failures':len(initial_failures),
                         'public_recovered':public_recovered,'validated_recovered':len(recovered),
                         'recovery_rate_after_failure':public_recovered/len(initial_failures) if initial_failures else None,
                         'validated_recovery_rate':len(recovered)/len(initial_failures) if initial_failures else None,
                         'first_validated_recovery':first,'formed_second_candidate':formation}
        recovery[arm]['first_public_success'] = first_public
        marginals[arm] = []
        for a,b in ((1,3),(3,5),(1,5)):
            gain = sum(validated(r,arm,b)-validated(r,arm,a) for r in rows)
            added = {name:curve[arm][b-1]['logical_cost'][name]-curve[arm][a-1]['logical_cost'][name] for name in COSTS}
            marginals[arm].append({'from':a,'to':b,'additional_validated_recoveries':gain,
                'additional_cost':added,'cost_per_recovery':{name:value/gain if gain else None for name,value in added.items()},
                'recoveries_per_100k_tokens':gain*100000/added['tokens'] if added['tokens'] else None})
    d1,d5,o5 = (lambda r:validated(r,'D',1)),(lambda r:validated(r,'D',5)),(lambda r:validated(r,'O',5))
    di = sum(d5(r)-d1(r) for r in rows)/n
    interval = bootstrap_difference(rows,d5,d1,bootstrap_replicates)
    label = ('meaningful_positive' if di>=.1 and interval[0]>=.1 else
             'small_positive' if 0<di<.1 else
             'materiality_inconclusive' if interval[0]<.1<=interval[1] else 'no_observed_recovery')
    return {'version':1,'tasks':n,'templates':len({r['template'] for r in rows}),
            'families':len({r['family'] for r in rows}),'curve':curve,'recovery':recovery,'marginals':marginals,
            'H_I':{'effect':di,'materiality':.1,'ci95':interval,'interpretation':label,
                   'no_p_value':True,'raw_recovered_tasks':recovery['D']['validated_recovered']},
            'H_F':{'effect':sum(d5(r)-o5(r) for r in rows)/n,
                   'ci95':bootstrap_difference(rows,d5,o5,bootstrap_replicates),
                   **paired_permutation(rows,d5,o5,permutations),'alpha':.05,'multiplicity':'sole_confirmatory_test'},
            'Q3':{'effect':sum(validated(r,'D',5)-validated(r,'R',5) for r in rows)/n,
                  'interpretation':'descriptive; workspace/history and feedback differ'},
            'bootstrap':{'replicates':bootstrap_replicates,'seed':SEED,'method':'percentile',
                         'unit':'whole_template','strata':'fixed_bug_family'},
            'task_telemetry':{r['task_id']:r.get('telemetry',{}) for r in rows},
            'limitations':['families are fixed','zero-width bootstrap is not equivalence',
                          'formation-limited trajectories do not establish failure of repair']}
