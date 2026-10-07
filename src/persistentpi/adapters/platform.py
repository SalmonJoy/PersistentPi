"""Subprocess lifetime controls are separate from execution isolation."""
from dataclasses import dataclass
import ctypes
import os
import platform
import signal
import subprocess
import threading
import time


def process_identity(pid):
    if os.name == 'nt':
        from ctypes import wintypes as w
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
        kernel.OpenProcess.restype = w.HANDLE
        kernel.GetProcessTimes.argtypes = [w.HANDLE, ctypes.POINTER(w.FILETIME), ctypes.POINTER(w.FILETIME), ctypes.POINTER(w.FILETIME), ctypes.POINTER(w.FILETIME)]
        kernel.CloseHandle.argtypes = [w.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return None
        times = [w.FILETIME() for _ in range(4)]
        try:
            if not kernel.GetProcessTimes(handle, *(ctypes.byref(t) for t in times)):
                return None
            return f'windows:{times[0].dwHighDateTime}:{times[0].dwLowDateTime}'
        finally:
            kernel.CloseHandle(handle)
    try:
        from pathlib import Path
        raw = Path(f'/proc/{pid}/stat').read_text()
        return 'linux:' + raw.rsplit(')', 1)[1].split()[19]
    except (OSError, IndexError):
        return None


def hardware():
    return {'system': platform.system(), 'release': platform.release(), 'machine': platform.machine(),
            'python': platform.python_version(), 'logical_cpus': os.cpu_count(),
            'ram_bytes': None, 'temperature_c': None,
            'measurement_kind': 'observed', 'os_sandbox': False, 'network_confinement': False,
            'ram_enforcement': False, 'disk_hard_limit': False}


def owner_state(pid, identity):
    if os.name == 'nt':
        from ctypes import wintypes as w
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
        kernel.OpenProcess.restype = w.HANDLE
        kernel.GetExitCodeProcess.argtypes = [w.HANDLE, ctypes.POINTER(w.DWORD)]
        kernel.CloseHandle.argtypes = [w.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return 'dead' if ctypes.get_last_error() == 87 else 'unknown'
        try:
            code = w.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                return 'unknown'
            if code.value != 259:
                return 'dead'
        finally:
            kernel.CloseHandle(handle)
    else:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return 'dead'
        except PermissionError:
            return 'unknown'
    current = process_identity(pid)
    if current is None or identity is None:
        return 'unknown'
    return 'alive' if current == identity else 'dead'


class WindowsJob:
    def __init__(self, process):
        from ctypes import wintypes as w
        class Basic(ctypes.Structure):
            _fields_ = [('per_process_time', ctypes.c_longlong), ('per_job_time', ctypes.c_longlong),
                        ('flags', w.DWORD), ('min_working_set', ctypes.c_size_t), ('max_working_set', ctypes.c_size_t),
                        ('active_process_limit', w.DWORD), ('affinity', ctypes.c_size_t),
                        ('priority', w.DWORD), ('scheduling', w.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
        class Extended(ctypes.Structure):
            _fields_ = [('basic', Basic), ('io', IO), ('process_memory', ctypes.c_size_t),
                        ('job_memory', ctypes.c_size_t), ('peak_process_memory', ctypes.c_size_t), ('peak_job_memory', ctypes.c_size_t)]
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = w.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
        self.kernel.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        self.kernel.TerminateJobObject.argtypes = [w.HANDLE, w.UINT]
        self.kernel.CloseHandle.argtypes = [w.HANDLE]
        self.handle = self.kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise OSError(ctypes.get_last_error(), 'CreateJobObject failed')
        limits = Extended()
        limits.basic.flags = 0x2000  # KILL_ON_JOB_CLOSE, including descendant processes.
        if not self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            self.close()
            raise OSError(ctypes.get_last_error(), 'Job lifetime limit failed')
        if not self.kernel.AssignProcessToJobObject(self.handle, int(process._handle)):
            self.close()
            raise OSError(ctypes.get_last_error(), 'Job assignment failed')

    def terminate(self):
        self.kernel.TerminateJobObject(self.handle, 1)

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


@dataclass(frozen=True)
class ProcessResult:
    outcome: str
    exit_code: int | None
    duration: float
    output: str
    truncated: bool
    cleanup: str
    cleanup_error: str | None


def execute(argv, cwd, timeout, output_limit, cancelled=lambda: False):
    if not isinstance(argv, (list, tuple)) or not argv or any(not isinstance(a, str) for a in argv):
        raise ValueError('Execution requires an argument vector')
    began = time.monotonic()
    retained = bytearray()
    total = [0]
    environment = {k: v for k, v in os.environ.items() if k.upper() in ('SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'PATH', 'LANG')}
    environment.update(PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0', PYTHONUTF8='1')
    proc = subprocess.Popen(argv, cwd=cwd, shell=False, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=environment,
                            start_new_session=os.name != 'nt',
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
    job, cleanup, cleanup_error = None, 'posix_process_group', None
    if os.name == 'nt':
        try:
            job = WindowsJob(proc)
            cleanup = 'windows_job_object'
        except OSError as exc:
            proc.kill()
            proc.wait(timeout=5)
            proc.stdout.close()
            return ProcessResult('error', proc.returncode, time.monotonic() - began,
                                 '', False, 'windows_job_assignment_failed', str(exc))

    def drain():
        while True:
            block = proc.stdout.read(4096)
            if not block:
                break
            total[0] += len(block)
            retained.extend(block[:max(0, output_limit - len(retained))])

    thread = threading.Thread(target=drain, daemon=True)
    thread.start()

    def terminate():
        if job is not None:
            job.terminate()
        elif os.name == 'nt':
            subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True, timeout=5)
        else:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    outcome = 'error'
    try:
        while proc.poll() is None:
            if cancelled():
                outcome = 'cancelled'
                terminate()
                break
            if time.monotonic() - began >= timeout:
                outcome = 'timeout'
                terminate()
                break
            time.sleep(.01)
        else:
            outcome = 'pass' if proc.returncode == 0 else 'fail'
        proc.wait(timeout=5)
    finally:
        # A test that exits while leaving children must not leak those children.
        if job is not None:
            job.close()
        elif os.name != 'nt':
            terminate()
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
        thread.join(timeout=5)
        proc.stdout.close()
    from ..artifacts import bounded_text
    output, truncated = bounded_text(retained, output_limit)
    return ProcessResult(outcome, proc.returncode, time.monotonic() - began,
                         output, truncated or total[0] > output_limit, cleanup, cleanup_error)
