"""Pro-only operational policy; no Runner, search, cohort or evaluator imports."""
from copy import deepcopy
from contextlib import closing
from decimal import Decimal, InvalidOperation
from pathlib import Path
import http.client
import json
import sqlite3
import time

from .admission import (NativeCloudTransport, admission_decision, credential_metadata,
                        execute_probe, resolve_identity, assert_identity, safe_bytes)

ACCESS = {
    'provider': 'ollama-cloud', 'plan': 'Pro', 'monthly_access_cost_usd': '20.00',
    'already_purchased_by_operator': True,
    'permitted_inference_funding': 'included Pro usage credits only',
    'additional_credit_ceiling_usd': '0.00', 'automatic_reload': False,
    'manual_top_up': False, 'subscription_upgrade': False, 'additional_account': False,
    'model_provider_fallback': False, 'exhaustion_action': 'STOP',
}


def amended_pro_configuration(parent, amendment):
    if (amendment.get('amendment_id') != 'M0.9C-R2/1'
            or amendment.get('protocol_version') != '0.6'
            or amendment.get('requested_alias') != 'gpt-oss:120b-cloud'
            or amendment.get('access') != ACCESS
            or type(amendment.get('proposal_requests')) is not int
            or amendment['proposal_requests'] != 8
            or type(amendment.get('proposal_provider_accounted_tokens')) is not int
            or amendment['proposal_provider_accounted_tokens'] != 200000
            or amendment.get('research_authorized') is not False
            or parent['planner']['model'] != 'gpt-oss:120b-cloud'
            or parent['protocol_version'] != '0.6'
            or parent['planner']['max_requests'] != 8
            or parent['planner']['max_tokens'] != 200000
            or parent['planner']['purchased_credit_ceiling'] != 0
            or 'operational_access' in parent):
        raise ValueError('Unapproved Pro amendment')
    result = deepcopy(parent)
    result['operational_access'] = deepcopy(ACCESS)
    result['planner']['feasibility'] = 'fixed pre-purchased Pro access; included credits only; no additional credits or fallback'
    result['accounting_scope']['monetary'] = 'USD20/month access cost separate; actual probe/proposal included-credit usage separate; additional purchased credits USD0; STOP on exhaustion'
    return result


def money(value):
    if not isinstance(value, str):
        raise ValueError('Decimal evidence must be a string')
    try:
        result = Decimal(value)
    except InvalidOperation:
        raise ValueError('Invalid decimal evidence') from None
    if not result.is_finite() or result < 0:
        raise ValueError('Invalid decimal evidence')
    return result


def allowance(account, pricing, context_tokens):
    if (pricing.get('authoritative') is not True or not pricing.get('source')
            or pricing.get('model') != 'gpt-oss:120b'
            or type(context_tokens) is not int or not 0 < context_tokens <= 1000000):
        raise ValueError('Authoritative pricing/context required')
    rates = {k: money(pricing[k]) for k in ('input_per_million', 'cached_input_per_million', 'output_per_million')}
    highest = max(rates.values())
    campaign = Decimal(200000) * highest / Decimal(1000000)
    probe = Decimal(context_tokens) * max(rates['input_per_million'], rates['cached_input_per_million']) / Decimal(1000000)
    probe += Decimal(128) * rates['output_per_million'] / Decimal(1000000)
    balance = money(account['included_balance_lower_bound_usd'])
    return {'proposal_requests': 8, 'proposal_tokens': 200000,
            'campaign_credit_upper_bound_usd': str(campaign),
            'probe_credit_upper_bound_usd': str(probe),
            'combined_credit_upper_bound_usd': str(campaign + probe),
            'included_balance_lower_bound_usd': str(balance),
            'campaign_and_probe_fit': balance >= campaign + probe,
            'probe_fits': balance >= probe, 'input_reservation_tokens': context_tokens,
            'assumptions': 'full advertised context for probe input; all proposal tokens at highest price; no caching savings; not actual usage',
            'access_plan_monthly_usd': '20.00', 'additional_credit_ceiling_usd': '0.00'}


def rotation_attested(attestation):
    return (attestation.get('replacement_key') is True
            and attestation.get('earlier_key_revoked') is True
            and attestation.get('source') == 'explicit user/operator attestation')


def pro_decision(credential, redaction, account, contracts, forecast, probe=None):
    failures = []
    if account.get('plan') != 'Pro' or account.get('authoritative') is not True:
        failures.append('authenticated_Pro_entitlement_not_established')
    if account.get('auto_reload_enabled') is not False:
        failures.append('auto_reload_off_not_established')
    if account.get('additional_balance_zero') is not True:
        failures.append('zero_additional_credit_balance_not_established')
    if forecast.get('campaign_and_probe_fit') is not True:
        failures.append('included_campaign_allowance_not_established')
    adapted = {**account, 'purchased_balance_zero': account.get('additional_balance_zero'),
               'bounded_probe_allowance_sufficient': forecast.get('probe_fits') is True}
    result = admission_decision(credential, redaction, adapted, contracts, probe)
    if failures:
        result['state'] = 'BLOCKED_AFTER_PROBE' if probe is not None else 'BLOCKED'
        result['prerequisite_failures'] += failures
    return result


