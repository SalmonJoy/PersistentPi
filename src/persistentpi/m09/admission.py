"""M0.9C-R operational admission; no benchmark or campaign execution surface."""
from copy import deepcopy
from contextlib import closing
import datetime as dt
import hashlib
import http.client
import json
from pathlib import Path
import sqlite3
import time

from ..contracts import canonical, digest
from .planner import PlannerReply

ALIAS = 'gpt-oss:120b-cloud'
HOST = 'ollama.com'
ENDPOINT = 'https://ollama.com/api/chat'
ADAPTER = 'm09cr-admission-1'
STATES = ('BLOCKED', 'READY_FOR_ADMISSION_PROBE', 'ADMITTED', 'BLOCKED_AFTER_PROBE')


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def amended_configuration(parent, amendment):
    if (amendment['protocol_version'] != '0.6' or parent['protocol_version'] != '0.6'
            or parent['planner']['model'] != 'glm-5.3'
            or amendment['requested_alias'] != ALIAS
            or amendment['purchased_credit_ceiling'] != 0):
        raise ValueError('Amendment parent/identity mismatch')
    result = deepcopy(parent)
    result['planner']['model'] = ALIAS
    result['accounting_scope']['planner'] = (
        'provider_accounted_tokens = prompt_eval_count + eval_count; '
        'cached count separate; thinking content provenance only')
    if (result['planner']['max_requests'] != 8 or result['planner']['max_tokens'] != 200000
            or result['planner']['purchased_credit_ceiling'] != 0):
        raise ValueError('Frozen campaign ceilings changed')
    return result


def credential_metadata(environment):
    return {'dedicated_key_present': bool(environment.get('PERSISTENTPI_PLANNER_API_KEY')),
            'rotation_attested': environment.get('PERSISTENTPI_PLANNER_CREDENTIAL_ROTATED') == '1',
            'credential_used': False, 'credential_value_recorded': False}


def credential_secrets(environment):
    return tuple(value for name, value in environment.items()
                 if name in ('OLLAMA_API_KEY', 'PERSISTENTPI_PLANNER_API_KEY') and value)


def safe_bytes(value, secrets=()):
    raw = canonical(value)
    # Reject raw and JSON-escaped forms before any disk or database write.
    for secret in secrets:
        if secret and (secret.encode() in raw or json.dumps(secret)[1:-1].encode() in raw):
            raise ValueError('Credential disclosure blocked')
    return raw


def usage(response):
    result = {}
    for name in ('prompt_eval_count', 'eval_count'):
        value = response.get(name)
        if type(value) is not int or value < 0:
            raise ValueError('Authoritative usage unavailable')
        result[name] = value
    cached = response.get('prompt_eval_cached_count')
    if cached is not None and (type(cached) is not int or not 0 <= cached <= result['prompt_eval_count']):
        raise ValueError('Invalid cached token count')
    result['prompt_eval_cached_count'] = cached
    result['provider_accounted_tokens'] = result['prompt_eval_count'] + result['eval_count']
    return result


def proposal_reply(response, identity, latency, seed_supported=False):
    """Bridge to the existing campaign contract using provider totals exactly."""
    counted = usage(response)
    return PlannerReply(response, identity, counted['prompt_eval_count'], counted['eval_count'],
                        reasoning_in_output=True, latency=latency,
                        seed_supported=seed_supported).validate()


