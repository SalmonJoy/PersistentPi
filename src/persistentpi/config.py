"""Resolve reviewed fixture configuration into immutable experiment manifests."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
import subprocess
import tomllib

from .artifacts import file_map, relative_name
from .adapters.platform import hardware
from .contracts import Budget, TaskView, digest
from .tools import TOOLS, TOOLSET_VERSION, authorize
from .contracts import ActionRequest


def project_root():
    return Path(__file__).resolve().parents[2]


def git_state(root):
    def call(*args):
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    commit = call('rev-parse', 'HEAD')
    status = call('status', '--porcelain', '--untracked-files=all')
    tracked = call('ls-files', '--cached', '--others', '--exclude-standard', '-z')
    files = {}
    if tracked:
        for name in tracked.split('\x00'):
            if name and (root / name).is_file():
                files[name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
    return {'commit': commit, 'dirty': bool(status) if status is not None else True,
            'dirty_state_hash': digest({'status': status, 'files': files}) if status else None,
            'files': files}


@dataclass(frozen=True)
class TaskSpec:
    view: TaskView
    source: Path
    public_tests: Path
    hidden_tests: Path
    steps: tuple
    public_hash: str
    hidden_hash: str
    hash: str
    source_hash: str
    execution_policy: str = 'reviewed_python'


@dataclass(frozen=True)
class Resolved:
    manifest: dict
    tasks: tuple[TaskSpec, ...]
    attempt_budgets: tuple[int, ...]
    budget_config: dict
    mode: str
    seed: int
    replicate: int
    authored: bytes


def tree_hash(folder):
    return digest({name: hashlib.sha256(raw).hexdigest() for name, raw in file_map(folder).items()})


def resolve(path, root=None, mode='development', replicate=None):
    root = Path(root or project_root()).resolve()
    path = Path(path).resolve()
    authored = path.read_bytes()
    config = tomllib.loads(authored.decode('utf-8'))
    protocol = config.get('experiment', {}).get('protocol_version')
    real = protocol in ('0.2', '0.3', '0.4')
    required = {'experiment', 'scaffold', 'harness_test_limits'} | ({'model'} if real else set()) | ({'interface'} if protocol in ('0.3', '0.4') else set())
    if set(config) != required:
        raise ValueError('Unknown or missing experiment sections')
    experiment, scaffold = config['experiment'], config['scaffold']
    if set(experiment) != {'protocol_version', 'execution_mode', 'tasks', 'attempt_budgets', 'seed', 'replicate'}:
        raise ValueError('Unknown or missing experiment fields')
    if set(scaffold) - {'scaffold_id', 'parent_scaffold_id', 'scaffold_version'} or not {'scaffold_id','scaffold_version'} <= set(scaffold):
        raise ValueError('Invalid scaffold identity')
    expected_mode = 'bounded_python_smoke' if real else 'reviewed_scripted_fixture'
    if protocol not in ('0.1', '0.2', '0.3', '0.4') or experiment['execution_mode'] != expected_mode:
        raise ValueError('Unsupported protocol/execution policy combination')
    if mode not in ('development', 'formal'):
        raise ValueError('Invalid run mode')
    seed = experiment['seed']
    replicate = experiment['replicate'] if replicate is None else replicate
    if type(seed) is not int or type(replicate) is not int or replicate < 0:
        raise ValueError('Invalid seed/replicate')
    budgets = tuple(experiment['attempt_budgets'])
    if not budgets or len(set(budgets)) != len(budgets):
        raise ValueError('Attempt budgets must be nonempty and unique')
    limits = config['harness_test_limits']
    for count in budgets:
        Budget(max_attempts=count, **limits)
    task_ids = experiment['tasks']
    if not task_ids or len(set(task_ids)) != len(task_ids):
        raise ValueError('Tasks must be nonempty and unique')
    specs = []
    model = {'id': 'scripted-v1', 'usage_kind': 'simulated', 'weights': None}
    if real:
        model = validate_model(config['model'])
    interface = None
    if protocol in ('0.3', '0.4'):
        from .interfaces import PROTOCOLS, registry
        interface = config['interface']
        if set(interface) != {'output_protocol', 'edit_primitive'} or interface['output_protocol'] not in PROTOCOLS:
            raise ValueError('Invalid interface configuration')
        registry(interface['edit_primitive'])
        model = {**model, **interface, 'prompt_version': interface['output_protocol'] +
                 ('-E1' if interface['edit_primitive'] == 'E1' else '')}
    if any(not isinstance(v, str) or not v for v in scaffold.values()):
        raise ValueError('Scaffold identities must be nonempty strings')
    for task_id in task_ids:
        if not isinstance(task_id, str) or not task_id or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in task_id):
            raise ValueError('Invalid fixture identifier')
        folder = root / 'fixtures' / task_id
        metadata = tomllib.loads((folder / 'task.toml').read_text(encoding='utf-8'))
        task_fields = {'fixture_version','description','editable_paths','public_test_id'}
        if set(metadata) != task_fields | ({'execution_policy'} if real else {'script'}):
            raise ValueError('Invalid task manifest')
        if not real and metadata['script'] != 'script.toml':
            raise ValueError('Only fixture-local reviewed scripts are supported')
        if real and metadata['execution_policy'] != 'bounded-python-1':
            raise ValueError('Real model tasks require bounded-python-1 execution')
        steps = () if real else tuple(tomllib.loads((folder / 'script.toml').read_text(encoding='utf-8'))['steps'])
        for step in steps:
            if set(step) - {'action','requires_public_outcome'}:
                raise ValueError('Invalid script step')
            action = ActionRequest.from_dict(step['action'])
            if action.tool != 'finish':
                authorize(action)
        source, public, hidden = folder / 'workspace', folder / 'public_tests', folder / 'hidden_tests'
        editable = tuple(metadata['editable_paths'])
        for name in (*editable, *file_map(source), *file_map(public), *file_map(hidden)):
            relative_name(name)
        paths = tuple(sorted(file_map(source))) + tuple('public_tests/' + x for x in sorted(file_map(public)))
        if not editable or any(p not in paths or not p.startswith('src/') for p in editable):
            raise ValueError('Editable paths must name fixture source files')
        public_hash, hidden_hash = tree_hash(public), tree_hash(hidden)
        source_hash = tree_hash(source)
        identity = digest({'metadata': metadata, 'source': source_hash, 'public': public_hash,
                           'hidden': hidden_hash, 'steps': steps})
        view = TaskView(task_id, metadata['description'], editable, paths,
                        metadata['public_test_id'], metadata['fixture_version'])
        specs.append(TaskSpec(view, source, public, hidden, steps, public_hash, hidden_hash, identity,
                              source_hash, metadata.get('execution_policy', 'reviewed_python')))
    code_hashes = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for directory in ('src', 'migrations') for p in sorted((root / directory).rglob('*'))
                   if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    strategy_files = {k: v for k, v in code_hashes.items()
                      if k.endswith(('/runner.py', '/adapters/scripted.py', '/adapters/ollama.py', '/prompts.py', '/interfaces.py'))}
    scaffold_identity = {**scaffold, 'parent_scaffold_id': scaffold.get('parent_scaffold_id'),
                         'scaffold_hash': digest({'identity': scaffold, 'strategy': strategy_files})}
    provenance = git_state(root)
    if mode == 'formal' and (not provenance['commit'] or provenance['dirty']):
        raise ValueError('Formal runs require a clean Git commit')
    manifest = {'manifest_version': 1, 'protocol_version': protocol,
                'execution_mode': experiment['execution_mode'], 'mode': mode,
                'scaffold': scaffold_identity, 'seed': seed, 'replicate': replicate,
                'attempt_budgets': budgets, 'harness_test_limits': limits,
                'tasks': [{'task_id': s.view.task_id, 'task_hash': s.hash, 'fixture_version': s.view.fixture_version,
                           'public_hash': s.public_hash, 'hidden_hash': s.hidden_hash,
                           'source_hash': s.source_hash, 'execution_policy': s.execution_policy} for s in specs],
                'model': model,
                'planner': None, 'memory_snapshot': None, 'tools': TOOLS, 'toolset_version': TOOLSET_VERSION,
                'code_hashes': code_hashes, 'harness_hash': digest(code_hashes), 'git': provenance,
                'execution_profile': hardware(), 'authored_config_hash': digest(config)}
    if interface:
        manifest['interface'] = interface
        manifest['tools'] = registry(interface['edit_primitive'])
        manifest['toolset_version'] = '0.3-' + interface['edit_primitive']
    return Resolved(manifest, tuple(specs), budgets, limits, mode, seed, replicate, authored)


def validate_model(value):
    from .adapters.ollama import endpoint_parts
    from .prompts import PROMPT_VERSION, CONTEXT_VERSION
    required = {'backend', 'model', 'endpoint', 'temperature', 'seed', 'num_ctx', 'num_predict',
                'timeout_seconds', 'keep_alive', 'context', 'repair', 'label'}
    if set(value) != required or value['backend'] != 'ollama' or value['repair'] is not False:
        raise ValueError('Invalid model configuration; only local Ollama without repair is supported')
    endpoint_parts(value['endpoint'])
    if not isinstance(value['model'], str) or not value['model'] or value['label'] != 'development_smoke_non_baseline':
        raise ValueError('A model tag and explicit development smoke label are required')
    if type(value['seed']) is not int:
        raise ValueError('Model seed must be an integer')
    import math
    for name in ('temperature', 'timeout_seconds'):
        number = value[name]
        if type(number) not in (int, float) or not math.isfinite(number) or number < 0 or (name == 'timeout_seconds' and number == 0):
            raise ValueError('Invalid model setting: ' + name)
    for name in ('num_ctx', 'num_predict'):
        if type(value[name]) is not int or value[name] <= 0:
            raise ValueError('Invalid positive integer model setting: ' + name)
    if not isinstance(value['keep_alive'], str) or not value['keep_alive']:
        raise ValueError('keep_alive must be an explicit duration string')
    context = value['context']
    if set(context) != {'max_bytes', 'field_bytes', 'recent_observations'}:
        raise ValueError('Invalid context policy')
    if any(type(v) is not int or v <= 0 for v in context.values()):
        raise ValueError('Context limits must be positive integers')
    return {**value, 'usage_kind': 'measured', 'prompt_version': PROMPT_VERSION,
            'context_version': CONTEXT_VERSION, 'failure_taxonomy_version': '0.2'}
