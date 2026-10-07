"""Read-only replay of actual M0.8D public model requests, without inference."""
import hashlib
import json
from pathlib import Path
import sqlite3
import zipfile

from ..contracts import DecisionState, Observation, ActionRequest, ActionResult, digest
from ..m08.primitive_pilot import public_inputs
from ..m08.runtime import observation_from
from .render import controller_for, wire_request
from .spec import compile_scaffold, references


def audit_references(root):
    folder = Path(root) / 'docs/research-records/m08d'
    tasks = {t.task_id: t for t in public_inputs(root)[0]}
    configs = json.loads((folder / 'configs.json').read_bytes())
    counts, proofs = {}, []
    for reference, arm in (('B0', 'A'), ('B1', 'B')):
        configuration = compile_scaffold(references()[reference])
        with sqlite3.connect((folder / (arm + '.sqlite')).resolve().as_uri()+'?mode=ro&immutable=1', uri=True) as db, \
                zipfile.ZipFile(folder / (arm + '-research.zip')) as archive:
            db.row_factory = sqlite3.Row
            def blob(key):
                raw = archive.read('artifacts/' + key)
                if hashlib.sha256(raw).hexdigest() != key:
                    raise ValueError('Historical public artifact corrupt')
                return json.loads(raw)
            requests = 0
            for run in db.execute("SELECT * FROM runs WHERE mode='development' ORDER BY task_id"):
                task = tasks[run['task_id']]
                observations, step = [], 0
                for event in db.execute('SELECT * FROM events WHERE run_id=? ORDER BY sequence', (run['id'],)):
                    value = json.loads(event['payload_json'])
                    if event['type'] == 'decision_started':
                        step = value['window_decision']
                    if event['type'] == 'model_request':
                        recorded = blob(value['request_artifact'])['payload']
                        public = json.loads(recorded['messages'][1]['content'])
                        budget, control = public['budget'], public['control']
                        state = DecisionState(1, budget['remaining_decisions'], budget['remaining_tool_calls'], budget['remaining_tokens'], 120)
                        controller = controller_for(configuration, task.view.editable_paths)
                        controller.phase, controller.reads = control['phase'], control['successful_reads']
                        actual, _ = wire_request(configuration, task.view, observations, state, controller, configs[arm]['model'])
                        if actual != recorded:
                            raise ValueError('Historical reference request parity failed: ' + reference + ':' + run['task_id'])
                        requests += 1
                        proofs.append({'reference': reference, 'task': run['task_id'], 'request_hash': digest(actual)})
                    if event['type'] == 'action_completed':
                        observations.append(observation_from({'step': step, 'action': value['action'], 'result': value['result']}))
            counts[reference] = requests
    return {'passed': True, 'requests': counts, 'proofs_hash': digest(proofs), 'proofs': proofs,
            'model_visible_wrapper_changes': False, 'live_inference': False}
