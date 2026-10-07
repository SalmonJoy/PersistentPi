"""Public subset: historical parity/private freeze tests are not distributed."""
from collections import Counter
from copy import deepcopy
import io
import ast
import json
from pathlib import Path
import hashlib
import random
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts')]

from persistentpi.artifacts import atomic_write
from persistentpi.contracts import canonical, digest
from persistentpi.m010.accounting import charge, forecast, money, usage
from persistentpi.m010.admission import prerequisites, probe_result
from persistentpi.m010.analysis import interface_ready, improvement
from persistentpi.m010.boundary import access_audit, isolated_output
from persistentpi.m010.classifier import classify
from persistentpi.m010.completion import complete
from persistentpi.m010.config import FAMILIES
from persistentpi.m010.export import export, replay
from persistentpi.m010.f0 import historical_parity, parse_f0
from persistentpi.m010.f2 import tool_schema, arguments
from persistentpi.m010.freeze import prepare, seal, regression_gate
from persistentpi.m010.frozen import parent_registry, verify_anchors, parent_spec
from persistentpi.m010.ledger import Ledger
from persistentpi.m010.mutation import FIELDS, ENUMS, mutation_schema, parse_f1, compile_mutation
from persistentpi.m010.render import render, probe_arguments, probe_request, request_identity
from persistentpi.m010.scenarios import generate, schedule
from persistentpi.m010.scheduler import Scheduler
from persistentpi.m010.statistics import paired_bootstrap, exact_permutation, holm
from persistentpi.m010.stubs import PRICING, RecordingTransport, campaign_handler, fixture_response
from persistentpi.m010.transport import NativeTransport, NoRedirect

REGISTRY = parent_registry()
SCENARIOS = generate(REGISTRY)
ORDER = schedule(SCENARIOS)
S = SCENARIOS[0]
P = S['parent_id']


def proposal(field='recent_observations', value=1):
    return {'parent_id': P, 'mutations': [{'field': field, 'value': value}], 'target_failures': ['OTHER']}


def compile_value(value):
    return compile_mutation(parse_f1(canonical(value).decode()), REGISTRY)


