"""Frozen study rules, independent of historical search budgets."""
from copy import deepcopy
from pathlib import Path
import json

from ..contracts import digest

ROOT = Path(__file__).resolve().parents[3]
ARMS = ('F0', 'F1', 'F2')
FAMILIES = ('no_op_repetition', 'formation_failure', 'excessive_read', 'context_mismatch',
            'syntax_rejection', 'output_truncation', 'high_cost', 'mixed_failures')
BUCKETS = ('coupled_conditions', 'boundary_empty', 'initialization_accumulation',
           'early_returns', 'state_machine', 'parsing', 'two_functions', 'duplicates_order')
CATEGORIES = ('NO_OP', 'PATCH_MISMATCH', 'INVALID_SYNTAX', 'MALFORMED', 'UNAUTHORIZED',
              'OUTPUT_LIMIT', 'BUDGET', 'GIVE_UP', 'PUBLIC_FAIL', 'PUBLIC_PASS', 'OTHER')
COMMON_SYSTEM = ('You optimize a frozen small coding Runner using protocol metrics only. '
    'Choose a legal scaffold mutation using the supplied parent and contract. Select semantic changes yourself. '
    'The trusted compiler copies the parent and replaces exactly the declared fields; it does not choose '
    'settings or repair proposals. Propose general scaffold changes, never task answers, lookup tables, '
    'executable programs, protected-component changes, or resource-ceiling changes. '
    'Unlisted keys and field aliases are forbidden.')
SUFFIX = {'F1': 'Return exactly one JSON MutationProposal in final content. No fences or surrounding prose.',
          'F2': 'Submit exactly one submit_scaffold_mutation tool call with MutationProposal arguments. '
                'Do not invoke another tool or request a second turn.'}
DEFAULT = {
    'study': 'M0.10A/1', 'milestone': 'M0.10A-I', 'historical_protocol': '0.6',
    'planner': {'alias': 'gpt-oss:120b-cloud', 'api_identifier': 'gpt-oss:120b',
                'endpoint': 'https://ollama.com/api/chat', 'temperature': 0, 'think': 'high',
                'num_predict': 4096, 'seed': None, 'seed_support': 'not_established', 'stream': False},
    'limits': {'request_bytes': 16384, 'response_bytes': 65536, 'submission_bytes': 65536,
               'timeout_seconds': 180, 'input_context_tokens': 131072,
               'generation_tokens': 4096, 'included_credit_usd': '2.00',
               'feasibility_wall_seconds': 10800, 'admission_wall_seconds': 600,
               'additional_purchased_credit_usd': '0.00'},
    'budgets': {'two_arm': {'arms': ['F0', 'F1'], 'requests': 48, 'provider_tokens': 6488064},
                'three_arm': {'arms': ['F0', 'F1', 'F2'], 'requests': 72, 'provider_tokens': 9732096},
                'probe': {'requests': 1, 'provider_tokens': 135168}},
    'analysis': {'bootstrap_resamples': 100000, 'bootstrap_seed': 20261010,
                  'quantile': 'nearest-rank', 'ordinary_confidence': 0.95,
                  'three_arm_progression_confidence': 0.975, 'permutations': 256,
                  'permutation_statistic': 'mean over all 24 paired scenario differences',
                  'permutation_tail': 'count(abs(T_perm)>=abs(T_obs))/256',
                  'monte_carlo_correction': False, 'multiplicity': 'Holm F1/F0 and F2/F0 only'},
    'readiness': {'valid_minimum': 20, 'family_minimum': 1, 'families': 8,
                  'systematic_leakage_minimum': 2, 'requires_comparison': False},
    'improvement': {'additional_valid_minimum': 6, 'interval_lower_exclusive': 0},
    'schedule': {'seed': 42, 'unit': 'scenario temporal block', 'concurrency': 'admitted arm count'},
    'f2_decision': 'before feasibility outcomes; offline infeasibility excludes F2 before probe',
    'completion': {'stop': {'meaning': 'complete', 'source': 'https://docs.ollama.com/api/chat'},
                   'length': {'meaning': 'truncated', 'source': 'historical admitted provider contract'}},
    'funding': {'plan': 'Pro', 'included_only': True, 'automatic_reload': False,
                'top_up': False, 'upgrade': False, 'fallback': False},
    'prohibited_fields': ['code', 'script', 'command', 'exec', 'eval', 'task_id', 'task_lookup',
                           'reference_solution', 'hidden_tests', 'evaluator', 'logger', 'supervisor',
                           'resource_limits', 'model'],
    'capabilities': {'runner': False, 'benchmarks': False, 'hidden_scoring': False,
                     'automatic_search': False, 'feasibility_inference_authorized': False},
}


def configuration():
    return deepcopy(DEFAULT)


def load_configuration(path):
    result = json.loads(Path(path).read_bytes())
    if result != DEFAULT:
        raise ValueError('M010_CONFIGURATION_DRIFT')
    return result


def budget(arms):
    arms = tuple(arms)
    key = 'two_arm' if arms == ('F0', 'F1') else 'three_arm' if arms == ARMS else None
    if key is None:
        raise ValueError('M010_ARM_LIST')
    return deepcopy(DEFAULT['budgets'][key])


def configuration_hash():
    return digest(DEFAULT)
