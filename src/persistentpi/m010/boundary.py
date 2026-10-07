"""Offline read/write audit with explicit source and evidence capabilities."""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
import sys

from .config import ROOT

_active = ContextVar('m010_access_audit', default=None)
_installed = False


def install_audit():
    global _installed
    if _installed:
        return
    def audit(event, args):
        state = _active.get()
        if state is None:
            return
        if event == 'socket.connect' and state['network']:
            return
        if event in ('socket.connect', 'subprocess.Popen', 'os.system'):
            raise PermissionError('M010_OFFLINE_CAPABILITY:' + event)
        if event not in ('open', 'sqlite3.connect'):
            return
        if isinstance(args[0], int):
            return
        path = Path(args[0]).resolve()
        write = event == 'sqlite3.connect'
        if event == 'open':
            mode = args[1]
            flags = args[2]
            write = (isinstance(mode, str) and any(x in mode for x in 'wax+')) or bool(flags and flags & (1 | 2 | 64 | 512))
        allowed = state['writes'] if write else state['reads'] + state['writes']
        passed = any(path == p or (p.is_dir() and path.is_relative_to(p)) for p in allowed)
        state['events'].append({'path': str(path), 'write': write, 'allowed': passed})
        if not passed:
            raise PermissionError('M010_PATH_CAPABILITY:' + str(path))
    sys.addaudithook(audit)
    _installed = True


@contextmanager
def access_audit(reads=(), writes=(), network=False):
    install_audit()
    state = {'reads': tuple(Path(p).resolve() for p in reads),
             'writes': tuple(Path(p).resolve() for p in writes), 'network': network, 'events': []}
    token = _active.set(state)
    try:
        yield state
    finally:
        _active.reset(token)


def isolated_output(path):
    path = Path(path).resolve()
    records = ROOT / 'docs' / 'research-records'
    if path.is_relative_to(records) and any(p.lower().startswith(('m08', 'm09')) for p in path.relative_to(records).parts):
        raise PermissionError('M010_HISTORICAL_OUTPUT')
    if any(p.lower() in ('search32', 'qualification48', 'final96', 'hidden') for p in path.parts):
        raise PermissionError('M010_PROTECTED_OUTPUT')
    return path
