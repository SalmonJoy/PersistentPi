"""Offline preparation and source-addressed freeze; no live admission execution."""
import hashlib
import json
from pathlib import Path
import platform

from ..artifacts import atomic_write
from ..contracts import canonical, digest
from .boundary import access_audit, isolated_output
from .config import ROOT, configuration, COMMON_SYSTEM, SUFFIX
from .f0 import historical_parity
from .f2 import tool_schema
from .frozen import parent_registry, verify_anchors
from .mutation import mutation_schema, shared_rules
from .render import render, probe_request
from .scenarios import generate, schedule, GENERATOR, PROFILES, REMAINING


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def trusted_sources():
    files = list((ROOT / 'src/persistentpi/m010').glob('*.py')) + [ROOT / 'docs/m010a-preregistration.md']
    return files + list((ROOT / 'scripts').glob('m010*.py'))


def prepare(destination):
    destination = isolated_output(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('M010_PREPARE_REQUIRES_EMPTY_DESTINATION')
    destination.mkdir(parents=True, exist_ok=True)
    registry = parent_registry()
    with access_audit(reads=[ROOT / 'src']) as access:
        scenarios = generate(registry)
        order = schedule(scenarios)
        requests = {(s['id'], arm): render(s, arm) for s in scenarios for arm in ('F0', 'F1', 'F2')}
    audit = {'passed': all(e['allowed'] and not e['write'] for e in access['events']),
             'operations': access['events'], 'allowed_read_roots': ['src'],
             'generator_uses_benchmark_loader': False, 'runner_calls': 0, 'research_inference': 0}
    artifacts = {
        'preregistration.json': {'configuration': configuration(), 'mutation_schema': mutation_schema(),
            'mutation_rules': shared_rules(), 'common_system': COMMON_SYSTEM, 'suffixes': SUFFIX,
            'synthetic': {'generator': GENERATOR, 'profiles': PROFILES, 'remaining': REMAINING},
            'human_spec_sha256': sha(ROOT / 'docs/m010a-preregistration.md'),
            'historical_anchors': verify_anchors(), 'freeze_python': platform.python_version()},
        'parents.json': registry, 'scenarios.json': scenarios, 'schedule.json': order,
        'mutation-schema.json': mutation_schema(), 'tool-schema.json': tool_schema(),
        'f0-parity.json': historical_parity(), 'access-audit.json': audit,
        'probe-request.json': probe_request(),
    }
    for name, value in artifacts.items():
        atomic_write(destination / name, canonical(value))
    sizes = {}
    for (sid, arm), payload in requests.items():
        raw = canonical(payload)
        atomic_write(destination / 'requests' / (sid + '-' + arm + '.json'), raw)
        sizes[sid + ':' + arm] = len(raw)
    size_report = {'all_scenario_requests': sizes, 'probe_bytes': len(canonical(probe_request())),
        'maximum_bytes': {arm: max(size for key, size in sizes.items() if key.endswith(':' + arm))
                          for arm in ('F0', 'F1', 'F2')}, 'cap': 16384,
        'scope': 'exact maximum over all requests possible under the immutable 24-scenario/B0-B1 registry',
        'all_passed': all(size <= 16384 for size in sizes.values()),
        'f2_offline_feasible': all(size <= 16384 for key, size in sizes.items() if key.endswith(':F2')),
        'probe_executed': False}
    atomic_write(destination / 'request-sizes.json', canonical(size_report))
    files = {p.relative_to(destination).as_posix(): sha(p) for p in sorted(destination.rglob('*')) if p.is_file()}
    value = {'format': 'm010-preparation-1', 'files': files, 'schedule_hash': order['hash'],
             'research_inference': 0, 'runner_calls': 0, 'sealed': False}
    atomic_write(destination / 'preparation.json', canonical(value))
    return {**value, 'hash': digest(value), 'request_sizes': size_report}


def regression_gate(test_evidence):
    """Only the explicitly authorized protected-boundary deferrals are admissible."""
    historical = test_evidence.get('historical_regression', {})
    deferred = historical.get('deferred', [])
    common = (historical.get('passed_permitted_tests') is True
              and not historical.get('errors') and not historical.get('failures')
              and historical.get('research_inference') == 0
              and historical.get('runner_research_calls') == 0
              and test_evidence.get('deferred_tests') == len(deferred))
    if not common:
        return False
    if not deferred:
        return test_evidence.get('historical_tests_passed') is True
    return (test_evidence.get('historical_tests_passed') is False
            and test_evidence.get('historical_permitted_tests_passed') is True
            and test_evidence.get('deferral_authorization') == 'user-approved-protected-boundary-deferrals'
            and all(isinstance(row, (list, tuple)) and len(row) == 2
                    and isinstance(row[1], str) and row[1].startswith('M010_REGRESSION_BOUNDARY:')
                    for row in deferred))


def seal(prepared, test_evidence):
    """Freeze with full test receipts, including any explicitly authorized deferrals."""
    prepared = isolated_output(prepared)
    new = test_evidence.get('new_tests', {})
    if (test_evidence.get('new_tests_passed') is not True or not regression_gate(test_evidence)
            or test_evidence.get('runner_calls') != 0 or test_evidence.get('research_inference') != 0
            or new.get('passed') is not True or new.get('source_drift') is not False
            or new.get('errors') or new.get('failures') or new.get('runner_calls') != 0
            or new.get('research_inference') != 0 or new.get('operational_probe_executed') is not False):
        raise ValueError('M010_FREEZE_TEST_GATE')
    tested = {p.relative_to(ROOT).as_posix(): sha(p) for p in trusted_sources() if p.suffix == '.py'}
    if new.get('tested_source_hashes') != tested:
        raise ValueError('M010_FREEZE_TESTED_SOURCE_DRIFT')
    preparation = json.loads((prepared / 'preparation.json').read_bytes())
    for name, expected in preparation['files'].items():
        if sha(prepared / name) != expected:
            raise ValueError('M010_PREPARATION_DRIFT')
    repo_files = trusted_sources()
    value = {'format': 'm010-freeze-1', 'study': 'M0.10A/1', 'milestone': 'M0.10A-I',
        'python_version': platform.python_version(), 'preparation_hash': digest(preparation),
        'prepared_files': preparation['files'],
        'source_files': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(repo_files)},
        'historical_anchors': verify_anchors(), 'test_evidence': test_evidence,
        'research_inference': 0, 'runner_calls': 0, 'probe_executed': False}
    manifest = {**value, 'hash': digest(value)}
    atomic_write(prepared / 'freeze.json', canonical(manifest))
    return manifest


def verify_sources(manifest):
    value = {k: v for k, v in manifest.items() if k != 'hash'}
    if digest(value) != manifest['hash']:
        raise ValueError('M010_FREEZE_HASH')
    if set(manifest['source_files']) != {p.relative_to(ROOT).as_posix() for p in trusted_sources()}:
        raise ValueError('M010_FREEZE_SOURCE_ALLOWLIST')
    for name, expected in manifest['source_files'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('M010_SOURCE_DRIFT:' + name)
    verify_anchors()
    return manifest


def verify(prepared):
    prepared = isolated_output(prepared)
    manifest = json.loads((prepared / 'freeze.json').read_bytes())
    verify_sources(manifest)
    for name, expected in manifest['prepared_files'].items():
        path = (prepared / name).resolve()
        if not path.is_relative_to(prepared):
            raise ValueError('M010_FREEZE_PATH')
        if sha(path) != expected:
            raise ValueError('M010_FREEZE_ARTIFACT_DRIFT:' + name)
    verify_anchors()
    return manifest
