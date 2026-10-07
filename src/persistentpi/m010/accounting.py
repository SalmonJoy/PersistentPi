"""Provider counters and exact decimal bounds; cached tokens never added twice."""
from decimal import Decimal, InvalidOperation

from .config import DEFAULT, budget


def money(value):
    if not isinstance(value, str):
        raise ValueError('M010_MONEY_TYPE')
    try:
        result = Decimal(value)
    except InvalidOperation:
        raise ValueError('M010_MONEY') from None
    if not result.is_finite() or result < 0:
        raise ValueError('M010_MONEY')
    return result


def rates(pricing):
    if (pricing.get('authoritative') is not True or not pricing.get('source')
            or pricing.get('model') != 'gpt-oss:120b'):
        raise ValueError('M010_PRICING_EVIDENCE')
    return {k: money(pricing[k]) for k in ('input_per_million', 'cached_input_per_million', 'output_per_million')}


def usage(response, enforce_limits=True):
    keys = ('prompt_eval_count', 'prompt_eval_cached_count', 'eval_count')
    if any(type(response.get(k)) is not int or response[k] < 0 for k in keys):
        raise ValueError('M010_ACCOUNTING_MISSING')
    if response['prompt_eval_cached_count'] > response['prompt_eval_count']:
        raise ValueError('M010_ACCOUNTING_LIMIT')
    violations = [name for name, cap in (('prompt_eval_count', 131072), ('eval_count', 4096)) if response[name] > cap]
    if violations and enforce_limits:
        raise ValueError('M010_ACCOUNTING_LIMIT')
    return {**{k: response[k] for k in keys},
            'provider_accounted_tokens': response['prompt_eval_count'] + response['eval_count'],
            'reasoning_tokens': None, 'ceiling_violations': violations}


def charge(response, pricing):
    u, r = usage(response, enforce_limits=False), rates(pricing)
    value = (Decimal(u['prompt_eval_count'] - u['prompt_eval_cached_count']) * r['input_per_million']
        + Decimal(u['prompt_eval_cached_count']) * r['cached_input_per_million']
        + Decimal(u['eval_count']) * r['output_per_million']) / 1000000
    return {**u, 'calculated_charge_usd': str(value), 'actual_debit_usd': None,
            'basis': 'authoritative counters and rates; calculated, not an observed account debit'}


def reservation(pricing):
    r = rates(pricing)
    value = (Decimal(131072) * max(r['input_per_million'], r['cached_input_per_million'])
             + Decimal(4096) * r['output_per_million']) / 1000000
    return {'provider_tokens': 135168, 'included_credit_usd': str(value), 'requests': 1}


def forecast(arms, pricing, probe=True):
    b, unit = budget(arms), reservation(pricing)
    total = Decimal(unit['included_credit_usd']) * (b['requests'] + int(probe))
    return {'arms': list(arms), 'feasibility_requests': b['requests'],
            'feasibility_tokens': b['provider_tokens'], 'probe_requests': int(probe),
            'probe_tokens': 135168 if probe else 0, 'combined_credit_bound_usd': str(total),
            'fits_frozen_ceiling': total <= money(DEFAULT['limits']['included_credit_usd'])}
