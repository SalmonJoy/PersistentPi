"""Content-addressed artifacts and portable content-only checkpoints."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from .contracts import CheckpointRef, canonical


def is_link(path):
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def file_map(folder):
    folder = Path(folder)
    if not folder.is_dir() or is_link(folder):
        raise ValueError('Expected a non-linked directory')
    result = {}
    for path in sorted(Path(folder).rglob('*')):
        if is_link(path):
            raise ValueError('Links/reparse points are not allowed in fixture workspaces')
        if path.is_file():
            result[path.relative_to(folder).as_posix()] = path.read_bytes()
    return result


def relative_name(name):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name or '\x00' in name:
        raise ValueError('Invalid relative path')
    if any(part in ('', '.', '..') for part in name.split('/')):
        raise ValueError('Path traversal/absolute paths are forbidden')
    return name


def atomic_write(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def bounded_text(raw, limit):
    text = raw[:limit].decode('utf-8', errors='replace')
    encoded = text.encode('utf-8')
    return encoded[:limit].decode('utf-8', errors='ignore'), len(raw) > limit or len(encoded) > limit


class Artifacts:
    def __init__(self, store):
        self.store = store
        self.folder = store.state / 'artifacts'
        self.folder.mkdir(exist_ok=True)

    def put(self, data: bytes, kind='blob', visibility='research'):
        key = hashlib.sha256(data).hexdigest()
        path = self.folder / key
        if path.exists():
            if path.read_bytes() != data:
                raise ValueError('Existing artifact is corrupted')
        else:
            atomic_write(path, data)
        with self.store.db:
            self.store.db.execute('INSERT OR IGNORE INTO artifacts VALUES(?,?,?,?,?)',
                                  (key, kind, path.relative_to(self.store.state).as_posix(), len(data), visibility))
        return key

    def get(self, key):
        if len(key) != 64 or any(c not in '0123456789abcdef' for c in key):
            raise ValueError('Invalid artifact reference')
        raw = (self.folder / key).read_bytes()
        if hashlib.sha256(raw).hexdigest() != key:
            raise ValueError('Artifact checksum failed')
        return raw

    def checkpoint(self, workspace, parent=None):
        files = {name: self.put(raw, 'workspace_file', 'public') for name, raw in file_map(workspace).items()}
        key = self.put(canonical({'checkpoint_version': 1, 'files': files}), 'checkpoint', 'public')
        return CheckpointRef(key, parent)

    def restore(self, reference, destination):
        destination = Path(destination)
        allowed = [self.store.state / kind for kind in ('workspaces', 'evaluations')]
        resolved = destination.resolve()
        if not any(resolved.is_relative_to(root) and resolved != root for root in allowed):
            raise ValueError('Restore destination must be Supervisor-owned')
        for parent in (destination, *destination.parents):
            if parent.exists() and is_link(parent):
                raise ValueError('Linked restore destination')
        data = json.loads(self.get(reference.hash))
        if data.get('checkpoint_version') != 1:
            raise ValueError('Unsupported checkpoint version')
        files = {relative_name(name): self.get(blob) for name, blob in data['files'].items()}
        if destination.exists():
            file_map(destination)
            for path in destination.iterdir():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        destination.mkdir(parents=True, exist_ok=True)
        for name, raw in files.items():
            path = destination / name
            atomic_write(path, raw)
