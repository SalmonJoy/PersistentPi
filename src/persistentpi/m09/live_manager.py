"""Admitted, terminal search-only scheduler. Historical kernel remains unchanged."""
import json
import re
import uuid

from ..contracts import canonical, digest
from ..telemetry import utc
from .analysis import Result, best, entry_gate, metrics
from .cohorts import split_search
from .disclosure import request, VERSION
from .manager import SearchManager, proposal_contract
from .spec import compile_scaffold, references, parse_proposal
from .screening import validate_candidate
from .storage import LIMITS
from .live_binding import AdmissionBinding, AdmittedPlanner, render_request
from .live_store import SearchStore, SearchAccess

TERMINALS = ('SEARCH_STOPPED', 'SEARCH_COMPLETE_NO_FINALIST', 'SEARCH_COMPLETE_FINALIST_FROZEN')


class SearchOnlyManager(SearchManager):
    def __init__(self, store, planner, evaluator, binding, mode='OFFLINE'):
        if type(store) is not SearchStore or type(binding) is not AdmissionBinding:
            raise ValueError('Search-only store and anchored admission required')
        binding.check(store.config)
        if mode not in ('OFFLINE', 'SEARCH_ONLY'):
            raise ValueError('Unknown launch mode')
        if mode == 'OFFLINE':
            if not getattr(planner, 'offline', False) or not getattr(evaluator, 'offline', False):
                raise ValueError('Live disabled by default')
        else:
            if type(planner) is not AdmittedPlanner or planner.binding.hash != binding.hash:
                raise ValueError('Only the exact admitted Planner is allowed')
            if not store.config['operational_launch']['validation_only']:
                from .live_runtime import LiveCandidateExecutor
                if type(evaluator) is not LiveCandidateExecutor or evaluator.binding.hash != binding.hash:
                    raise ValueError('Only the fixed laptop Runner is allowed live')
            elif not getattr(evaluator, 'offline', False):
                raise ValueError('Validation cannot enable Runner inference')
        self.store, self.planner, self.evaluator, self.binding, self.mode = store, planner, evaluator, binding, mode
        self.references = {k: compile_scaffold(s) for k, s in references().items()}
        self.access = SearchAccess(store.search)
        for reference in self.references.values():
            store.scaffold(reference)

    def _check(self, round_number, slot):
        self.binding.check(self.store.config)
        if (self.store.campaign()['phase'] != 'search' or round_number not in range(1, 5) or slot not in (1, 2)):
            raise RuntimeError('Proposal access closed or slot outside frozen schedule')
        if self.mode == 'SEARCH_ONLY':
            if type(self.planner) is not AdmittedPlanner or self.planner.binding.hash != self.binding.hash:
                raise ValueError('Admitted adapter mismatch')

    def render_request(self, observation, parent, archive, remaining, contract):
        if self.mode == 'OFFLINE':
            return request(observation, parent, archive, remaining, contract)
        self.planner.pre_request()
        return render_request(self.binding, self.store.config, observation, parent, archive, remaining, contract)

    def results(self, scaffold_id, cohort='search'):
        if cohort != 'search':
            raise PermissionError('No non-search result capability')
        return super().results(scaffold_id, cohort)

    def evaluate(self, configuration, tasks, stage):
        if stage not in ('reference', 'screen', 'remaining'):
            raise PermissionError('No non-search evaluator capability')
        return super().evaluate(configuration, tasks, stage)

    def _proposal(self, round_number, slot):
        self._check(round_number, slot)
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
        payload = self.render_request(observation, parent, archive, remaining, proposal_contract())
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
        self._check(round_number, slot)
        disclosed_body = json.loads(payload['messages'][1]['content'])
        archive, remaining = disclosed_body['archive'], disclosed_body['remaining']
        self.store.start(qid)
        try:
            reply = self.planner.propose({'observation': observation, 'request': payload, 'parent': parent}, archive, remaining).validate()
            response = self.store.put(reply.response, 'planner_response')
            if getattr(self.planner,'last_provenance',None) is not None:
                self.store.put(self.planner.last_provenance, 'planner_transport_provenance')
            self.store.put({'thinking': reply.response.get('message', {}).get('thinking')}, 'planner_thinking')
            identity = self.store.put({**reply.identity, 'seed_supported': reply.seed_supported}, 'planner_identity')
            usage = self.store.put({'input_tokens': reply.input_tokens, 'output_tokens': reply.output_tokens,
                                   'reasoning_tokens': None, 'reasoning_in_output': True,
                                   'prompt_eval_cached_count': getattr(self.planner, 'last_usage', {}).get('prompt_eval_cached_count') if getattr(self.planner, 'last_usage', None) else None,
                                   'provider_accounted_tokens': reply.input_tokens + reply.output_tokens,
                                   'total_tokens': reply.total_tokens}, 'planner_usage')
            with self.store.db:
                self.store.db.execute('INSERT INTO m09_planner_responses VALUES(?,?,?,?,?,?)',
                                      (qid, response, identity, usage, utc(), reply.latency))
            self.store.complete(qid, {'planner_requests': 1, 'planner_tokens': reply.total_tokens})
        except BaseException:
            if getattr(self.planner, 'last_response', None) is not None:
                self.store.put(self.planner.last_response, 'incomplete_planner_response')
            if getattr(self.planner, 'last_usage', None) is not None:
                self.store.put(self.planner.last_usage, 'incomplete_authoritative_usage')
            if getattr(self.planner,'last_provenance',None) is not None:
                self.store.put(self.planner.last_provenance, 'incomplete_transport_provenance')
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

    def _exit(self):
        phase = self.store.campaign()['phase']
        if phase not in ('finished', 'stopped'):
            raise RuntimeError('Search exit must be terminal')
        if not self.store.state().get('search_terminal'):
            terminal = 'SEARCH_STOPPED' if phase == 'stopped' else (
                'SEARCH_COMPLETE_FINALIST_FROZEN' if self.finalist() else 'SEARCH_COMPLETE_NO_FINALIST')
            self.store.update(search_terminal=terminal, proposal_access_closed=True)
        barrier = self.store.assert_barrier()
        return {**self.report(), 'search_terminal': self.store.state()['search_terminal'], 'barrier': barrier}

    def run(self):
        if self.store.campaign()['phase'] in ('finished', 'stopped'):
            return self._exit()
        if self.store.state().get('paused'):
            raise RuntimeError('Explicitly resume an idle pause first')
        try:
            if self.store.campaign()['phase'] == 'references':
                for reference in self.references.values():
                    self.evaluate(reference, self.store.search, 'reference')
                    self.archive(reference, False)
                self.store.update('search')
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
                return self._exit()
            configuration, results = selected
            self.store.decision('generated_selection', {'scaffold': configuration.scaffold_id})
            gate = entry_gate(results, self.results(self.references['B0'].scaffold_id),
                              self.results(self.references['B1'].scaffold_id))
            receipt = self.store.decision('entry_gate', {'scaffold': configuration.scaffold_id, **gate})
            if gate['passed']:
                lineage = [dict(r) for r in self.store.db.execute('SELECT * FROM m09_proposals WHERE campaign=? AND scaffold_id=?',
                                                               (self.store.id, configuration.scaffold_id))]
                freeze = self.store.put({'scaffold': configuration.scaffold_id, 'entry_receipt': receipt,
                    'closed_round': 5, 'proposal_budget_closed': True, 'spec': configuration.spec.to_dict(),
                    'compiler': configuration.compiler, 'catalog': configuration.catalog_hash,
                    'binding_hash': self.binding.hash, 'lineage': lineage, 'results': [r.to_dict() for r in results],
                    'metrics': metrics(results), 'complexity': configuration.complexity(),
                    'cost': self.store.cost_report()}, 'finalist_freeze')
                with self.store.db:
                    self.store.db.execute('INSERT INTO m09_finalists VALUES(?,?,?,1)',
                                          (self.store.id, configuration.scaffold_id, freeze))
            self.store.update('finished', stop_reason='finalist_frozen' if gate['passed'] else 'qualification_entry_failed')
        except BaseException:
            if self.store.campaign()['phase'] not in ('finished', 'stopped'):
                self.store.stop('search_integrity_stop')
            self._exit()
            raise
        return self._exit()
