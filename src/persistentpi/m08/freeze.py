"""Checksummed research lock; trusted manager validates it before execution."""
import hashlib
import json
from pathlib import Path
import subprocess

from ..artifacts import atomic_write
from ..contracts import canonical, digest
from ..adapters.platform import hardware


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze_paths(root):
    paths = []
    for directory in ('src','migrations','tests'):
        paths += [p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    paths += [root/'configs/m08-preregistered.json', root/'docs/m08-preregistration.md',
              root/'docs/protocol.md', root/'scripts/m08.py']
    return sorted(set(paths))


class Freeze:
    def __init__(self, path, root, expected_hash):
        self.path,self.root = Path(path),Path(root).resolve()
        self.hash = checksum(self.path)
        if self.hash != expected_hash:
            raise ValueError('Freeze manifest differs from expected hash')
        self.data = json.loads(self.path.read_bytes())
        if self.data.get('freeze_version')!=1 or self.data.get('protocol_version')!='0.5':
            raise ValueError('Unsupported M0.8 freeze')
        self.commit = self.data['implementation_commit']
        self.validate()

    def validate(self):
        if checksum(self.path)!=self.hash:
            raise ValueError('Freeze manifest changed during execution')
        expected_names = {p.relative_to(self.root).as_posix() for p in freeze_paths(self.root)}
        if set(self.data['files']) != expected_names:
            raise ValueError('Frozen implementation file set changed')
        for name,expected in self.data['files'].items():
            if checksum(self.root/name)!=expected:
                raise ValueError('Frozen research asset changed: '+name)
        plan = json.loads((self.root/'configs/m08-preregistered.json').read_bytes())
        if digest(plan)!=self.data['preregistration_hash']:
            raise ValueError('Preregistration does not match frozen expected value')
        if self.data.get('canonical_preregistration'):
            raw = (self.root/self.data['canonical_preregistration']).read_bytes()
            if raw!=canonical(plan):
                raise ValueError('Canonical preregistration snapshot differs from frozen design')
        return plan


def create(root, output, suite_manifest, certification, tokenizer):
    root = Path(root).resolve()
    output = Path(output)
    if output.exists():
        raise ValueError('Freeze destination exists; replacement requires a new version')
    status = subprocess.run(['git','-C',str(root),'status','--porcelain'],capture_output=True,text=True,check=True).stdout
    if status.strip():
        raise ValueError('Freeze creation requires a clean implementation commit')
    commit = subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
    plan = json.loads((root/'configs/m08-preregistered.json').read_bytes())
    output = output.resolve()
    if not output.is_relative_to(root):
        raise ValueError('Freeze artifacts must remain in the research repository')
    snapshot = output.parent/'preregistration.json'
    certification_path = output.parent/'fixture-certification.json'
    if snapshot.exists() or certification_path.exists():
        raise ValueError('Preregistration/certification snapshots already exist')
    atomic_write(snapshot,canonical(plan))
    atomic_write(certification_path,canonical(certification))
    data = {'freeze_version':1,'protocol_version':'0.5','implementation_commit':commit,
            'baseline_commit':plan['baseline_commit'],'preregistration_hash':digest(plan),
            'human_preregistration_sha256':checksum(root/'docs/m08-preregistration.md'),
            'files':{p.relative_to(root).as_posix():checksum(p) for p in freeze_paths(root)},
            'suite_manifest':suite_manifest,'suite_manifest_hash':digest(suite_manifest),
            'certification_hash':digest(certification),'tokenizer_identity':tokenizer.identity,
            'canonical_preregistration':snapshot.relative_to(root).as_posix(),
            'certification_path':certification_path.relative_to(root).as_posix(),
            'execution_profile':hardware(),
            'live_calibration':'pending','final_evaluation':'not_run'}
    atomic_write(output,canonical(data))
    return {'path':str(output),'sha256':checksum(output),'preregistration_hash':digest(plan),
            'implementation_commit':commit,'certified_tasks':certification['task_count']}