def calculated_charge(response, pricing):
    from .admission import usage
    counts = usage(response)
    cached = counts['prompt_eval_cached_count']
    if cached is None:
        return {'actual_charge_usd': None, 'calculated_charge_usd': None,
                'reason': 'cached count unavailable; do not silently assume zero',
                'uncached_price_upper_bound_usd': str((Decimal(counts['prompt_eval_count']) * money(pricing['input_per_million'])
                     + Decimal(counts['eval_count']) * money(pricing['output_per_million'])) / Decimal(1000000))}
    total = (Decimal(counts['prompt_eval_count'] - cached) * money(pricing['input_per_million'])
             + Decimal(cached) * money(pricing['cached_input_per_million'])
             + Decimal(counts['eval_count']) * money(pricing['output_per_million'])) / Decimal(1000000)
    return {'actual_charge_usd': None, 'calculated_charge_usd': str(total),
            'basis': 'provider token counts and published rates; not an observed account debit'}


def load_credential(path, attestation):
    if not rotation_attested(attestation):
        raise ValueError('Explicit replacement/revocation attestation required')
    values = []
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        name, separator, value = line.strip().removeprefix('export ').partition('=')
        if separator and name.strip() == 'OLLAMA_API_KEY':
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            values.append(value)
    if len(values) != 1 or not values[0] or any(c.isspace() for c in values[0]):
        raise ValueError('Missing/invalid private credential')
    return {'PERSISTENTPI_PLANNER_API_KEY': values[0], 'PERSISTENTPI_PLANNER_CREDENTIAL_ROTATED': '1'}


def prior_probe_consumed(paths):
    """Read only explicitly named operational ledgers, never research databases."""
    consumed = False
    for path in paths:
        path = Path(path).resolve(strict=True)
        with closing(sqlite3.connect(path.as_uri() + '?mode=ro&immutable=1', uri=True)) as db:
            if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Prior operational ledger integrity failed')
            consumed |= db.execute('SELECT COUNT(*) FROM probe').fetchone()[0] != 0
    return consumed


def resolve_pro_admission(ledger, environment, redaction, account, contracts,
                          forecast, identity, prior_paths, transport, allow_probe=False):
    """One operational decision; no benchmark content or research execution."""
    if prior_probe_consumed(prior_paths) or ledger.snapshot()['probe_count']:
        result = {'state':'BLOCKED_AFTER_PROBE', 'prerequisite_failures':['probe_opportunity_already_consumed'],
                  'unresolved_contracts':[], 'research_authorized':False}
        ledger.event('decision',result)
        return result
    credential = credential_metadata(environment)
    ledger.event('credential_metadata',credential)
    ledger.event('account_evidence',account)
    ledger.event('allowance_forecast',forecast)
    decision = pro_decision(credential,redaction,account,contracts,forecast)
    if decision['state'] == 'BLOCKED':
        ledger.event('decision',decision)
        return decision
    try:
        catalog, metadata = transport.metadata()
        current = resolve_identity(catalog,metadata,None)
        assert_identity(identity,current)
    except Exception:
        decision = {'state':'BLOCKED', 'prerequisite_failures':['model_metadata_identity_or_contract_drift'],
                    'unresolved_contracts':[], 'research_authorized':False}
        ledger.event('decision',decision)
        return decision
    ledger.event('cloud_identity',identity)
    ledger.event('contracts',contracts)
    ledger.event('decision_before_probe',decision)
    if decision['state'] == 'READY_FOR_ADMISSION_PROBE' and allow_probe:
        receipt, updated = execute_probe(ledger,identity,decision,transport,contracts)
        receipt['http_status'] = getattr(transport,'last_http_status',None)
        ledger.event('operational_http_receipt',{'http_status':receipt['http_status']})
        ledger.event('contracts_after_probe',updated)
        decision = pro_decision(credential,redaction,account,updated,forecast,receipt)
    ledger.event('decision',decision)
    return decision


class ObservedCloudTransport(NativeCloudTransport):
    """Same native adapter mapping, with bounded HTTP-status provenance added."""
    def _request(self, method, endpoint, body=None, timeout=20):
        from ..contracts import canonical
        if (method, endpoint) not in (('GET', '/api/tags'), ('POST', '/api/show'), ('POST', '/api/chat'), ('POST', '/api/me')):
            raise ValueError('Unapproved operational endpoint')
        self.last_http_status = None
        connection = http.client.HTTPSConnection('ollama.com', timeout=timeout)
        started = time.monotonic()
        try:
            connection.connect()
            wire = connection.sock
            def remaining():
                seconds = timeout - (time.monotonic() - started)
                if seconds <= 0:
                    raise RuntimeError('Deadline exceeded')
                wire.settimeout(seconds)
            remaining()
            connection.request(method, endpoint, None if body is None else canonical(body),
                               {'Authorization': 'Bearer ' + self._secret, 'Content-Type': 'application/json'})
            remaining()
            response = connection.getresponse()
            self.last_http_status = response.status
            if response.status != 200:
                raise RuntimeError('Unsuccessful API status')
            pieces, size = [], 0
            while size <= 65536:
                remaining()
                chunk = response.read1(65537 - size)
                if not chunk:
                    break
                pieces.append(chunk)
                size += len(chunk)
            raw = b''.join(pieces)
            if size > 65536:
                raise RuntimeError('Response byte ceiling')
            result = json.loads(raw)
            safe_bytes(result, (self._secret,))
            self.last_response_bytes = size
            import hashlib
            self.last_response_sha256 = hashlib.sha256(raw).hexdigest()
            return result
        except Exception:
            raise RuntimeError('Operational cloud request failed; payload suppressed') from None
        finally:
            connection.close()
