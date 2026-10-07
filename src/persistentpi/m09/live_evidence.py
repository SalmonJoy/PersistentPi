"""Separate non-generating API evidence from included-only billing evidence."""
from dataclasses import dataclass, asdict
import datetime as dt
import json
from pathlib import Path
import re

from ..contracts import digest
from .admission import assert_identity, usage
from .pro_admission import allowance, money

SCHEMA = Path(__file__).resolve().parents[3]/'configs/m09cl2-account-schema.json'


class EvidenceError(ValueError):
    """A fixed, secret-free condition suitable for a failed preflight receipt."""


@dataclass(frozen=True)
class AccountEvidence:
    version: str
    artifact_hash: str
    observation_hash: str
    source: str
    observed_at: str
    age_seconds: float
    plan: str
    allowance: dict
    purchased_balance_zero: bool
    auto_reload_enabled: bool

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class ApiEvidence:
    version: str
    identity: dict
    authentication: dict
    prior_probe: dict

    def to_dict(self):
        return asdict(self)


def authentication_evidence(response, status):
    # Subscription fields are optional. Never retain user IDs or raw /api/me data.
    if status != 200 or not isinstance(response, dict) or response.get('error'):
        raise EvidenceError('api_authentication_not_established')
    value = response.get('plan')
    optional = {'present': 'plan' in response, 'type': type(value).__name__,
                'value': value if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,32}', value) else None}
    return {'route': 'POST /api/me', 'http_status': status,
            'accepted_authenticated_metadata_request': True,
            'subscription_evidence_used': False, 'optional_plan': optional,
            'unknown_fields': 'ignored; response/user identifiers not retained'}


def validate_account(account, pricing, now=None):
    schema = json.loads(SCHEMA.read_bytes())
    if not isinstance(account, dict) or set(account)-set(schema['allowed']):
        raise EvidenceError('account_evidence_schema_invalid')
    if any(name not in account for name in schema['required']):
        raise EvidenceError('account_evidence_required_field_missing')
    if (account['schema_version'] != schema['version'] or account['plan'] != 'Pro'
            or account['authoritative'] is not True or account['current_operator_attestation'] is not True
            or account['source'] != 'https://ollama.com/settings'
            or account['source_type'] != 'refreshed signed-in provider usage UI'):
        raise EvidenceError('account_Pro_provenance_not_established')
    if account['auto_reload_enabled'] is not False:
        raise EvidenceError('auto_reload_off_not_established')
    if account['additional_balance_zero'] is not True or money(account['additional_balance_usd']) != 0:
        raise EvidenceError('zero_additional_credit_balance_not_established')
    try:
        observed = dt.datetime.fromisoformat(account['observed_at'].replace('Z', '+00:00'))
        if observed.tzinfo is None:
            raise ValueError('Timezone required')
        current = dt.datetime.now(dt.timezone.utc) if now is None else now
        age = (current-observed).total_seconds()
    except (ValueError, TypeError, AttributeError):
        raise EvidenceError('account_evidence_timestamp_invalid') from None
    if not -schema['future_clock_tolerance_seconds'] <= age <= schema['maximum_age_seconds']:
        raise EvidenceError('account_evidence_not_fresh')
    observation = {name: account[name] for name in schema['observation_fields']}
    if digest(observation) != account['evidence_sha256']:
        raise EvidenceError('account_observation_hash_mismatch')
    if account['pricing'] != pricing:
        raise EvidenceError('authoritative_pricing_drift')
    if money(account['included_balance_lower_bound_usd']) > money(account['monthly_included_credits_usd']):
        raise EvidenceError('included_allowance_bound_invalid')
    forecast = allowance(account, pricing, 131072)
    if forecast['campaign_and_probe_fit'] is not True:
        raise EvidenceError('included_campaign_allowance_insufficient')
    return AccountEvidence(schema['version'], digest(account), account['evidence_sha256'],
                           account['source'], account['observed_at'], age, 'Pro', forecast, True, False)


def validate_api(binding, current_identity, authentication, admission, admission_hash):
    assert_identity(binding.identity, current_identity)
    probe = admission['probe_receipt']
    counted = usage(probe)
    if (admission['decision']['state'] != 'ADMITTED' or admission['identity'] != binding.identity
            or admission['probe_http_status'] != 200 or admission['physical']['probe_count'] != 1
            or admission['physical']['probe']['state'] != 'COMPLETED'
            or probe['failures'] != [] or probe['done'] is not True or probe['done_reason'] != 'stop'
            or probe['identity'] != binding.identity['api_identifier']
            or probe['content_present'] is not True or probe['thinking_present'] is not True
            or probe['operational_only'] is not True or probe['proposal_requests'] != 0
            or probe['proposal_tokens'] != 0 or counted['provider_accounted_tokens'] != 127
            or authentication.get('accepted_authenticated_metadata_request') is not True
            or authentication.get('http_status') != 200):
        raise EvidenceError('prior_probe_or_current_API_contract_not_established')
    return ApiEvidence('api-evidence-1', current_identity, authentication,
                       {'admission_hash': admission_hash, 'response_hash': probe['response_hash'],
                        'provider_usage': counted, 'operational_only': True, 'reused_not_repeated': True,
                        'proves': 'prior authentication, model access, thinking/output/usage compatibility',
                        'does_not_prove': 'current subscription, current allowance, or research performance'})
