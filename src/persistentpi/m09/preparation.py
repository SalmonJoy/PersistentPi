"""Offline artifact preparation; deliberately no final-task loader or cloud client."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import subprocess

from ..artifacts import atomic_write
from ..contracts import canonical, digest
from .cohorts import PublicTask, exposed_search, manifest, qualification, split_search
from .parity import audit_references
from .spec import ScaffoldSpecV1, compile_scaffold, interface_catalog, references

BASELINE = '28e44ee045a69f074e800d780129bd6457d4f0cd'


def git(root, *arguments):
    return subprocess.run(['git', '-C', str(root), *arguments], check=True,
                          capture_output=True, text=True).stdout.strip()


def history_audit(root):
    # Compare tracked paths through Git, never load historical benchmark contents.
    baseline_paths = set(git(root, 'ls-tree', '-r', '--name-only', BASELINE).splitlines())
    changed = git(root, 'diff', BASELINE, '--name-only', '--', 'src', 'tests',
                  'docs/research-records/m08*', 'configs/m08*', 'scripts/m08*',
                  'migrations/001_initial.sql', 'migrations/002_feedback.sql').splitlines()
    changed = sorted(set(changed) & baseline_paths)
    if changed:
        raise ValueError('Historical files changed: ' + ','.join(changed))
    evidence = git(root, 'ls-tree', '-r', BASELINE, '--', 'docs/research-records').splitlines()
    return {'passed': True, 'baseline': BASELINE, 'head': git(root, 'rev-parse', 'HEAD'),
            'historical_tracked_changes': changed, 'baseline_evidence_git_inventory_hash': digest(evidence),
            'method': 'Git tracked-file comparison and object-name inventory; no benchmark extraction',
            'benchmark_hidden_scoring': False, 'final_contents_loaded': False}


def spec_schema():
    from .spec import FIELDS, TOOLS
    enums = {'interface': sorted(interface_catalog()['items']), 'controller': ['C0','C1','C2','C3'],
             'read_allowance': [0,1,2], 'recent_observations': list(range(5)),
             'rejection_feedback': ['generic','precise'], 'retry': ['stop','retry'],
             'stagnation': [0,2,3], 'inspect_output': [128,256,512,1024],
             'act_output': [128,256,512,1024], 'version': [1]}
    properties = {'system_text': {'type': 'string', 'maxLength': 4096},
                  'tool_descriptions': {'type': 'object', 'additionalProperties': False,
                                        'properties': {t: {'type': 'string'} for t in TOOLS}},
                  'source_preload': {'type': 'boolean'},
                  'context_fields': {'type': 'array', 'uniqueItems': True, 'items': {'enum': list(FIELDS)}},
                  'inspect_calls': {'type': 'integer', 'minimum': 1, 'maximum': 15},
                  'act_calls': {'type': 'integer', 'minimum': 1, 'maximum': 15}}
    properties.update({k: {'enum': v} for k,v in enums.items()})
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'ScaffoldSpecV1',
            'type': 'object', 'required': ['system_text'], 'additionalProperties': False,
            'properties': properties,
            '$comment': 'Trusted Python validator additionally enforces ASCII/combined4096, mandatory contexts, READ0 preload, payload prohibition and immutable ceilings.'}


def write_json(path, value):
    atomic_write(path, canonical(value))


def preparation_paths(root):
    paths = list((root/'src/persistentpi').rglob('*.py')) + list((root/'migrations').glob('*.sql'))
    paths += list((root/'tests').glob('test_*.py'))
    paths += [root/'scripts/m09b.py', root/'scripts/m09b_tests.py', root/'pyproject.toml',
              root/'configs/m09-preregistered.json', root/'docs/m09-preregistration.md',root/'docs/m09b-offline.md']
    paths += [root/'scripts'/f'm08{letter}_tests.py' for letter in 'fghi']
    return sorted(set(paths))


def prepare(root, folder):
    root, folder = Path(root), Path(folder)
    if folder.exists():
        raise ValueError('Preparation output exists; no opportunistic regeneration')
    history = history_audit(root)
    search = exposed_search(root)
    qs, certificate = qualification(search)
    screen, remaining = split_search(search)
    folder.mkdir(parents=True)
    for name, cohort, tasks in (('search32','search',search),('screen8','screen',screen),
                                ('remaining24','remaining',remaining),('qualification48','qualification',qs)):
        write_json(folder/(name+'-manifest.json'), manifest(tasks, cohort))
    write_json(folder/'search32-public.json', [t.to_dict() for t in search])
    write_json(folder/'qualification48-public.json', [t.to_dict() for t in qs])
    write_json(folder/'qualification-certification.json', certificate)
    write_json(folder/'references.json', {name: {'scaffold_id': compile_scaffold(spec).scaffold_id,
               'spec': spec.to_dict(), 'complexity': compile_scaffold(spec).complexity()}
               for name,spec in references().items()})
    write_json(folder/'interface-catalog.json', interface_catalog())
    write_json(folder/'scaffold-spec-schema.json', spec_schema())
    write_json(folder/'reference-parity.json', audit_references(root))
    write_json(folder/'history-audit.json', history)
    write_json(folder/'environment.json', {'python': platform.python_version(), 'platform': platform.platform(),
               'python_dependencies': [], 'models_called': [], 'simulation': True})
    for name, original in (('preregistration.md','docs/m09-preregistration.md'),
                           ('preregistration.json','configs/m09-preregistered.json'),
                           ('runner-model.json','docs/research-records/m08d/model.json'),
                           ('reference-configurations.json','docs/research-records/m08d/configs.json'),
                           ('schema.sql','migrations/003_optimization.sql')):
        atomic_write(folder/name, (root/original).read_bytes())
    files = {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(folder.rglob('*')) if p.is_file()}
    code = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in preparation_paths(root)}
    frozen = {'version':'m09b-freeze-1','protocol':'0.6','code_commit':git(root,'rev-parse','HEAD'),
              'files':files,'code':code,'search_hash':manifest(search,'search')['hash'],
              'qualification_hash':manifest(qs,'qualification')['hash'],
              'cloud_backend_identity_frozen':False,'live_inference':False,'final_contents_loaded':False,
              'benchmark_hidden_scoring':False}
    write_json(folder/'freeze.json', frozen)
    return {'folder':str(folder), 'freeze_sha256':digest(frozen), 'search_hash':frozen['search_hash'],
            'qualification_hash':frozen['qualification_hash'], 'certified':certificate['passed']}


def verify_freeze(root, folder):
    root, folder = Path(root), Path(folder)
    frozen = json.loads((folder/'freeze.json').read_bytes())
    if frozen['protocol'] != '0.6' or frozen['cloud_backend_identity_frozen']:
        raise ValueError('Freeze policy mismatch')
    if set(frozen['code']) != {p.relative_to(root).as_posix() for p in preparation_paths(root)}:
        raise ValueError('Trusted code inventory drift')
    from ..artifacts import relative_name
    for base, mapping in ((folder, frozen['files']), (root, frozen['code'])):
        for name,key in mapping.items():
            relative_name(name)
            target = (base/name).resolve()
            if not target.is_relative_to(base.resolve()) or hashlib.sha256(target.read_bytes()).hexdigest() != key:
                raise ValueError('Freeze checksum mismatch: '+name)
    search, qs = load_cohorts(folder)
    if manifest(search,'search')['hash'] != frozen['search_hash'] or manifest(qs,'qualification')['hash'] != frozen['qualification_hash']:
        raise ValueError('Frozen cohort reconstruction mismatch')
    screen, remaining = split_search(search)
    for name,cohort,tasks in (('search32','search',search),('screen8','screen',screen),
                             ('remaining24','remaining',remaining),('qualification48','qualification',qs)):
        if json.loads((folder/(name+'-manifest.json')).read_bytes()) != manifest(tasks,cohort):
            raise ValueError('Frozen partition mismatch')
    return {'passed':True,'freeze_sha256':digest(frozen),'search_tasks':len(search),'qualification_tasks':len(qs),
            'final_contents_loaded':False,'benchmark_hidden_scoring':False}


def load_cohorts(folder):
    folder = Path(folder)
    return tuple(PublicTask.from_dict(t) for t in json.loads((folder/'search32-public.json').read_bytes())), \
           tuple(PublicTask.from_dict(t) for t in json.loads((folder/'qualification48-public.json').read_bytes()))