class ContractTests(unittest.TestCase):
    def test_all_fields_and_allowed_values(self):
        domains = {**ENUMS, 'system_text': ['', 'General bounded scaffold instructions.'],
            'tool_descriptions': [{}, *[{k: 'General tool description.'} for k in ('read_file', 'edit_file', 'replace_file', 'finish')]],
            'context_fields': [['task', 'tools', 'budget', 'control'],
                               ['public_cases', 'source', 'observations', 'control', 'budget', 'tools', 'task']],
            'source_preload': [False, True], 'inspect_calls': list(range(1, 16)), 'act_calls': list(range(1, 16))}
        self.assertEqual(set(domains), set(FIELDS))
        for field, values in domains.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    p = proposal(field, value)
                    if field == 'read_allowance' and value == 0:
                        p['mutations'].append({'field': 'source_preload', 'value': True})
                    compiled = compile_value(p)
                    self.assertEqual(compiled.spec.to_dict()[field], value)

    def test_every_numeric_boundary_and_bool_distinction(self):
        for field in ('inspect_calls', 'act_calls'):
            for value in (0, 16, True, False, '1', 1.0):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    compile_value(proposal(field, value))
        for field in ('read_allowance', 'recent_observations', 'stagnation', 'inspect_output', 'act_output'):
            for value in (-1, True, '2', 2.0, 9999):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    compile_value(proposal(field, value))

    def test_unknown_keys_alias_version_executable_rejected(self):
        for field in ('version', 'output_tokens', 'command', 'model', 'foo'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                compile_value(proposal(field, 1))
        for name in ('code', 'extra'):
            value = proposal(); value[name] = 'untrusted'
            with self.assertRaises(ValueError): compile_value(value)
        value = proposal(); value['mutations'][0]['extra'] = True
        with self.assertRaises(ValueError): compile_value(value)

    def test_duplicate_keys_and_duplicate_conflicting_fields(self):
        raw = canonical(proposal()).decode().replace('"parent_id":', '"parent_id":"' + P + '","parent_id":')
        with self.assertRaises(ValueError): parse_f1(raw)
        for value in (1, 2):
            p = proposal(); p['mutations'].append({'field': 'recent_observations', 'value': value})
            with self.assertRaises(ValueError): compile_value(p)

    def test_categories_exact_types_unique_and_limits(self):
        for cats in ([], ['no_op'], ['OTHER', 'OTHER'], [True], 'OTHER', [None]):
            p = proposal(); p['target_failures'] = cats
            with self.subTest(cats=cats), self.assertRaises(ValueError): compile_value(p)

    def test_parent_required_and_no_default_invention(self):
        for parent in ('0' * 64, P.upper(), '../parent', None):
            p = proposal(); p['parent_id'] = parent
            with self.assertRaises(ValueError): compile_value(p)
        result = compile_value(proposal())
        expected = deepcopy(REGISTRY[P]['spec']); expected['recent_observations'] = 1
        self.assertEqual(result.spec.to_dict(), expected)

    def test_parent_must_be_normalized_and_provenance_intact(self):
        registry = deepcopy(REGISTRY)
        del registry[P]['spec']['recent_observations']
        registry[P]['spec_hash'] = digest(registry[P]['spec'])
        with self.assertRaises(ValueError): parent_spec(registry, P)
        for key in ('compiler', 'renderer', 'protocol', 'catalog_hash'):
            registry = deepcopy(REGISTRY); registry[P][key] = 'changed'
            with self.assertRaises(ValueError): parent_spec(registry, P)

    def test_dependency_no_silent_repair(self):
        with self.assertRaises(ValueError): compile_value(proposal('read_allowance', 0))
        for context in (['task', 'tools', 'budget'], ['task', 'tools', 'budget', 'control', 'control'], ['task', 'tools', 'budget', 'control', 'hidden']):
            with self.assertRaises(ValueError): compile_value(proposal('context_fields', context))

    def test_text_payload_and_combined_limit(self):
        for text in ('non-ascii:\u00e9', '\x00', '```', 'def solve(', 'reference_solution', 'task_lookup', 'x' * 4097):
            with self.subTest(text=text[:30]), self.assertRaises(ValueError): compile_value(proposal('system_text', text))
        value = proposal('system_text', 'x' * 4096)
        self.assertEqual(len(compile_value(value).spec.system_text), 4096)
        value['mutations'].append({'field': 'tool_descriptions', 'value': {'read_file': 'x'}})
        with self.assertRaises(ValueError): compile_value(value)

    def test_operation_order_hash_and_parent_immutability(self):
        p = proposal(); p['mutations'] += [{'field': 'source_preload', 'value': True}, {'field': 'read_allowance', 'value': 0}]
        before = canonical(REGISTRY)
        a = compile_value(p); p['mutations'].reverse(); b = compile_value(p)
        self.assertEqual(a.scaffold_id, b.scaffold_id)
        self.assertEqual(before, canonical(REGISTRY))

    def test_rationale_and_submission_limits(self):
        p = proposal(); p['rationale'] = 'x' * 257
        with self.assertRaises(ValueError): compile_value(p)
        with self.assertRaises(ValueError): parse_f1(' ' * 65537)
        with self.assertRaises(ValueError): parse_f1('```' + canonical(proposal()).decode() + '```')


    def test_f0_defaults_not_parent_inheritance_and_category_normalization(self):
        value = {'parents': [P], 'scaffold': {'system_text': 'General.'}, 'mutation': '', 'rationale': '',
                 'targeted_categories': ['OTHER', 'OTHER']}
        envelope = parse_f0(canonical(value).decode(), REGISTRY)
        self.assertEqual(envelope.scaffold.recent_observations, 4)
        self.assertEqual(envelope.targeted_categories, ('OTHER',))
        value['scaffold'] = {}
        with self.assertRaises(ValueError): parse_f0(canonical(value).decode(), REGISTRY)

    def test_f2_vocabulary_equivalence_and_oneof(self):
        self.assertEqual(tool_schema()['function']['parameters'], mutation_schema())
        branches = tool_schema()['function']['parameters']['properties']['mutations']['items']['oneOf']
        self.assertEqual({b['properties']['field']['enum'][0] for b in branches}, set(FIELDS))
        response = fixture_response(S, 'F2')
        json_result = classify(fixture_response(S, 'F1'), 'F1', {P: REGISTRY[P]})
        tool_result = classify(response, 'F2', {P: REGISTRY[P]})
        self.assertEqual(json_result['normalized_spec'], tool_result['normalized_spec'])

    def test_f2_rejected_native_transport_forms(self):
        good = fixture_response(S, 'F2')
        variants = []
        for calls in ([], good['message']['tool_calls'] * 2, None):
            r = deepcopy(good); r['message']['tool_calls'] = calls; variants.append(r)
        r = deepcopy(good); r['message']['tool_calls'][0]['function']['name'] = 'other'; variants.append(r)
        r = deepcopy(good); r['message']['tool_calls'][0]['function']['arguments'] = '{}'; variants.append(r)
        variants += [fixture_response(S, 'F0'), {**good, 'message': {'thinking': 'only reasoning'}}]
        for r in variants:
            with self.assertRaises(ValueError): arguments(r)
            self.assertFalse(classify(r, 'F2', {P: REGISTRY[P]})['acquired_valid_proposal'])

    def test_documented_completion_not_literal_stop(self):
        r = fixture_response(S, 'F2'); r['done_reason'] = 'tool_completion'
        with self.assertRaises(ValueError): complete(r)
        evidence = {'tool_completion': {'meaning': 'complete', 'source': 'synthetic documented semantics'}}
        self.assertEqual(complete(r, evidence)['done_reason'], 'tool_completion')
        r['message']['tool_calls'][0]['function']['arguments'] = probe_arguments()
        self.assertTrue(probe_result(r, evidence)['passed'])

    def test_truncation_fails_even_parseable(self):
        for arm in ('F0', 'F1', 'F2'):
            r = fixture_response(S, arm); r['done_reason'] = 'length'
            result = classify(r, arm, {P: REGISTRY[P]})
            self.assertFalse(result['acquired_valid_proposal']); self.assertTrue(result['truncated'])
            self.assertEqual(result['first_failure']['stage'], 2)

    def test_probe_spec_is_frozen_and_unexecuted(self):
        payload = probe_request()
        self.assertEqual(json.loads(payload['messages'][1]['content']), probe_arguments())
        self.assertEqual(payload['options']['num_predict'], 4096)
        self.assertEqual(payload['think'], 'high')
        self.assertNotIn('format', payload); self.assertNotIn('tool_choice', payload)

    def test_probe_exact_argument_types_and_identity_usage(self):
        good = fixture_response(S, 'F2')
        good['message']['tool_calls'][0]['function']['arguments'] = probe_arguments()
        self.assertTrue(probe_result(good)['passed'])
        bad = deepcopy(good); bad['message']['tool_calls'][0]['function']['arguments']['mutations'][0]['value'] = True
        self.assertFalse(probe_result(bad)['passed'])
        for key in ('model', 'done', 'prompt_eval_count', 'eval_count', 'prompt_eval_cached_count'):
            bad = deepcopy(good); del bad[key]
            self.assertFalse(probe_result(bad)['passed'])


class ScenarioTests(unittest.TestCase):
    def test_exact_deterministic_24_by_8(self):
        self.assertEqual(canonical(SCENARIOS), canonical(generate(REGISTRY)))
        self.assertEqual(Counter(s['family'] for s in SCENARIOS), Counter({f: 3 for f in FAMILIES}))
        self.assertEqual(Counter(s['parent_id'] for s in SCENARIOS), Counter({k: 12 for k in REGISTRY}))

    def test_shape_formulas_and_no_source(self):
        for s in SCENARIOS:
            body = s['payload']; obs = body['observation']
            self.assertEqual(obs['aggregate']['tasks'], 32)
            self.assertEqual(len(obs['families']), 8)
            self.assertEqual(len(obs['excerpts']), 2)
            for event in obs['excerpts']:
                self.assertEqual(event['content'], '<source omitted>')
                self.assertEqual(event['old_equals_new'], event['old_hash'] == event['new_hash'])
            self.assertNotIn('reference_solution', canonical(body).decode())

    def test_shuffle_exactly_scenario_ids(self):
        expected = sorted(s['id'] for s in SCENARIOS); random.Random(42).shuffle(expected)
        self.assertEqual(ORDER['scenario_order'], expected)
        self.assertEqual(ORDER['hash'], digest({k: v for k, v in ORDER.items() if k != 'hash'}))

    def test_render_bytes_and_semantic_pairing(self):
        for s in SCENARIOS:
            user_bodies = []
            for arm in ('F0', 'F1', 'F2'):
                payload = render(s, arm)
                self.assertLessEqual(len(canonical(payload)), 16384)
                self.assertEqual(payload['options'], {'temperature': 0, 'num_predict': 4096})
                self.assertFalse(set(payload) & {'format', 'response_format', 'tool_choice'})
                body = json.loads(payload['messages'][1]['content']); del body['contract']; user_bodies.append(body)
            self.assertEqual(user_bodies[0], user_bodies[1]); self.assertEqual(user_bodies[1], user_bodies[2])

    def test_generator_access_capability_audit(self):
        with access_audit(reads=[ROOT / 'src']) as audit:
            generated = generate()
        self.assertEqual(len(generated), 24)
        self.assertTrue(all(e['allowed'] and not e['write'] for e in audit['events']))
        self.assertFalse(any('research-records' in e['path'] for e in audit['events']))

    def test_protected_access_denied_before_read(self):
        for name in ('search32-public.json', 'qualification48-public.json', 'final96.json', 'hidden.json'):
            with access_audit(reads=[ROOT / 'src']), self.assertRaises(PermissionError):
                (ROOT / 'docs/research-records/m09b/prepared' / name).read_bytes()
        with self.assertRaises(PermissionError): isolated_output(ROOT / 'docs/research-records/m09cf/extra')

    def test_no_runner_or_benchmark_execution_capability(self):
        forbidden = {'eval', 'exec', 'compile', 'load_suite', 'exposed_search', 'qualification', 'HiddenEvaluator', 'Runner'}
        for path in (ROOT / 'src/persistentpi/m010').glob('*.py'):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, forbidden, str(path))
                if isinstance(node, ast.ImportFrom):
                    self.assertFalse((node.module or '').startswith(('m08.benchmark', 'runner', 'evaluation')))


class LedgerCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.folder = Path(self.temp.name)
        self.ledger = Ledger(self.folder / 'ledger')
    def tearDown(self):
        self.ledger.close(); self.temp.cleanup()
    def create(self, arms=('F0', 'F1'), pricing=None):
        self.ledger.create('test', 'a' * 64, arms, ORDER, REGISTRY, pricing or PRICING)
    def reserve(self):
        sid = ORDER['scenario_order'][0]; s = next(s for s in SCENARIOS if s['id'] == sid)
        self.ledger.reserve_block('test', sid, 0, {a: render(s, a) for a in ('F0', 'F1')})
        return s


class LedgerTests(LedgerCase):
    def test_atomic_reservation_and_namespace(self):
        self.create(); self.reserve()
        self.assertEqual(len(self.ledger.requests('test')), 2)
        self.assertEqual(self.ledger.exposure('test')['tokens'], 2 * 135168)
        names = [r[0] for r in self.ledger.db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        self.assertTrue(all(n.startswith(('m010_', 'sqlite_')) for n in names))
        self.assertTrue(self.ledger.integrity())

    def test_no_resend_and_prior_unsettled(self):
        self.create(); s = self.reserve(); q = self.ledger.requests('test')[0]
        self.ledger.start(q['id'])
        with self.assertRaises(ValueError): self.ledger.start(q['id'])
        sid = ORDER['scenario_order'][1]; s = next(x for x in SCENARIOS if x['id'] == sid)
        with self.assertRaises(ValueError):
            self.ledger.reserve_block('test', sid, 1, {a: render(s, a) for a in ('F0', 'F1')})

    def test_atomic_ceiling_rolls_back(self):
        pricing = {**PRICING, 'input_per_million': '100'}
        self.create(pricing=pricing)
        with self.assertRaises(ValueError): self.reserve()
        self.assertEqual(self.ledger.requests('test'), [])

    def test_missing_accounting_saved_then_stop(self):
        self.create(); s = self.reserve(); q = self.ledger.requests('test')[0]
        self.ledger.start(q['id']); r = fixture_response(s, q['arm']); del r['eval_count']
        with self.assertRaises(ValueError): self.ledger.capture(q['id'], r, 1)
        self.assertEqual(self.ledger.study('test')['status'], 'STOPPED')
        self.assertIsNotNone(self.ledger.requests('test')[0]['response_hash'])

    def test_known_provider_overrun_accounted_not_clipped(self):
        self.create(); s = self.reserve(); q = self.ledger.requests('test')[0]
        self.ledger.start(q['id']); r = fixture_response(s, q['arm']); r['eval_count'] = 5000
        with self.assertRaises(ValueError): self.ledger.capture(q['id'], r, 1)
        row = self.ledger.requests('test')[0]
        account = self.ledger.get(row['account_hash'])
        self.assertEqual(account['provider_accounted_tokens'], 6000)
        self.assertEqual(account['ceiling_violations'], ['eval_count'])
        self.assertEqual(self.ledger.study('test')['status'], 'STOPPED')

    def test_redaction_before_persistence(self):
        self.ledger.secrets = ('test-secret-value',)
        with self.ledger.transaction(), self.assertRaises(ValueError):
            self.ledger.put({'x': 'test-secret-value'}, 'bad')

    def test_probe_reservation_idempotent_no_send(self):
        row = self.ledger.reserve_probe(probe_request(), PRICING, {'synthetic': True})
        self.assertEqual(row['state'], 'RESERVED')
        again = self.ledger.reserve_probe(probe_request(), PRICING, {'synthetic': True})
        self.assertEqual(row, again)
        self.ledger.start_probe()
        with self.assertRaises(ValueError): self.ledger.start_probe()

    def test_scheduler_concurrency_admission(self):
        self.create(); t = RecordingTransport(SCENARIOS, concurrency=1)
        with self.assertRaises(ValueError): Scheduler(self.ledger, 'test', SCENARIOS).run(t)
        self.assertEqual(t.events, [])

    def test_saved_receipt_resume_without_send(self):
        self.create(); s = self.reserve(); rows = self.ledger.requests('test')
        for q in rows:
            self.ledger.start(q['id']); self.ledger.capture(q['id'], fixture_response(s, q['arm']), .01)
        t = RecordingTransport(SCENARIOS)
        result = Scheduler(self.ledger, 'test', SCENARIOS).run(t)
        self.assertEqual(result['status'], 'COMPLETE')
        self.assertEqual(len([e for e in t.events if e['event'] == 'send']), 46)

    def test_started_unresolved_not_restarted(self):
        self.create(); self.reserve(); self.ledger.start(self.ledger.requests('test')[0]['id'])
        t = RecordingTransport(SCENARIOS)
        result = Scheduler(self.ledger, 'test', SCENARIOS).run(t)
        self.assertEqual(result['status'], 'STOPPED'); self.assertEqual(t.events, [])

    def test_worker_inherits_protected_read_boundary(self):
        self.create()
        def forbidden(s, arm):
            (ROOT / 'docs/research-records/m09b/prepared/qualification48-public.json').read_bytes()
            raise AssertionError('unreachable')
        t = RecordingTransport(SCENARIOS, handler=forbidden)
        result = Scheduler(self.ledger, 'test', SCENARIOS).run(t)
        self.assertEqual(result['status'], 'STOPPED')
        self.assertEqual(len([e for e in t.events if e['event'] == 'send']), 2)
        self.assertFalse(any(q['response_hash'] for q in self.ledger.requests('test')))

    def test_dispatch_completion_order_invariant(self):
        self.create(('F0', 'F1', 'F2'))
        t = RecordingTransport(SCENARIOS, order=('F2', 'F1', 'F0'))
        result = Scheduler(self.ledger, 'test', SCENARIOS).run(t)
        self.assertEqual(result['status'], 'COMPLETE'); self.assertEqual(t.peak, 3)
        for sid in ORDER['scenario_order']:
            sends = [i for i, e in enumerate(t.events) if e['scenario'] == sid and e['event'] == 'send']
            receives = [i for i, e in enumerate(t.events) if e['scenario'] == sid and e['event'] == 'receipt']
            self.assertLess(max(sends), min(receives))
        for first, second in zip(ORDER['scenario_order'], ORDER['scenario_order'][1:]):
            self.assertLess(max(i for i, e in enumerate(t.events) if e['scenario'] == first),
                            min(i for i, e in enumerate(t.events) if e['scenario'] == second))


class AnalysisTests(unittest.TestCase):
    def test_exact_256_assignments_ties_no_correction(self):
        differences = {f: [0, 0, 0] for f in FAMILIES}
        result = exact_permutation(differences)
        self.assertEqual(result['p_value'], 1); self.assertEqual(result['tail_count'], 256)
        self.assertEqual({r['mask'] for r in result['assignments']}, set(range(256)))
        result = exact_permutation({f: [1, 1, 1] for f in FAMILIES})
        self.assertEqual(result['T_obs'], 1); self.assertEqual(result['p_value'], 2 / 256)

    def test_bootstrap_degenerate_and_paired(self):
        for value in (-1, 0, 1):
            b = paired_bootstrap({f: [value] * 3 for f in FAMILIES})
            self.assertEqual(b['ci95'], [value, value]); self.assertEqual(b['ci975'], [value, value])
            self.assertEqual(sum(b['histogram'].values()), 100000)

    def test_holm_exact_two_comparisons(self):
        self.assertEqual(holm({'F1': .01, 'F2': .03}), {'F1': .02, 'F2': .03})
        self.assertEqual(holm({'F1': .8, 'F2': .9}), {'F1': 1, 'F2': 1})

    def test_readiness_independent_and_f0_ready(self):
        rows = [{'family': s['family'], 'acquired_valid_proposal': True, 'leakage': []} for s in SCENARIOS]
        self.assertEqual(interface_ready(rows, True, True)['classification'], 'INTERFACE_READY')
        self.assertEqual(improvement(0, [0, 0], True)['classification'], 'NOT_ESTABLISHED')
        self.assertEqual(interface_ready(rows, True, False)['classification'], 'NOT_CLASSIFIED_INCOMPLETE')

    def test_material_not_ready_missing_family_and_leakage(self):
        rows = [{'family': s['family'], 'acquired_valid_proposal': s['family'] != FAMILIES[0], 'leakage': []} for s in SCENARIOS]
        self.assertEqual(interface_ready(rows, True, True)['classification'], 'INTERFACE_NOT_READY')
        self.assertEqual(improvement(16, [.3, .9], True)['classification'], 'INTERFACE_MEDIATED_IMPROVEMENT')
        for r in rows: r['acquired_valid_proposal'] = True
        rows[0]['leakage'] = ['command']; rows[1]['leakage'] = ['command']
        self.assertEqual(interface_ready(rows, True, True)['classification'], 'INTERFACE_NOT_READY')

    def test_accounting_cache_not_added_and_decimal(self):
        r = fixture_response(S, 'F1'); a = charge(r, PRICING)
        self.assertEqual(a['provider_accounted_tokens'], 1100)
        self.assertEqual(a['prompt_eval_cached_count'], 100)
        self.assertEqual(money(a['calculated_charge_usd']), money('0.0001964'))
        self.assertTrue(forecast(('F0', 'F1', 'F2'), PRICING)['fits_frozen_ceiling'])
        for key in ('prompt_eval_count', 'prompt_eval_cached_count', 'eval_count'):
            bad = deepcopy(r); del bad[key]
            with self.assertRaises(ValueError): usage(bad)


class TransportTests(unittest.TestCase):
    def test_single_send_timeout_error_and_no_retry(self):
        for error in (TimeoutError(), ConnectionError(), RuntimeError('server error')):
            opener = Mock(); opener.open.side_effect = error
            t = NativeTransport('synthetic-key', {'passed': True}, 'separately-authorized-operational-probe', opener)
            with self.assertRaises(type(error)): t.send({'model': 'gpt-oss:120b'})
            with self.assertRaises(PermissionError): t.send({'model': 'gpt-oss:120b'})
            self.assertEqual(opener.open.call_count, 1)

    def test_redirect_no_follow(self):
        with self.assertRaises(RuntimeError): NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other/')

    def test_partial_response_and_byte_cap(self):
        for wire in (b'{', b'x' * 65537):
            receipt = Mock(); receipt.status = 200; receipt.read.return_value = wire
            receipt.__enter__ = Mock(return_value=receipt); receipt.__exit__ = Mock(return_value=False)
            opener = Mock(); opener.open.return_value = receipt
            t = NativeTransport('synthetic-key', {'passed': True}, 'separately-authorized-operational-probe', opener)
            with self.assertRaises(ValueError): t.send({'model': 'gpt-oss:120b'})
            self.assertEqual(t.sends, 1)

    def test_live_transport_denied_without_authorization(self):
        with self.assertRaises(PermissionError): NativeTransport('not-used', {'passed': True})

    def test_no_live_scheduler_transport(self):
        with tempfile.TemporaryDirectory() as temporary:
            ledger = Ledger(temporary)
            try:
                ledger.create('blocked', 'c' * 64, ('F0', 'F1'), ORDER, REGISTRY, PRICING)
                with self.assertRaises(PermissionError):
                    Scheduler(ledger, 'blocked', SCENARIOS).run(Mock(kind='admitted-cloud'))
                self.assertEqual(ledger.requests('blocked'), [])
            finally:
                ledger.close()

    def test_native_http_deadline_and_close_no_redirect_retry(self):
        connection = Mock(); connection.sock = Mock()
        response = Mock(); response.status = 200
        response.read1.side_effect = [canonical(fixture_response(S, 'F1')), b'']
        response.getheader.return_value = 'synthetic-receipt'
        connection.getresponse.return_value = response
        with patch('http.client.HTTPSConnection', return_value=connection):
            t = NativeTransport('synthetic-key', {'passed': True}, 'separately-authorized-operational-probe')
            result, metadata = t.send({'model': 'gpt-oss:120b'})
        self.assertEqual(result['model'], 'gpt-oss:120b')
        self.assertEqual(metadata['request_id'], 'synthetic-receipt')
        self.assertEqual(connection.request.call_count, 1)
        self.assertEqual(connection.close.call_count, 1)
        connection.reset_mock()
        with patch('http.client.HTTPSConnection', return_value=connection), patch('time.monotonic', side_effect=[0, 181]):
            t = NativeTransport('synthetic-key', {'passed': True}, 'separately-authorized-operational-probe')
            with self.assertRaises(TimeoutError): t.send({'model': 'gpt-oss:120b'})
        self.assertEqual(connection.request.call_count, 0)
        self.assertEqual(connection.close.call_count, 1)


class AdmissionTests(unittest.TestCase):
    def evidence(self):
        return {'credential': {k: True for k in ('newly_rotated', 'earlier_revoked', 'environment_only', 'redaction_tests_passed')},
            'identity': {'api_identifier': 'gpt-oss:120b', 'alias': 'gpt-oss:120b-cloud',
                'endpoint': 'https://ollama.com/api/chat', 'adapter_mapping': 'direct API',
                'catalog_identity': 'synthetic-catalog', 'authenticated': True, 'source': 'synthetic-authenticated-metadata'},
            'account': {'authoritative': True, 'source': 'synthetic-account', 'plan': 'Pro',
                'included_available_usd': '2.00', 'additional_purchased_usd': '0.00', 'reload_enabled': False},
            'pricing': deepcopy(PRICING), 'api': {'authoritative': True, 'source': 'synthetic-contract',
                'context_bound': 131072, 'temperature_supported': True, 'think_high_supported': True,
                'accounting_fields': ['prompt_eval_count', 'prompt_eval_cached_count', 'eval_count'], 'concurrency': 3}}

    def test_every_mandatory_credential_prerequisite(self):
        for key in self.evidence()['credential']:
            e = self.evidence(); e['credential'][key] = False
            self.assertFalse(prerequisites(e)['passed'])

    def test_model_route_and_provenance(self):
        self.assertTrue(prerequisites(self.evidence(), ('F0', 'F1', 'F2'))['passed'])
        for key, value in (('api_identifier', 'other'), ('alias', 'other'), ('endpoint', 'http://localhost'), ('authenticated', False)):
            e = self.evidence(); e['identity'][key] = value
            self.assertFalse(prerequisites(e)['passed'])

    def test_funding_accounting_and_price_ceiling(self):
        for key, value in (('plan', 'Free'), ('included_available_usd', '1.99'), ('additional_purchased_usd', '0.01'), ('reload_enabled', True)):
            e = self.evidence(); e['account'][key] = value
            self.assertFalse(prerequisites(e)['passed'])
        e = self.evidence(); e['pricing']['input_per_million'] = '1.00'
        self.assertFalse(prerequisites(e)['passed'])

    def test_no_silent_concurrency_or_parameter_fallback(self):
        e = self.evidence(); e['api']['concurrency'] = 2
        self.assertTrue(prerequisites(e, ('F0', 'F1'))['passed'])
        self.assertFalse(prerequisites(e, ('F0', 'F1', 'F2'))['passed'])
        for key in ('temperature_supported', 'think_high_supported'):
            e = self.evidence(); e['api'][key] = False
            self.assertFalse(prerequisites(e)['passed'])
        e = self.evidence(); e['api']['accounting_fields'] = ['eval_count']
        self.assertFalse(prerequisites(e)['passed'])

    def test_saved_probe_receipt_recovery_is_offline(self):
        with tempfile.TemporaryDirectory() as temporary:
            ledger = Ledger(temporary)
            try:
                ledger.reserve_probe(probe_request(), PRICING, self.evidence())
                # Emulate only the durable state after a saved synthetic receipt; no send occurs.
                response = fixture_response(S, 'F2')
                response['message']['tool_calls'][0]['function']['arguments'] = probe_arguments()
                with ledger.transaction():
                    key = ledger.put(response, 'synthetic-probe-receipt')
                    ledger.db.execute('UPDATE m010_probe SET state=?,response_hash=?', ('RESPONSE_SAVED', key))
                result = ledger.finalize_probe()
                self.assertTrue(result['passed']); self.assertEqual(ledger.probe()['state'], 'COMPLETE')
                with self.assertRaises(ValueError): ledger.start_probe()
            finally:
                ledger.close()


class CampaignTests(unittest.TestCase):
    def test_nine_campaigns_and_export_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for label in 'ABCDEFGHI':
                with self.subTest(label=label):
                    ledger = Ledger(root / label)
                    try:
                        arms = ('F0', 'F1', 'F2') if label == 'E' else ('F0', 'F1')
                        ledger.create(label, 'b' * 64, arms, ORDER, REGISTRY, PRICING)
                        transport = RecordingTransport(SCENARIOS, campaign_handler(label))
                        Scheduler(ledger, label, SCENARIOS).run(transport)
                        destination = root / ('export-' + label)
                        export(ledger, label, SCENARIOS, destination)
                        evidence = json.loads((destination / 'campaign.json').read_bytes())
                        self.assertTrue(replay(destination / 'campaign.zip')['passed'])
                        result = evidence['analysis']; f1 = result['arms']['F1']
                        if label in ('A', 'B', 'I'):
                            self.assertEqual(f1['readiness']['classification'], 'INTERFACE_READY')
                        if label == 'A':
                            self.assertEqual(result['comparisons']['F1_vs_F0']['improvement']['classification'], 'INTERFACE_MEDIATED_IMPROVEMENT')
                        if label == 'B':
                            self.assertEqual(result['arms']['F0']['readiness']['classification'], 'INTERFACE_READY')
                            self.assertEqual(result['comparisons']['F1_vs_F0']['improvement']['classification'], 'NOT_ESTABLISHED')
                        if label == 'C':
                            self.assertEqual(f1['valid'], 16)
                            self.assertEqual(f1['readiness']['classification'], 'INTERFACE_NOT_READY')
                            self.assertEqual(result['comparisons']['F1_vs_F0']['improvement']['classification'], 'INTERFACE_MEDIATED_IMPROVEMENT')
                        if label == 'D': self.assertEqual(f1['valid'], 0)
                        if label == 'E':
                            self.assertEqual(result['arms']['F2']['readiness']['classification'], 'INTERFACE_READY')
                            self.assertEqual(result['comparisons']['F2_vs_F0']['improvement']['classification'], 'INTERFACE_MEDIATED_IMPROVEMENT')
                        if label == 'F':
                            self.assertFalse(result['complete'])
                            self.assertEqual(f1['readiness']['classification'], 'NOT_CLASSIFIED_INCOMPLETE')
                        if label == 'G':
                            self.assertEqual(f1['valid'], 22)
                            self.assertEqual(f1['readiness']['classification'], 'INTERFACE_NOT_READY')
                        if label == 'H': self.assertEqual(f1['truncation_count'], 24)
                        if label == 'I': self.assertEqual(f1['unique_scaffolds'], 2)
                    finally:
                        ledger.close()


    def test_freeze_deferrals_require_explicit_authorization_and_boundary_reasons(self):
        historical = {'passed_permitted_tests': True, 'errors': [], 'failures': [],
                      'research_inference': 0, 'runner_research_calls': 0,
                      'deferred': [['fixture', 'M010_REGRESSION_BOUNDARY:protected-content']]}
        evidence = {'historical_regression': historical, 'deferred_tests': 1,
                    'historical_tests_passed': False, 'historical_permitted_tests_passed': True,
                    'deferral_authorization': 'user-approved-protected-boundary-deferrals'}
        self.assertTrue(regression_gate(evidence))
        for change in ({'deferral_authorization': None}, {'historical_tests_passed': True},
                       {'deferred_tests': 0}, {'historical_permitted_tests_passed': False}):
            self.assertFalse(regression_gate({**evidence, **change}))
        for change in ({'errors': ['failure']}, {'passed_permitted_tests': False},
                       {'deferred': [['fixture', 'ordinary test failure']]}, {'research_inference': 1}):
            self.assertFalse(regression_gate({**evidence, 'historical_regression': {**historical, **change}}))

    def test_freeze_all_test_pass_has_no_deferral_exception(self):
        historical = {'passed_permitted_tests': True, 'errors': [], 'failures': [], 'deferred': [],
                      'research_inference': 0, 'runner_research_calls': 0}
        self.assertTrue(regression_gate({'historical_regression': historical, 'deferred_tests': 0,
                                        'historical_tests_passed': True}))


if __name__ == '__main__':
    report = None
    if '--report' in sys.argv:
        index = sys.argv.index('--report'); report = Path(sys.argv[index + 1]); del sys.argv[index:index + 2]
    paths = list((ROOT / 'src/persistentpi/m010').glob('*.py')) + list((ROOT / 'scripts').glob('m010*.py'))
    sources = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    program = unittest.main(verbosity=2, exit=False)
    result = program.result
    if report:
        atomic_write(report, canonical({'tests_run': result.testsRun, 'passed': result.wasSuccessful(),
            'failures': [(t.id(), e) for t, e in result.failures], 'errors': [(t.id(), e) for t, e in result.errors],
            'runner_calls': 0, 'research_inference': 0, 'operational_probe_executed': False,
            'tested_source_hashes': sources,
            'source_drift': any(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != h for name, h in sources.items())}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