def resolve_identity(catalog, model_metadata, seed_supported=None):
    if seed_supported is not None and type(seed_supported) is not bool:
        raise ValueError('Seed support must be established')
    matches = [row for row in catalog.get('models', [])
               if row.get('name') in (ALIAS, ALIAS.removesuffix('-cloud'))]
    if len(matches) != 1:
        raise ValueError('Exact GPT-OSS model mapping unavailable')
    row = matches[0]
    if model_metadata.get('thinking', {}).get('values') is None or 'high' not in model_metadata['thinking']['values']:
        raise ValueError('High thinking mapping unavailable')
    return {'requested_alias': ALIAS, 'api_identifier': row['name'],
            'catalog_tag': row.get('model'), 'digest': row.get('digest'),
            'version': row.get('version'), 'modified_at': row.get('modified_at'),
            'endpoint': ENDPOINT, 'adapter_version': ADAPTER,
            'thinking_metadata': model_metadata['thinking'],
            'parameter_mapping': {'thinking': {'field': 'think', 'value': 'high'},
                                  'temperature': {'field': 'options.temperature', 'value': 0},
                                  'output': {'field': 'options.num_predict', 'probe_maximum': 128,
                                             'proposal_maximum': 4096},
                                  'seed': {'supported': seed_supported is True,
                                           'support_status': ('not_established' if seed_supported is None
                                                              else 'supported' if seed_supported else 'unsupported'),
                                           'value': 42 if seed_supported else None}},
            'backend_weights_immutability_proven': False}


def assert_identity(frozen, current):
    if frozen != current:
        raise ValueError('Cloud identity/contract drift')


def probe_request(identity):
    if (identity.get('requested_alias') != ALIAS or identity.get('endpoint') != ENDPOINT
            or identity.get('adapter_version') != ADAPTER
            or identity.get('api_identifier') not in (ALIAS, ALIAS.removesuffix('-cloud'))):
        raise ValueError('Unapproved probe identity')
    options = {'temperature': 0, 'num_predict': 128}
    if identity['parameter_mapping']['seed']['supported']:
        options['seed'] = 42
    return {'model': identity['api_identifier'],
            'messages': [{'role': 'user', 'content': 'Reply with the single word READY.'}],
            'think': 'high', 'stream': False, 'options': options}


def prerequisites(credential, redaction_passed, account):
    failures = []
    if not credential.get('dedicated_key_present') or not credential.get('rotation_attested'):
        failures.append('newly_rotated_environment_credential_not_established')
    if redaction_passed is not True:
        failures.append('credential_redaction_checks_not_passed')
    if not account.get('authoritative') or not account.get('evidence_sha256') or not account.get('source'):
        failures.append('authoritative_account_evidence_not_established')
    if account.get('free_model_entitlement') is not True:
        failures.append('included_free_model_entitlement_not_established')
    if account.get('bounded_probe_allowance_sufficient') is not True:
        failures.append('bounded_probe_allowance_not_established')
    if not (account.get('purchased_balance_zero') is True
            or account.get('purchased_consumption_prevented') is True):
        failures.append('purchased_credit_consumption_not_excluded')
    return failures


def admission_decision(credential, redaction_passed, account, contracts, probe=None):
    failures = prerequisites(credential, redaction_passed, account)
    required = ('identity', 'temperature', 'thinking', 'output_cap', 'usage', 'response', 'deadline')
    unresolved = [name for name in required if contracts.get(name) is not True]
    if probe is not None:
        failures += probe.get('failures', [])
        state = 'BLOCKED_AFTER_PROBE' if failures or unresolved else 'ADMITTED'
    elif failures:
        state = 'BLOCKED'
    elif not unresolved:
        state = 'ADMITTED'
    elif contracts.get('unresolved_are_probe_resolvable') is True:
        state = 'READY_FOR_ADMISSION_PROBE'
    else:
        state = 'BLOCKED'
    return {'state': state, 'prerequisite_failures': failures, 'unresolved_contracts': unresolved,
            'research_authorized': False}


