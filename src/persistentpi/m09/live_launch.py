"""Operational launcher utilities; task contents load only inside authorized search_live."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import time

from ..artifacts import atomic_write
from ..contracts import canonical, digest
from ..telemetry import Store
from .live_binding import AdmissionBinding, AdmittedPlanner, ResearchTransport, render_request
from .live_manager import SearchOnlyManager, TERMINALS
from .live_runtime import LiveCandidateExecutor, LocalRunnerBackend
from .live_store import SearchStore
from .disclosure import project
from .manager import proposal_contract
from .spec import compile_scaffold, references
from .storage import LIMITS, WINDOW, forecast, execution_hash, OptimizationStore
from .pro_admission import load_credential, allowance
from .admission import safe_bytes
from .live_evidence import validate_account, validate_api, EvidenceError

ROOT = Path(__file__).resolve().parents[3]
PREPARED = ROOT/'docs/research-records/m09b/prepared'
STATE = ROOT/'.local/m09c-live/state'
FREEZE = ROOT/'docs/research-records/m09cl2/launcher-freeze.json'
FILES = ('src/persistentpi/m09/live_binding.py', 'src/persistentpi/m09/live_store.py',
         'src/persistentpi/m09/live_manager.py', 'src/persistentpi/m09/live_runtime.py',
         'src/persistentpi/m09/live_launch.py', 'scripts/m09cl.py', 'scripts/m09cl_tests.py',
         'src/persistentpi/m09/live_evidence.py', 'configs/m09cl2-account-schema.json',
         'scripts/m09cl2.py', 'scripts/m09cl2_tests.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def historical_integrity(root=ROOT):
    prepared = root/'docs/research-records/m09b/prepared'
    frozen = json.loads((prepared/'freeze.json').read_bytes())
    for name, expected in frozen['code'].items():
        if sha(root/name) != expected:
            raise ValueError('Historical trusted source changed')
    admitted_sources = json.loads((root/'docs/research-records/m09cr2/artifacts/frozen/freeze.json').read_bytes())['sources']
    if any(sha(root/name) != expected for name,expected in admitted_sources.items()):
        raise ValueError('Historical admission dependency changed')
    for name, expected in frozen['files'].items():
        if name.startswith('qualification'):
            path = (prepared/name).relative_to(root).as_posix()
            ids = [subprocess.run(['git', '-C', str(root), 'rev-parse', commit+':'+path],
                                  check=True, capture_output=True).stdout for commit in ('HEAD', 'm0.9b^{commit}')]
            if ids[0] != ids[1]:
                raise ValueError('Protected metadata/object drift')
        elif sha(prepared/name) != expected:
            raise ValueError('Frozen artifact drift')
    partitions = {n: json.loads((prepared/(n+'-manifest.json')).read_bytes())
                  for n in ('search32', 'screen8', 'remaining24')}
    for m in partitions.values():
        if digest({'cohort': m['cohort'], 'rows': m['rows']}) != m['hash']:
            raise ValueError('Partition manifest hash mismatch')
    rows = {n: {r['task_id']: r for r in m['rows']} for n, m in partitions.items()}
    if (len(rows['search32']) != 32 or len(rows['screen8']) != 8 or len(rows['remaining24']) != 24
            or set(rows['screen8']) & set(rows['remaining24'])
            or {**rows['screen8'], **rows['remaining24']} != rows['search32']):
        raise ValueError('Frozen partition changed')
    return {'passed': True, 'freeze': sha(prepared/'freeze.json'),
            'partitions': {n: m['hash'] for n, m in partitions.items()},
            'protected_task_bytes_read': False, 'scientific_sources': frozen['code'],
            'admission_sources': admitted_sources}


def verify_launcher():
    record = json.loads(FREEZE.read_bytes())
    if set(record['sources']) != set(FILES) or any(sha(ROOT/n) != h for n,h in record['sources'].items()):
        raise ValueError('Launcher freeze drift')
    binding = AdmissionBinding.load(ROOT)
    if record['binding_hash'] != binding.hash or record['historical'] != historical_integrity():
        raise ValueError('Launcher/admission/history linkage drift')
    if any(sha(ROOT/name) != expected for name,expected in record['receipts'].items()):
        raise ValueError('Launcher validation receipt drift')
    parent = '50697cd91d94eea17bac4d4c9c9606545f5a5ddd'
    for name, expected in record['historical_artifacts'].items():
        original = subprocess.run(['git', '-C', str(ROOT), 'show', parent+':'+name],
                                  check=True, capture_output=True).stdout
        if hashlib.sha256(original).hexdigest() != expected or sha(ROOT/name) != expected:
            raise ValueError('Historical launcher/stop evidence drift')
    if (record['account_evidence_schema']['sha256'] != sha(ROOT/'configs/m09cl2-account-schema.json')
            or record['api_evidence_validator']['sha256'] != sha(ROOT/'src/persistentpi/m09/live_evidence.py')):
        raise ValueError('Evidence validator/schema drift')
    return record


def forecast_gate():
    path = ROOT/'docs/research-records/m09c/forecast.json'
    raw = path.read_bytes()
    original = subprocess.run(['git', '-C', str(ROOT), 'show', 'm0.9c:'+path.relative_to(ROOT).as_posix()],
                              check=True, capture_output=True).stdout
    if raw != original:
        raise ValueError('Historical forecast drift')
    saved = json.loads(raw)
    for row in saved['sources']:
        if sha(ROOT/row['path']) != row['sha256']:
            raise ValueError('Development forecast source drift')
    computed = forecast(saved['samples'])
    if not computed['passed'] or any(computed[k] != saved[k] for k in computed):
        raise ValueError('Frozen forecast gate failed')
    return {'passed': True, 'forecast_hash': sha(path), **computed}


def zero_ledger(state=None):
    # This is the future research store, distinct from labeled synthetic campaigns.
    owner = Store(STATE if state is None else state)
    try:
        rows = list(owner.db.execute('SELECT reservation_json,usage_json FROM m09_operations'))
        counts = {'planner_requests': 0, 'planner_tokens': 0, 'runner_calls': 0, 'runner_tokens': 0}
        for row in rows:
            usage = json.loads(row['usage_json'] or row['reservation_json'])
            for key in counts:
                counts[key] += usage.get(key, 0)
        if any(counts.values()) or owner.db.execute('SELECT COUNT(*) FROM m09_campaigns').fetchone()[0]:
            raise ValueError('Fresh research ledger is not empty')
        return {**counts, 'durable_database': str(owner.state/'experiments.sqlite'),
                'integrity': owner.db.execute('PRAGMA integrity_check').fetchone()[0]}
    finally:
        owner.close()


def resume_ledger(campaign_id, state=None):
    owner = Store(STATE if state is None else state)
    try:
        rows = list(owner.db.execute('SELECT * FROM m09_campaigns'))
        binding = AdmissionBinding.load(ROOT)
        if (len(rows) != 1 or rows[0]['id'] != campaign_id
                or rows[0]['config_hash'] != digest(binding.configuration())
                or json.loads(rows[0]['state_json'])['execution_hash'] != execution_hash()):
            raise ValueError('Resume identity/configuration drift')
        # Recovery requires only durable metadata, not task objects or evaluator access.
        class RecoveryView:
            db, id = owner.db, campaign_id
            def state(self):
                return json.loads(self.db.execute('SELECT state_json FROM m09_campaigns WHERE id=?',(self.id,)).fetchone()[0])
        OptimizationStore.recover(RecoveryView())
        rows = list(owner.db.execute('SELECT * FROM m09_campaigns'))
        operations = list(owner.db.execute('SELECT * FROM m09_operations WHERE campaign=?', (campaign_id,)))
        if (rows[0]['phase'] not in ('references','search') or any(o['state'] in ('started','indeterminate') for o in operations)):
            raise ValueError('No resumable unstarted search remains; preserve ambiguous receipts')
        return {'campaign_id': campaign_id, 'fresh_ledger': False, 'reset_budgets': False,
                'operations': len(operations), 'generating_requests': 0}
    finally:
        owner.close()


def dry_run(binding, output):
    configuration = binding.configuration(validation=True)
    canary = 'PRIVATE_SOURCE_CANARY_NOT_FOR_PLANNER'
    observation = project(events=[{'action': {'tool': 'edit_file', 'arguments': {
        'old': canary, 'new': canary}}, 'result': {'ok': False, 'error': 'Invalid Python syntax'},
        'hidden': canary, 'source': canary, 'expected': canary}])
    payload = render_request(binding, configuration, observation, compile_scaffold(references()['B0']),
                             [], LIMITS, proposal_contract())
    raw = canonical(payload)
    if canary.encode() in raw or b'glm-5.3' in raw:
        raise ValueError('Dry-run disclosure/model canary failed')
    record = {'transmitted': False, 'synthetic_observation': True, 'request': payload,
              'request_hash': digest(payload), 'endpoint': binding.identity['endpoint'],
              'binding_hash': binding.hash, 'renderer': configuration['operational_launch']['renderer']}
    atomic_write(Path(output), canonical(record))
    return record


def search_preflight(account_evidence, output, campaign_id=None):
    stages = {}
    try:
        return _search_preflight(account_evidence, output, campaign_id, stages)
    except Exception as error:
        known = ('Cloud identity/contract drift', 'Frozen Runner unavailable',
                 'Operational cloud request failed; payload suppressed', 'Clean repository required',
                 'Fresh research ledger is not empty', 'Launcher freeze drift')
        condition = str(error) if isinstance(error, EvidenceError) or str(error) in known else 'mandatory_check_failed'
        atomic_write(Path(output), canonical({'passed': False, 'state': 'PRIMARY_SEARCH_PREFLIGHT_BLOCKED',
                     'condition': condition, 'error_type': type(error).__name__, 'checks': stages,
                     'generating_requests': 0, 'research_executed': False}))
        raise


def _search_preflight(account_evidence, output, campaign_id, stages):
    if subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain'], check=True,
                      capture_output=True).stdout.strip():
        raise ValueError('Clean repository required')
    frozen = verify_launcher()
    binding = AdmissionBinding.load(ROOT)
    prediction = forecast_gate()
    ledger = zero_ledger() if campaign_id is None else resume_ledger(campaign_id)
    stages['frozen_integrity_and_ledger'] = True
    environment = load_credential(ROOT.parents[1]/'.env', json.loads(
        (ROOT/'docs/research-records/m09cr2/rotation-attestation.json').read_bytes()))
    transport = ResearchTransport(environment, binding)
    planner = AdmittedPlanner(binding, binding.configuration(), transport)
    account = json.loads(Path(account_evidence).read_bytes())
    safe_bytes(account,(transport._secret,))
    billing = validate_account(account, transport.pricing)
    stages['account_evidence'] = billing.to_dict()
    planner.pre_request()  # Authenticated metadata only, never chat/generation.
    admission_path = ROOT/'docs/research-records/m09cr2/admission-result.json'
    api = validate_api(binding, transport.current_identity_value, transport.authentication,
                       json.loads(admission_path.read_bytes()), sha(admission_path))
    stages['api_evidence'] = api.to_dict()
    forecast = billing.allowance
    from ..adapters.ollama import discover
    from ..m08.tokenizer import FrozenTokenizer
    expected = json.loads((PREPARED/'runner-model.json').read_bytes())
    base = json.loads((PREPARED/'reference-configurations.json').read_bytes())['A']['model']
    if discover(base) != expected['identity'] or FrozenTokenizer.installed(base).identity != expected['tokenizer']:
        raise ValueError('Frozen Runner unavailable')
    receipt = {'passed': True, 'state': 'PRIMARY_SEARCH_PREFLIGHT_READY', 'checks': stages,
               'account_evidence': billing.to_dict(), 'api_evidence': api.to_dict(),
               'generating_requests': 0, 'binding_hash': binding.hash,
               'launcher_hash': digest(frozen), 'configuration_hash': digest(binding.configuration()),
               'account_evidence_hash': digest(account), 'forecast': forecast,
               'ledger': ledger, 'development_forecast': prediction,
               'target': 'SEARCH_ONLY', 'terminal_states': TERMINALS,
               'qualification_material_capability': False, 'final_hidden_capability': False}
    atomic_write(Path(output), canonical(receipt))
    return receipt


@contextmanager
def exclusive_launch():
    STATE.parent.mkdir(parents=True, exist_ok=True)
    path = STATE.parent/'launcher.lock'
    # Never discard a lock on the basis of elapsed time or restart an ambiguous send.
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, canonical({'pid': os.getpid(), 'target': 'SEARCH_ONLY'}))
        os.fsync(fd)
        yield
    finally:
        os.close(fd)
        path.unlink()


def recover_lock():
    """Non-generating recovery only after the recorded launcher owner is provably gone."""
    path = STATE.parent/'launcher.lock'
    raw = path.read_bytes()
    identity = json.loads(raw)
    pid = identity.get('pid')
    if type(pid) is not int or pid <= 0 or identity.get('target') != 'SEARCH_ONLY':
        raise ValueError('Invalid lock identity; manual inspection required')
    if os.name == 'nt':
        import ctypes
        api = ctypes.WinDLL('kernel32',use_last_error=True)
        api.OpenProcess.restype = ctypes.c_void_p
        handle = api.OpenProcess(0x1000,False,pid)
        if handle:
            api.CloseHandle.argtypes = [ctypes.c_void_p]
            api.CloseHandle(handle)
            raise ValueError('Recorded owner exists; do not recover')
        if ctypes.get_last_error() != 87:
            raise ValueError('Cannot prove recorded owner absent')
    else:
        try:
            os.kill(pid,0)
        except ProcessLookupError:
            pass
        else:
            raise ValueError('Recorded owner exists; do not recover')
    if path.read_bytes() != raw:
        raise ValueError('Lock changed during recovery')
    # This does not reset or reopen any experiment operation. Resume still runs recover().
    receipt = {'owner_absent':True,'generating_requests':0,'ledger_modified':False,'lock_pid':pid}
    atomic_write(STATE.parent/('lock-recovery-'+str(time.time_ns())+'.json'),canonical(receipt))
    path.unlink()
    return receipt


def execute_search(store, planner, evaluator, binding, output):
    """The shared production/mock orchestration, with an unconditional terminal barrier."""
    manager = SearchOnlyManager(store, planner, evaluator, binding, mode='SEARCH_ONLY')
    try:
        return manager.run()
    finally:
        store.assert_barrier()
        from .export import export
        export(store, output)


def search_live(account_evidence, authorized=False, campaign_id=None, resume_idle=False):
    if authorized is not True:
        raise ValueError('Explicit primary-search authorization required')
    with exclusive_launch():
        preflight = search_preflight(account_evidence, STATE.parent/'preflight.json', campaign_id)
        binding = AdmissionBinding.load(ROOT)
        environment = load_credential(ROOT.parents[1]/'.env', json.loads(
            (ROOT/'docs/research-records/m09cr2/rotation-attestation.json').read_bytes()))
        # Only this explicit command may load Search32, never Qualification48.
        from .cohorts import PublicTask, manifest
        search = tuple(PublicTask.from_dict(t) for t in json.loads((PREPARED/'search32-public.json').read_bytes()))
        if manifest(search, 'search')['hash'] != historical_integrity()['partitions']['search32']:
            raise ValueError('Search identity drift')
        qualification_metadata = json.loads((PREPARED/'qualification48-manifest.json').read_bytes())
        from ..m08.tokenizer import FrozenTokenizer
        expected = json.loads((PREPARED/'runner-model.json').read_bytes())
        base = json.loads((PREPARED/'reference-configurations.json').read_bytes())['A']['model']
        store = SearchStore(STATE, binding.configuration(), search, qualification_metadata, campaign_id=campaign_id)
        try:
            if resume_idle:
                store.resume_pause()
            store.decision('live_preflight', preflight)
            planner = AdmittedPlanner(binding, store.config, ResearchTransport(environment, binding))
            evaluator = LiveCandidateExecutor(lambda *_: LocalRunnerBackend(binding, base, expected['identity']),
                                               FrozenTokenizer.installed(base), base, WINDOW, binding=binding)
            return execute_search(store, planner, evaluator, binding,
                                  STATE.parent/('primary-search-'+str(time.time_ns())+'.zip'))
        finally:
            store.close()
