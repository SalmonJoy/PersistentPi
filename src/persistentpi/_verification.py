"""Internal utilities shared by two distinct control-plane interfaces."""
from pathlib import Path
import sys
import uuid

from .adapters.platform import execute
from .artifacts import atomic_write, file_map
from .config import tree_hash
from .contracts import EvaluationResult

VERIFIER_VERSION = '0.1'


def verify(artifacts, run_id, checkpoint, tests, test_id, expected_hash,
           split, timeout, output_limit, cancelled, execution_policy='reviewed_python'):
    if tree_hash(tests) != expected_hash:
        raise ValueError('Verifier test content changed after manifest resolution')
    folder = artifacts.store.state / 'evaluations' / run_id / (split + '-' + str(uuid.uuid4()))
    artifacts.restore(checkpoint, folder)
    suite = folder / 'suite'
    suite.mkdir()
    for name, raw in file_map(tests).items():
        atomic_write(suite / name, raw)
    harness = Path(__file__).with_name('test_harness.py')
    command = (sys.executable, '-I', '-B', str(harness), str(folder), str(suite))
    if execution_policy != 'reviewed_python':
        if execution_policy != 'bounded-python-1':
            raise ValueError('Unsupported candidate execution policy')
        command += (execution_policy,)
    process = execute(command, folder, timeout, output_limit, cancelled)
    outcome = process.outcome
    if process.exit_code == 2 and outcome == 'fail':
        outcome = 'error'
    score = {'pass': 1.0, 'fail': 0.0}.get(outcome)
    return EvaluationResult(split, outcome, score, test_id, command, process.duration,
                            process.output, process.truncated, process.exit_code,
                            {'cleanup': process.cleanup, 'cleanup_error': process.cleanup_error,
                             'os_sandbox': False, 'verifier_version': VERIFIER_VERSION,
                             'execution_policy': execution_policy})


def save_evaluation(store, artifacts, run_id, attempt_id, checkpoint, evaluator_hash, result):
    record = result.to_dict()
    record['output_artifact'] = artifacts.put(record.pop('output').encode('utf-8'),
                                              'verification_output', result.split)
    from .contracts import canonical
    with store.db:
        store.db.execute('INSERT INTO evaluations VALUES(?,?,?,?,?,?,?,?,?)',
                         (str(uuid.uuid4()), run_id, attempt_id, checkpoint.hash,
                          evaluator_hash, result.split, result.outcome, result.score,
                          canonical(record).decode()))
    return record
