"""Comparable result sets, receipt unions, and engineering progression gates."""
from dataclasses import dataclass
import math
import random

from ..contracts import digest
from ..m08.benchmark import FAMILIES
from .cohorts import manifest, split_search


@dataclass(frozen=True)
class Result:
    scaffold_id: str
    cohort_hash: str
    task_id: str
    task_hash: str
    family: str
    template: str
    formed: bool
    public: str | None
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    inference_seconds: float = 0
    wall_seconds: float = 0
    receipt_id: str = ''
    termination: str = 'finished'

    def __post_init__(self):
        if type(self.formed) is not bool or self.public not in (None, 'pass', 'fail'):
            raise ValueError('RESULT_OUTCOME')
        if self.formed != (self.public is not None):
            raise ValueError('RESULT_FORMATION')
        for v in (self.calls, self.input_tokens, self.output_tokens):
            if type(v) is not int or v < 0:
                raise ValueError('RESULT_COUNT')
        for v in (self.inference_seconds, self.wall_seconds):
            if type(v) not in (int, float) or not math.isfinite(v) or v < 0:
                raise ValueError('RESULT_TIME')
        if self.family not in FAMILIES or not self.template.startswith(self.family + '/'):
            raise ValueError('RESULT_FAMILY')
        if self.termination in ('infrastructure', 'interrupted', 'indeterminate'):
            raise ValueError('Infrastructure result is incomplete, not a score')

    def to_dict(self):
        return dict(self.__dict__)


def validate_results(results, tasks, cohort_hash, scaffold_id):
    tasks = {t.task_id: t for t in tasks}
    if len(results) != len(tasks) or len({r.task_id for r in results}) != len(results):
        raise ValueError('Incomplete or duplicate result set')
    if {r.task_id for r in results} != set(tasks):
        raise ValueError('Result task cohort mismatch')
    for r in results:
        t = tasks[r.task_id]
        if (r.scaffold_id != scaffold_id or r.cohort_hash != cohort_hash or r.task_hash != t.task_hash
                or r.family != t.family or r.template != t.template):
            raise ValueError('Result identity mismatch')
        if not r.receipt_id:
            raise ValueError('Physical receipt missing')
    if len({r.receipt_id for r in results}) != len(results):
        raise ValueError('Physical receipt reused across distinct tasks')
    return tuple(sorted(results, key=lambda r: r.task_id))


def full_search(screen_results, remaining_results, search, scaffold_id):
    screen, remaining = split_search(search)
    cohort_hash = manifest(search, 'search')['hash']
    a = validate_results(screen_results, screen, cohort_hash, scaffold_id)
    b = validate_results(remaining_results, remaining, cohort_hash, scaffold_id)
    return validate_results(a + b, search, cohort_hash, scaffold_id)


def metrics(results):
    passed = [r for r in results if r.public == 'pass']
    formed = [r for r in results if r.formed]
    return {'tasks': len(results), 'public_passes': len(passed),
            'passing_families': len({r.family for r in passed}), 'formations': len(formed),
            'formation_families': len({r.family for r in formed}),
            'runner_tokens': sum(r.input_tokens + r.output_tokens for r in results),
            'runner_calls': sum(r.calls for r in results),
            'inference_seconds': sum(r.inference_seconds for r in results),
            'wall_seconds': sum(r.wall_seconds for r in results)}


def ranking(configuration, results):
    m = metrics(results)
    return (-m['public_passes'], -m['passing_families'], -m['formations'], -m['formation_families'],
            configuration.complexity(), m['runner_tokens'], m['runner_calls'],
            m['inference_seconds'], m['wall_seconds'], configuration.scaffold_id)


def best(entries):
    if not entries:
        return None
    signatures = {tuple(sorted((r.task_id, r.task_hash, r.cohort_hash) for r in rs)) for _, rs in entries}
    if len(signatures) != 1:
        raise ValueError('Cannot compare different task sets')
    return min(entries, key=lambda pair: ranking(*pair))


def entry_gate(candidate, b0, b1):
    if len(candidate) != 32 or any(len(rs) != 32 for rs in (b0, b1)):
        raise ValueError('Entry requires complete Search32')
    if len({tuple(sorted((r.task_id, r.task_hash, r.cohort_hash) for r in rs))
            for rs in (candidate, b0, b1)}) != 1:
        raise ValueError('Entry cohorts mismatch')
    c, a, b = map(metrics, (candidate, b0, b1))
    checks = {'vs_B0': c['public_passes'] >= a['public_passes'] + 4,
              'vs_B1': c['public_passes'] >= b['public_passes'] + 4,
              'families': c['passing_families'] >= 4}
    return {'passed': all(checks.values()), 'checks': checks, 'metrics': c}


def cluster_draw(groups, rng):
    return tuple(cluster for family in sorted(groups)
                 for cluster in rng.choices(groups[family], k=len(groups[family])))


def bootstrap(candidate, reference, replicates=10000, seed=9004):
    if len(candidate) != 48 or len(reference) != 48 or replicates < 1:
        raise ValueError('Bootstrap requires all Qualification48')
    ref = {r.task_id: r for r in reference}
    if len(ref) != 48 or len({r.task_id for r in candidate}) != 48 or set(ref) != {r.task_id for r in candidate}:
        raise ValueError('Bootstrap pairing missing')
    clusters = {}
    for r in candidate:
        x = ref[r.task_id]
        if (r.cohort_hash, r.task_hash, r.family, r.template) != (x.cohort_hash, x.task_hash, x.family, x.template):
            raise ValueError('Bootstrap pairing identity mismatch')
        clusters.setdefault((r.family, r.template), []).append(int(r.public == 'pass') - int(x.public == 'pass'))
    if len(clusters) != 16 or any(len(v) != 3 for v in clusters.values()):
        raise ValueError('Bootstrap cluster structure changed')
    groups = {f: [tuple(v) for (family, _), v in sorted(clusters.items()) if family == f] for f in FAMILIES}
    if any(len(v) != 2 for v in groups.values()):
        raise ValueError('Bootstrap family structure changed')
    rng = random.Random(seed)
    samples = sorted(sum(sum(cluster) for cluster in cluster_draw(groups, rng)) / 48 for _ in range(replicates))
    def percentile(p):
        position = (len(samples)-1)*p
        lo = int(position)
        hi = min(lo+1, len(samples)-1)
        return samples[lo] + (samples[hi]-samples[lo])*(position-lo)
    return {'effect': sum(sum(v) for v in clusters.values())/48,
            'ci95': [percentile(.025), percentile(.975)], 'replicates': replicates,
            'seed': seed, 'unit': 'whole-template', 'strata': 'fixed-family', 'p_value': None}


def qualification_gate(candidate, b0, b1):
    a, b = bootstrap(candidate, b0), bootstrap(candidate, b1)
    c, ma, mb = map(metrics, (candidate, b0, b1))
    checks = {'formations': c['formations'] >= 36, 'passes': c['public_passes'] >= 24,
              'families': c['passing_families'] >= 6,
              'extra_vs_B0': c['public_passes'] >= ma['public_passes']+8,
              'extra_vs_B1': c['public_passes'] >= mb['public_passes']+8,
              'LCB_vs_B0': a['ci95'][0] > 0, 'LCB_vs_B1': b['ci95'][0] > 0}
    return {'passed': all(checks.values()), 'checks': checks, 'vs_B0': a, 'vs_B1': b,
            'metrics': c, 'interpretation': 'engineering progression only'}
