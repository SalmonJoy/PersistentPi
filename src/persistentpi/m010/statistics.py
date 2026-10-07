"""Paired family bootstrap and exact enumeration; standard library only."""
from collections import Counter
import math
import random


def groups(differences):
    if len(differences) != 8 or any(len(v) != 3 or any(x not in (-1, 0, 1) for x in v) for v in differences.values()):
        raise ValueError('M010_PAIRED_CLUSTER_STRUCTURE')
    return [sum(differences[k]) for k in sorted(differences)]


def paired_bootstrap(differences):
    totals = groups(differences)
    rng = random.Random(20261010)
    # Integer histogram preserves nearest-rank quantiles without float ordering noise.
    histogram = Counter(sum(totals[rng.randrange(8)] for _ in range(8)) for _ in range(100000))
    def quantile(p):
        rank = math.ceil(p * 100000)
        count = 0
        for value, frequency in sorted(histogram.items()):
            count += frequency
            if count >= rank:
                return value / 24
        raise AssertionError('Bootstrap quantile unavailable')
    return {'effect': sum(totals) / 24, 'ci95': [quantile(.025), quantile(.975)],
            'ci975': [quantile(.0125), quantile(.9875)], 'seed': 20261010,
            'resamples': 100000, 'unit': 'whole semantic family with three paired instances',
            'quantile': 'nearest-rank', 'histogram': {str(k): v for k, v in sorted(histogram.items())}}


def exact_permutation(differences):
    totals = groups(differences)
    observed = sum(totals)
    assignments = [{'mask': mask, 'numerator': sum(-v if mask & (1 << k) else v for k, v in enumerate(totals)),
                    'denominator': 24} for mask in range(256)]
    tail = sum(abs(row['numerator']) >= abs(observed) for row in assignments)
    return {'T_obs': observed / 24, 'assignments': assignments, 'tail_count': tail,
            'p_value': tail / 256, 'denominator': 256, 'ties_included': True, 'correction': 0}


def holm(values):
    ordered = sorted(values.items(), key=lambda item: (item[1], item[0]))
    result, previous = {}, 0
    for index, (name, value) in enumerate(ordered):
        previous = max(previous, min(1, (len(ordered) - index) * value))
        result[name] = previous
    return result
