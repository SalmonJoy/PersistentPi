"""Evidence-based future admission. No account or credential is read implicitly."""
from copy import deepcopy
from ..contracts import canonical
from .accounting import forecast, money, rates, usage
from .completion import complete
from .config import DEFAULT
from .f2 import arguments
from .render import probe_arguments

MANDATORY_IDENTITY = ('api_identifier', 'alias', 'endpoint', 'adapter_mapping', 'catalog_identity')


def prerequisites(evidence, arms=('F0', 'F1')):
    failures = []
    credential = evidence.get('credential', {})
    for name in ('newly_rotated', 'earlier_revoked', 'environment_only', 'redaction_tests_passed'):
        if credential.get(name) is not True:
            failures.append('credential.' + name)
    identity = evidence.get('identity', {})
    if any(not identity.get(k) for k in MANDATORY_IDENTITY):
        failures.append('identity.provenance')
    if (identity.get('api_identifier') != 'gpt-oss:120b' or identity.get('alias') != 'gpt-oss:120b-cloud'
            or identity.get('endpoint') != 'https://ollama.com/api/chat'
            or identity.get('authenticated') is not True or identity.get('source') is None):
        failures.append('identity.admitted_route')
    account = evidence.get('account', {})
    try:
        if (account.get('authoritative') is not True or not account.get('source')
                or account.get('plan') != 'Pro' or money(account['included_available_usd']) < money('2.00')
                or money(account['additional_purchased_usd']) != 0 or account.get('reload_enabled') is not False):
            failures.append('account.included_funding')
    except (KeyError, ValueError):
        failures.append('account.included_funding')
    try:
        pricing = evidence['pricing']
        rates(pricing)
        if not forecast(arms, pricing, True)['fits_frozen_ceiling']:
            failures.append('account.forecast')
    except (KeyError, ValueError):
        failures.append('account.pricing')
    api = evidence.get('api', {})
    if (api.get('authoritative') is not True or not api.get('source')
            or api.get('context_bound') != 131072 or api.get('temperature_supported') is not True
            or api.get('think_high_supported') is not True):
        failures.append('api.contract')
    if api.get('accounting_fields') != ['prompt_eval_count', 'prompt_eval_cached_count', 'eval_count']:
        failures.append('api.accounting')
    if type(api.get('concurrency')) is not int or api['concurrency'] < len(arms):
        failures.append('api.concurrency')
    return {'passed': not failures, 'failures': failures, 'arms': list(arms),
            'state': 'READY_FOR_ADMISSION_PROBE' if not failures else 'BLOCKED',
            'identity': deepcopy(identity), 'concurrency': api.get('concurrency')}


def probe_result(response, completion_evidence=None):
    try:
        if response.get('model') != 'gpt-oss:120b':
            raise ValueError('M010_PROVIDER_IDENTITY')
        meaning = complete(response, completion_evidence)
        counters = usage(response)
        if canonical(arguments(response)) != canonical(probe_arguments()):
            raise ValueError('M010_PROBE_ARGUMENTS')
        return {'passed': True, 'state': 'ADMITTED', 'completion': meaning, 'usage': counters}
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        return {'passed': False, 'state': 'BLOCKED_AFTER_PROBE', 'reason': str(exc),
                'done_reason': response.get('done_reason') if isinstance(response, dict) else None}


def arm_decision(common, offline_f2, probe=None):
    if not common['passed']:
        return {'state': 'BLOCKED', 'arms': [], 'reason': 'common prerequisites'}
    if not offline_f2:
        return {'state': 'ADMITTED', 'arms': ['F0', 'F1'], 'f2': 'offline infeasible'}
    if probe is None:
        return {'state': 'READY_FOR_ADMISSION_PROBE', 'arms': [], 'f2': 'unestablished'}
    if probe['passed']:
        return {'state': 'ADMITTED', 'arms': ['F0', 'F1', 'F2'], 'f2': 'admitted', 'requires_concurrency': 3}
    if probe.get('reason') in ('M010_PROVIDER_IDENTITY', 'M010_ACCOUNTING_MISSING', 'M010_ACCOUNTING_LIMIT',
                               'M010_COMPLETION_UNESTABLISHED'):
        return {'state': 'BLOCKED_AFTER_PROBE', 'arms': [], 'reason': probe['reason']}
    return {'state': 'ADMITTED', 'arms': ['F0', 'F1'], 'f2': 'tool capability failed', 'requires_concurrency': 2}