class AdmissionLedger:
    """One operational opportunity, durable before send; never a proposal ledger."""
    def __init__(self, path, amendment_hash, secrets=()):
        safe_bytes({'amendment_hash': amendment_hash}, secrets)
        self.path, self.secrets = Path(path), secrets
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, timeout=10)
        self.db.execute('PRAGMA journal_mode=DELETE')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS identity(id INTEGER PRIMARY KEY CHECK(id=1), hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events(sequence INTEGER PRIMARY KEY, kind TEXT NOT NULL, json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS probe(id INTEGER PRIMARY KEY CHECK(id=1), state TEXT NOT NULL,
                request TEXT NOT NULL, request_hash TEXT NOT NULL, reservation TEXT NOT NULL,
                response TEXT, receipt TEXT);
            CREATE TRIGGER IF NOT EXISTS identity_immutable BEFORE UPDATE ON identity
                BEGIN SELECT RAISE(ABORT,'Immutable amendment identity'); END;
            CREATE TRIGGER IF NOT EXISTS identity_no_delete BEFORE DELETE ON identity
                BEGIN SELECT RAISE(ABORT,'Immutable amendment identity'); END;
            CREATE TRIGGER IF NOT EXISTS probe_no_delete BEFORE DELETE ON probe
                BEGIN SELECT RAISE(ABORT,'Single probe opportunity cannot be deleted'); END;
            CREATE TRIGGER IF NOT EXISTS probe_transition BEFORE UPDATE ON probe
                WHEN OLD.state != 'STARTED' OR NEW.state NOT IN ('COMPLETED','INDETERMINATE')
                OR OLD.request != NEW.request OR OLD.request_hash != NEW.request_hash
                OR OLD.reservation != NEW.reservation
                BEGIN SELECT RAISE(ABORT,'Invalid probe transition'); END;
            CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
                BEGIN SELECT RAISE(ABORT,'Immutable admission event'); END;
            CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
                BEGIN SELECT RAISE(ABORT,'Immutable admission event'); END;
        ''')
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO identity VALUES(1,?)', (amendment_hash,))
        if self.db.execute('SELECT hash FROM identity').fetchone()[0] != amendment_hash:
            self.db.close()
            raise ValueError('Admission amendment drift')
        with self.db:
            self.db.execute("UPDATE probe SET state='INDETERMINATE',receipt=? WHERE state='STARTED'",
                            (safe_bytes({'failures': ['indeterminate_after_restart']}, secrets).decode(),))

    def event(self, kind, value):
        safe_bytes({'kind': kind, 'value': value}, self.secrets)
        raw = safe_bytes(value, self.secrets).decode()
        with self.db:
            self.db.execute('INSERT INTO events(kind,json) VALUES(?,?)', (kind, raw))

    def start_probe(self, identity, decision):
        if decision['state'] != 'READY_FOR_ADMISSION_PROBE':
            raise ValueError('Probe admission prerequisites not satisfied')
        request = probe_request(identity)
        raw = safe_bytes(request, self.secrets)
        reservation = safe_bytes({'transmissions': 1, 'generated_tokens': 128,
                                  'wall_seconds': 180, 'response_bytes': 65536,
                                  'research_proposal_requests': 0, 'research_proposal_tokens': 0}, self.secrets)
        with self.db:
            self.db.execute('INSERT INTO probe VALUES(1,?,?,?,?,NULL,NULL)',
                            ('STARTED', raw.decode(), hashlib.sha256(raw).hexdigest(), reservation.decode()))
        return request

    def finish_probe(self, response, receipt):
        response_raw = safe_bytes(response, self.secrets).decode()
        receipt_raw = safe_bytes(receipt, self.secrets).decode()
        with self.db:
            cursor = self.db.execute("UPDATE probe SET state=?,response=?,receipt=? WHERE id=1 AND state='STARTED'",
                                     ('INDETERMINATE' if receipt.get('indeterminate') else 'COMPLETED', response_raw, receipt_raw))
            if cursor.rowcount != 1:
                raise ValueError('Probe is not durably started')

    def snapshot(self):
        row = self.db.execute('SELECT state,request_hash,reservation,receipt FROM probe').fetchone()
        return {'amendment_hash': self.db.execute('SELECT hash FROM identity').fetchone()[0],
                'probe_count': int(row is not None), 'probe': None if row is None else {
                    'state': row[0], 'request_hash': row[1], 'reservation': json.loads(row[2]),
                    'receipt': None if row[3] is None else json.loads(row[3])},
                'proposal_requests': 0, 'proposal_tokens': 0, 'runner_research_calls': 0,
                'qualification_access': False, 'final_access': False, 'hidden_scoring': False}

    def backup(self, target):
        with closing(sqlite3.connect(target)) as copy:
            self.db.backup(copy)

    def close(self):
        self.db.close()


class NativeCloudTransport:
    """Explicit endpoints, no redirects/retries, no exception/request-header logging."""
    def __init__(self, environment):
        metadata = credential_metadata(environment)
        if not metadata['dedicated_key_present'] or not metadata['rotation_attested']:
            raise ValueError('Rotated environment credential required before authentication')
        self._secret = environment['PERSISTENTPI_PLANNER_API_KEY']

    def _request(self, method, endpoint, body=None, timeout=20):
        if (method, endpoint) not in (('GET', '/api/tags'), ('POST', '/api/show'), ('POST', '/api/chat')):
            raise ValueError('Unapproved cloud endpoint')
        connection = http.client.HTTPSConnection(HOST, timeout=timeout)
        started = time.monotonic()
        try:
            connection.connect()
            wire = connection.sock

            def remaining():
                seconds = timeout - (time.monotonic() - started)
                if seconds <= 0:
                    raise RuntimeError('Cloud request deadline')
                wire.settimeout(seconds)

            remaining()
            connection.request(method, endpoint, None if body is None else canonical(body),
                               {'Authorization': 'Bearer ' + self._secret, 'Content-Type': 'application/json'})
            remaining()
            response = connection.getresponse()
            if response.status != 200:
                raise RuntimeError('Cloud response not successful')
            pieces, size = [], 0
            while size <= 65536:
                remaining()
                chunk = response.read1(65537 - size)
                if not chunk:
                    break
                pieces.append(chunk)
                size += len(chunk)
            raw = b''.join(pieces)
            if len(raw) > 65536:
                raise RuntimeError('Cloud response byte ceiling')
            result = json.loads(raw)
            safe_bytes(result, (self._secret,))
            self.last_response_bytes = len(raw)
            self.last_response_sha256 = hashlib.sha256(raw).hexdigest()
            return result
        except Exception:
            raise RuntimeError('Cloud request failed; diagnostic payload suppressed') from None
        finally:
            connection.close()

    def metadata(self):
        catalog = self._request('GET', '/api/tags')
        matches = [r['name'] for r in catalog.get('models', [])
                   if r.get('name') in (ALIAS, ALIAS.removesuffix('-cloud'))]
        if len(matches) != 1:
            raise ValueError('Cloud alias mapping unavailable')
        return catalog, self._request('POST', '/api/show', {'model': matches[0]})

    def probe(self, request):
        expected_options = {'temperature': 0, 'num_predict': 128}
        if request.get('options', {}).get('seed') == 42:
            expected_options['seed'] = 42
        if (request.get('model') not in (ALIAS, ALIAS.removesuffix('-cloud'))
                or request != {'model': request.get('model'),
                               'messages': [{'role': 'user', 'content': 'Reply with the single word READY.'}],
                               'think': 'high', 'stream': False, 'options': expected_options}):
            raise ValueError('Only the frozen neutral admission probe is permitted')
        return self._request('POST', '/api/chat', request, timeout=180)


def resolve_admission(ledger, environment, redaction_passed, account, contracts,
                      allow_probe=False, transport=None, seed_supported=None):
    """Trusted operational orchestration. No Runner, cohort or search imports."""
    credential = credential_metadata(environment)
    if ledger.snapshot()['probe_count']:
        previous = ledger.db.execute("SELECT json FROM events WHERE kind='decision' ORDER BY sequence DESC LIMIT 1").fetchone()
        if (ledger.snapshot()['probe']['state'] == 'COMPLETED' and previous
                and json.loads(previous[0])['state'] == 'ADMITTED'):
            return json.loads(previous[0])
        decision = {'state': 'BLOCKED_AFTER_PROBE', 'prerequisite_failures': ['probe_opportunity_already_consumed'],
                    'unresolved_contracts': [], 'research_authorized': False}
        ledger.event('decision', decision)
        return decision
    ledger.event('credential_metadata', credential)
    ledger.event('account_evidence', account)
    if prerequisites(credential, redaction_passed, account):
        decision = admission_decision(credential, redaction_passed, account, contracts)
        ledger.event('decision', decision)
        return decision
    transport = transport or NativeCloudTransport(environment)
    try:
        catalog, metadata = transport.metadata()
        frozen = resolve_identity(catalog, metadata, seed_supported)
    except Exception:
        decision = {'state': 'BLOCKED', 'prerequisite_failures': ['authenticated_metadata_unresolved'],
                    'unresolved_contracts': [], 'research_authorized': False}
        ledger.event('decision', decision)
        return decision
    ledger.event('cloud_identity', frozen)
    verified = {**contracts, 'identity': True, 'thinking': True}
    ledger.event('contracts', verified)
    decision = admission_decision(credential, redaction_passed, account, verified)
    if decision['state'] == 'READY_FOR_ADMISSION_PROBE' and allow_probe:
        receipt, verified = execute_probe(ledger, frozen, decision, transport, verified)
        ledger.event('contracts_after_probe', verified)
        decision = admission_decision(credential, redaction_passed, account, verified, receipt)
    ledger.event('decision', decision)
    return decision


def execute_probe(ledger, identity, decision, transport, contracts):
    request = ledger.start_probe(identity, decision)
    started = time.monotonic()
    response = None
    try:
        response = transport.probe(request)
        counted = usage(response)
        message = response.get('message', {})
        failures = []
        if response.get('model') != identity['api_identifier']:
            failures.append('returned_model_identity_mismatch')
        if response.get('done') is not True or response.get('done_reason') not in ('stop', 'length'):
            failures.append('completion_contract_unresolved')
        if counted['eval_count'] > 128:
            failures.append('generated_token_ceiling')
        if not isinstance(message.get('content'), str) or not isinstance(message.get('thinking'), str):
            failures.append('thinking_or_content_contract_unresolved')
        elapsed = time.monotonic() - started
        observed_size = getattr(transport, 'last_response_bytes', None)
        response_size = observed_size if type(observed_size) is int else len(canonical(response))
        if elapsed > 180 or response_size > 65536:
            failures.append('probe_resource_ceiling')
        receipt = {**counted, 'failures': failures, 'latency_seconds': elapsed,
                   'done': response.get('done'), 'done_reason': response.get('done_reason'),
                   'response_bytes': response_size,
                   'response_byte_count_basis': 'wire' if type(observed_size) is int else 'canonical_fixture_json',
                   'response_hash': hashlib.sha256(canonical(response)).hexdigest(),
                   'thinking_present': 'thinking' in message,
                   'content_present': 'content' in message, 'identity': response.get('model'),
                   'operational_only': True, 'proposal_requests': 0, 'proposal_tokens': 0}
        # Only observable checks become established; parameter semantics need independent evidence.
        updated = {**contracts, 'usage': True, 'response': not failures,
                   'identity': 'returned_model_identity_mismatch' not in failures}
    except Exception:
        receipt = {'failures': ['indeterminate_or_invalid_probe'], 'indeterminate': True,
                   'operational_only': True, 'proposal_requests': 0, 'proposal_tokens': 0}
        updated = contracts
        try:
            safe_bytes(response, ledger.secrets)
        except ValueError:
            response = None
            receipt['unsafe_response_excluded'] = True
    ledger.finish_probe(response, receipt)
    return receipt, updated
