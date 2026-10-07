"""Deterministic outer loop; Planner proposals never own scheduling or promotion."""
import itertools
import json
import random
import re
import time
import uuid

from ..contracts import canonical, digest
from ..telemetry import utc
from .analysis import Result, best, entry_gate, full_search, metrics, qualification_gate, validate_results
from .cohorts import CohortAccess, manifest, split_search
from .disclosure import project, request, VERSION
from .spec import ScaffoldSpecV1, compile_scaffold, interface_catalog, parse_proposal, references
from .storage import OptimizationStore, LIMITS
from .screening import validate_candidate


def proposal_contract():
    return {'required': ['parents', 'scaffold', 'mutation', 'rationale', 'targeted_categories'],
            'optional': ['predicted_metrics'], 'spec_fields': list(ScaffoldSpecV1.__dataclass_fields__),
            'interfaces': sorted(interface_catalog()['items']), 'controllers': ['C0', 'C1', 'C2', 'C3'],
            'read_allowance': [0, 1, 2], 'recent_observations': [0, 1, 2, 3, 4],
            'output_allocations': [128, 256, 512, 1024], 'feedback': ['generic', 'precise'],
            'retry': ['stop', 'retry'], 'stagnation': [0, 2, 3],
            'context_fields': ['task', 'tools', 'budget', 'control', 'observations', 'source', 'public_cases'],
            'mandatory_context_fields': ['task', 'tools', 'budget', 'control'],
            'maximum_authored_bytes': 4096, 'maximum_phase_calls': 15, 'total_task_decisions': 15}


