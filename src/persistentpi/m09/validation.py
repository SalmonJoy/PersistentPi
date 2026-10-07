"""Offline regression runner with synthetic, non-reserved benchmark fixtures."""
from dataclasses import replace
from contextlib import ExitStack
from functools import lru_cache
import http.client
import importlib.util
import io
import json
from pathlib import Path
import random
import subprocess
import sys
import types
import unittest
from unittest.mock import patch

from ..artifacts import atomic_write
from ..contracts import canonical, digest


def synthetic_generator():
    from ..m08 import benchmark

    class FixtureRandom(random.Random):
        def sample(self, population, k, **kwargs):
            if population == [2, 3, 4, 5, 6]:
                population = [7, 8, 9, 10, 11]
            return super().sample(population, k, **kwargs)

    namespace = {**benchmark.generate.__globals__,
                 'random': types.SimpleNamespace(Random=FixtureRandom)}
    generator = types.FunctionType(benchmark.generate.__code__, namespace)

    @lru_cache(maxsize=1)
    def generate():
        tasks, partition = generator()
        return tuple(replace(t, task_id='p' + digest(['m09b-synthetic', t.task_id])[:16])
                     for t in tasks), partition
    return generate


def validate(root, output, include_m09=True):
    root, output = Path(root), Path(output)
    if output.exists():
        raise ValueError('Validation output already exists')
    output.mkdir(parents=True)
    from .preparation import preparation_paths
    import hashlib
    def fingerprint():
        return digest({p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in preparation_paths(root)})
    original_fingerprint = fingerprint()
    sys.path.insert(0, str(root / 'tests'))
    sys.path.insert(0, str(root / 'scripts'))
    from ..m08 import benchmark
    from ..m08 import freeze, acquisition_pilot, primitive_pilot, capability_pilot
    baseline_names = set(subprocess.run(['git', '-C', str(root), 'ls-tree', '-r', '--name-only',
                         '28e44ee'], check=True, capture_output=True, text=True).stdout.splitlines())
    original_paths = freeze.freeze_paths
    def baseline_paths(folder):
        return [p for p in original_paths(folder) if p.relative_to(folder).as_posix() in baseline_names]
    log = io.StringIO()
    with ExitStack() as stack:
        stack.enter_context(patch.object(benchmark, 'generate', synthetic_generator()))
        for module in (freeze, acquisition_pilot, primitive_pilot, capability_pilot):
            if hasattr(module, 'freeze_paths'):
                stack.enter_context(patch.object(module, 'freeze_paths', baseline_paths))
        for client in (http.client.HTTPConnection, http.client.HTTPSConnection):
            stack.enter_context(patch.object(client, 'connect', side_effect=AssertionError('Live HTTP forbidden')))
        suite = unittest.defaultTestLoader.discover(str(root / 'tests'))
        for name in ('m08f_tests', 'm08g_tests', 'm08h_tests', 'm08i_tests'):
            spec = importlib.util.spec_from_file_location(name, root / 'scripts' / (name + '.py'))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
        if include_m09:
            path = root / 'scripts/m09b_tests.py'
            if path.exists():
                spec = importlib.util.spec_from_file_location('m09b_tests', path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    unchanged = original_fingerprint == fingerprint()
    receipt = {'tests': result.testsRun, 'failures': len(result.failures),
               'errors': len(result.errors), 'skips': len(result.skipped),
               'passed': result.wasSuccessful() and unchanged, 'live_inference': False,
               'validated_source_hash':original_fingerprint,'trusted_sources_unchanged_during_tests':unchanged,
               'reserved_task_contents_loaded': False,
               'historical_fixture_policy': 'synthetic parameters 7..11; namespaced IDs',
               'benchmark_hidden_scoring': False}
    atomic_write(output / 'tests.txt', log.getvalue().encode())
    atomic_write(output / 'validation.json', canonical(receipt))
    if not receipt['passed']:
        raise ValueError(json.dumps(receipt) + '\n' + log.getvalue()[-12000:])
    return receipt