class SearchManager:
    def __init__(self, store, planner, evaluator):
        if not getattr(planner, 'offline', False) or not getattr(evaluator, 'offline', False):
            raise RuntimeError('M0.9B manager admits offline adapters only')
        self.store, self.planner, self.evaluator = store, planner, evaluator
        self.references = {k: compile_scaffold(s) for k, s in references().items()}
        self.access = CohortAccess(store.search, store.qualification)
        for configuration in self.references.values():
            self.store.scaffold(configuration)

    def results(self, scaffold_id, cohort='search'):
        cohort_hash = manifest(self.store.search if cohort == 'search' else self.store.qualification, cohort)['hash']
        rows = self.store.db.execute('SELECT result_hash FROM m09_jobs WHERE campaign=? AND scaffold_id=? AND cohort_hash=? AND result_hash IS NOT NULL',
                                     (self.store.id, scaffold_id, cohort_hash))
        return tuple(Result(**self.store.get(row[0])) for row in rows)

    def evaluate(self, configuration, tasks, stage):
        name = 'qualification' if stage == 'qualification' else 'search'
        allowed = self.access.request(name, self.store.campaign()['phase'], self.finalist() is not None)
        allowed_by_id = {t.task_id: t.to_dict() for t in allowed}
        if any(allowed_by_id.get(t.task_id) != t.to_dict() for t in tasks):
            raise PermissionError('Task not in exact authorized cohort')
        cohort_hash = manifest(allowed, name)['hash']
        results = []
        for task in tasks:
            row = self.store.db.execute('SELECT j.*,o.state FROM m09_jobs j JOIN m09_operations o ON j.id=o.id WHERE j.campaign=? AND j.scaffold_id=? AND j.cohort_hash=? AND j.task_id=?',
                                       (self.store.id, configuration.scaffold_id, cohort_hash, task.task_id)).fetchone()
            if row and row['state'] == 'completed' and row['result_hash']:
                results.append(Result(**self.store.get(row['result_hash'])))
                continue
            if row and row['state'] != 'reserved':
                raise RuntimeError('Started/incomplete job cannot rerun')
            if row:
                job = row['id']
            else:
                job = digest([self.store.id, configuration.scaffold_id, cohort_hash, task.task_id])
                self.store.reserve('runner', job, {'runner_calls': 15, 'runner_tokens': 16000, 'physical_windows': 1})
                with self.store.db:
                    self.store.db.execute('INSERT INTO m09_jobs VALUES(?,?,?,?,?,?,NULL,NULL)',
                                          (job, self.store.id, configuration.scaffold_id, cohort_hash, task.task_id, stage))
            self.store.start(job)
            try:
                result = self.evaluator.evaluate(configuration, task, cohort_hash, job, self.store)
                validate_results((result,), (task,), cohort_hash, configuration.scaffold_id)
                artifact = self.store.put(result.to_dict(), 'task_result')
                self.store.complete(job, {'runner_calls': result.calls,
                                         'runner_tokens': result.input_tokens + result.output_tokens, 'physical_windows': 1})
                with self.store.db:
                    self.store.db.execute('UPDATE m09_jobs SET result_hash=? WHERE id=?', (artifact, job))
                results.append(result)
            except BaseException:
                state = self.store.db.execute('SELECT state FROM m09_operations WHERE id=?', (job,)).fetchone()[0]
                if state in ('started', 'reserved'):
                    self.store.indeterminate(job, 'runner_operation_indeterminate')
                raise
        return tuple(results)

    def archive(self, configuration, generated):
        all_results = self.results(configuration.scaffold_id)
        screen, remaining = split_search(self.store.search)
        screen_ids = {t.task_id for t in screen}
        full = full_search([r for r in all_results if r.task_id in screen_ids],
                           [r for r in all_results if r.task_id not in screen_ids],
                           self.store.search, configuration.scaffold_id)
        artifact = self.store.put({'results': [r.to_dict() for r in full], 'metrics': metrics(full),
                                   'complexity': configuration.complexity(), 'identity': configuration.scaffold_id}, 'full_search')
        with self.store.db:
            self.store.db.execute('INSERT OR IGNORE INTO m09_archive VALUES(?,?,?,?)',
                                  (self.store.id, configuration.scaffold_id, artifact, int(generated)))
        self.store.decision('archive', {'scaffold': configuration.scaffold_id, 'score': artifact, 'tasks': 32})
        return full

    def archive_entries(self, generated_only=False):
        rows = self.store.db.execute('SELECT * FROM m09_archive WHERE campaign=? ORDER BY scaffold_id', (self.store.id,))
        return [(self.store.configuration(row['scaffold_id']), self.results(row['scaffold_id']))
                for row in rows if not generated_only or row['generated']]

    def observation(self, results):
        search_hash = manifest(self.store.search,'search')['hash']
        if any(r.cohort_hash != search_hash for r in results):
            raise PermissionError('Only search results may enter Planner disclosures')
        events = []
        for result in results:
            for row in self.store.db.execute("SELECT payload_json FROM events WHERE run_id=? AND type='protocol_event' ORDER BY sequence", (result.receipt_id,)):
                events.append({**json.loads(row[0]), 'task_hash': result.task_hash})
        decisions = []
        for row in self.store.db.execute('SELECT validation FROM m09_proposals WHERE campaign=? ORDER BY created_utc', (self.store.id,)):
            decisions.append({'valid':'ACCEPTED','invalid':'REJECTED','duplicate':'DUPLICATE'}[row[0]])
            if row[0] == 'invalid':
                events.append({'category':'MALFORMED'})
        return project(results, events, decisions)

    def _proposal(self, round_number, slot):
        old = self.store.db.execute('SELECT p.* FROM m09_proposals p JOIN m09_planner_requests q ON p.request_id=q.id WHERE p.campaign=? AND q.round=? AND q.slot=?',
                                    (self.store.id, round_number, slot)).fetchone()
        if old:
            return self.store.configuration(old['scaffold_id']) if old['validation'] == 'valid' else None
        entries = self.archive_entries()
        parent, parent_results = best(entries)
        observation = self.observation(parent_results)
        archive = [{'id': c.scaffold_id, 'metrics': metrics(rs), 'tasks': 32} for c, rs in entries]
        remaining = {k: max(0, v - self.store.totals()[k]) for k, v in LIMITS.items()}
        prior = self.store.db.execute('SELECT p.scaffold_id FROM m09_proposals p JOIN m09_planner_requests q ON p.request_id=q.id WHERE p.campaign=? AND q.round=? AND q.slot=1 AND p.validation=\'valid\'',
                                     (self.store.id, round_number)).fetchone()
        if slot == 2 and prior:
            observation = self.observation(self.results(prior[0]))
        payload = request(observation, parent, archive, remaining, proposal_contract())
        payload = self.planner.prepare_request(payload)
        observation = json.loads(payload['messages'][1]['content'])['observation']
        qid = digest([self.store.id, round_number, slot])
        existing = self.store.db.execute('SELECT * FROM m09_planner_requests WHERE id=?', (qid,)).fetchone()
        if existing:
            operation = self.store.db.execute('SELECT state FROM m09_operations WHERE id=?', (qid,)).fetchone()[0]
            if operation != 'reserved':
                raise RuntimeError('Unresolved Planner request cannot resend')
            payload = self.store.get(existing['request_hash'])
            observation = json.loads(payload['messages'][1]['content'])['observation']
        else:
            disclosed = self.store.put(observation, 'planner_observation')
            disclosure = self.store.put({'observation': disclosed, 'policy': VERSION, 'request': digest(payload)}, 'disclosure')
            with self.store.db:
                self.store.db.execute('INSERT OR IGNORE INTO m09_disclosures VALUES(?,?,?,?,?)',
                                      (disclosure, self.store.id, VERSION, disclosed, utc()))
            request_hash = self.store.put(payload, 'planner_request')
            cfg = self.store.put({**self.store.config['planner'], 'offline': bool(self.planner.offline)}, 'planner_configuration')
            self.store.reserve('planner', qid, {'planner_requests': 1, 'planner_tokens': len(canonical(payload)) + 4096 + 1024})
            with self.store.db:
                self.store.db.execute('INSERT INTO m09_planner_requests VALUES(?,?,?,?,?,?,?)',
                                      (qid, self.store.id, round_number, slot, disclosure, request_hash, cfg))
        if not self.planner.offline:
            raise RuntimeError('Live Planner requires separately authorized M0.9C admission')
        disclosed_body = json.loads(payload['messages'][1]['content'])
        archive, remaining = disclosed_body['archive'], disclosed_body['remaining']
        self.store.start(qid)
        try:
            reply = self.planner.propose({'observation': observation, 'request': payload, 'parent': parent}, archive, remaining).validate()
            response = self.store.put(reply.response, 'planner_response')
            identity = self.store.put({**reply.identity, 'seed_supported': reply.seed_supported}, 'planner_identity')
            usage = self.store.put({'input_tokens': reply.input_tokens, 'output_tokens': reply.output_tokens,
                                   'reasoning_tokens': reply.reasoning_tokens, 'reasoning_in_output': reply.reasoning_in_output,
                                   'total_tokens': reply.total_tokens}, 'planner_usage')
            with self.store.db:
                self.store.db.execute('INSERT INTO m09_planner_responses VALUES(?,?,?,?,?,?)',
                                      (qid, response, identity, usage, utc(), reply.latency))
            self.store.complete(qid, {'planner_requests': 1, 'planner_tokens': reply.total_tokens})
        except BaseException:
            state = self.store.db.execute('SELECT state FROM m09_operations WHERE id=?', (qid,)).fetchone()[0]
            if state in ('started', 'reserved'):
                self.store.indeterminate(qid, 'planner_operation_indeterminate')
            raise
        allowed_parents = {c.scaffold_id for c, _ in entries}
        configuration, envelope, status, reason = None, None, 'invalid', 'MALFORMED'
        try:
            envelope = parse_proposal(reply.text, allowed_parents)
            configuration = compile_scaffold(envelope.scaffold)
            validate_candidate(configuration, self.store.config['runner'])
            seen = (configuration.scaffold_id in allowed_parents or self.store.db.execute(
                'SELECT 1 FROM m09_proposals WHERE campaign=? AND scaffold_id=?', (self.store.id, configuration.scaffold_id)).fetchone())
            self.store.scaffold(configuration)
            status, reason = ('duplicate', 'DUPLICATE') if seen else ('valid', 'ACCEPTED')
        except (ValueError, TypeError, KeyError, RecursionError) as exc:
            configuration, envelope = None, None
            if re.fullmatch(r'(?:SPEC|PROPOSAL)_[A-Z_]+', str(exc)):
                reason = str(exc)
        pid = digest([qid, response])
        artifact = self.store.put(envelope.to_dict() if envelope else {'raw_response_hash': response}, 'proposal_envelope')
        resources = self.store.put(self.store.config['window'], 'proposal_resources')
        with self.store.db:
            self.store.db.execute('INSERT INTO m09_proposals VALUES(?,?,?,?,?,?,?,?,?)',
                                  (pid, self.store.id, qid, configuration.scaffold_id if configuration else None,
                                   artifact, status, reason, resources, utc()))
            if envelope:
                for parent_id in envelope.parents:
                    self.store.db.execute('INSERT INTO m09_parents VALUES(?,?)', (pid, parent_id))
        validation = self.store.put({'proposal': pid, 'state': status, 'reason': reason}, 'proposal_validation')
        with self.store.db:
            self.store.db.execute('INSERT INTO m09_validations VALUES(?,?,?,?,?)', (validation, pid, status, reason, utc()))
        return configuration if status == 'valid' else None

    def finalist(self):
        row = self.store.db.execute('SELECT * FROM m09_finalists WHERE campaign=?', (self.store.id,)).fetchone()
        return dict(row) if row else None

    def run(self):
        phase = self.store.campaign()['phase']
        if phase in ('finished', 'stopped'):
            return self.report()
        if self.store.state().get('paused'):
            raise RuntimeError('Resume planned idle pause explicitly before execution')
        if phase == 'search' and self.finalist() is not None:
            # A durable freeze may precede the phase update when the process stops.
            self.store.update('qualification')
        if phase == 'references':
            for reference in self.references.values():
                self.evaluate(reference, self.store.search, 'reference')
                self.archive(reference, False)
            self.store.update('search')
        if self.store.campaign()['phase'] == 'search':
            for round_number in range(self.store.state()['round'], 5):
                candidates = []
                for slot in (1, 2):
                    configuration = self._proposal(round_number, slot)
                    if configuration:
                        screen, _ = split_search(self.store.search)
                        candidates.append((configuration, self.evaluate(configuration, screen, 'screen')))
                    self.store.update(round=round_number, slot=slot+1)
                winner = best(candidates)
                if winner:
                    configuration, _ = winner
                    _, remaining = split_search(self.store.search)
                    self.evaluate(configuration, remaining, 'remaining')
                    self.archive(configuration, True)
                self.store.decision('round', {'round': round_number, 'winner': winner[0].scaffold_id if winner else None})
                self.store.update(round=round_number+1, slot=1)
            selected = best(self.archive_entries(True))
            if selected is None:
                self.store.update('finished', stop_reason='no_generated_full_scaffold')
                return self.report()
            configuration, rs = selected
            gate = entry_gate(rs, self.results(self.references['B0'].scaffold_id), self.results(self.references['B1'].scaffold_id))
            receipt = self.store.decision('entry_gate', {'scaffold': configuration.scaffold_id, **gate})
            if not gate['passed']:
                self.store.update('finished', stop_reason='qualification_entry_failed')
                return self.report()
            freeze = self.store.put({'scaffold': configuration.scaffold_id, 'entry_receipt': receipt,
                                     'closed_round': 5, 'proposal_budget_closed': True}, 'finalist_freeze')
            with self.store.db:
                self.store.db.execute('INSERT INTO m09_finalists VALUES(?,?,?,1)', (self.store.id, configuration.scaffold_id, freeze))
            self.store.update('qualification')
        if self.store.campaign()['phase'] == 'qualification':
            finalist = self.finalist()
            selected = self.store.configuration(finalist['scaffold_id'])
            configurations = {'B0': self.references['B0'], 'B1': self.references['B1'], 'selected': selected}
            schedules = list(itertools.permutations(configurations)) * 8
            random.Random(9003).shuffle(schedules)
            tasks = self.access.request('qualification', 'qualification', True)
            self.store.decision('qualification_schedule', {'seed': 9003, 'rows': [
                {'task_id':task.task_id, 'arms':list(order)}
                for task,order in zip(sorted(tasks,key=lambda t:t.task_id),schedules)]})
            for task, order in zip(sorted(tasks, key=lambda t: t.task_id), schedules):
                for arm in order:
                    self.evaluate(configurations[arm], (task,), 'qualification')
            gate = qualification_gate(self.results(selected.scaffold_id, 'qualification'),
                                      self.results(self.references['B0'].scaffold_id, 'qualification'),
                                      self.results(self.references['B1'].scaffold_id, 'qualification'))
            if self.store.totals()['active_wall_seconds'] >= LIMITS['active_wall_seconds']:
                self.store.stop('active_wall_ceiling')
                return self.report()
            self.store.decision('qualification_gate', gate)
            self.store.update('finished', stop_reason='qualified' if gate['passed'] else 'qualification_failed')
        return self.report()

    def report(self):
        accounting = self.store.cost_report()
        return {'campaign': self.store.id, 'protocol': '0.6', 'phase': self.store.campaign()['phase'],
                'state': self.store.state(), 'finalist': self.finalist(),
                'physical_cost': {**accounting['completed_actual'],'active_wall_seconds':accounting['active_wall_seconds']},
                'cost_accounting': accounting,
                'archive': [{'scaffold': c.scaffold_id, 'metrics': metrics(rs)} for c, rs in self.archive_entries()]}
