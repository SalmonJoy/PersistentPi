"""Independent operational readiness and comparative evidence, never search promotion."""
from collections import Counter

from .classifier import diversity
from .config import FAMILIES, budget
from .statistics import paired_bootstrap, exact_permutation, holm


def interface_ready(rows, invariant_pass, complete_campaign, breach=False):
    counts = Counter(r['family'] for r in rows if r['acquired_valid_proposal'])
    leakage_count = sum(bool(r.get('leakage')) for r in rows)
    checks = {'minimum_valid': sum(r['acquired_valid_proposal'] for r in rows) >= 20,
              'every_family': all(counts[f] >= 1 for f in FAMILIES),
              'invariants': invariant_pass is True, 'no_breach': breach is False,
              'no_systematic_leakage': leakage_count < 2}
    return {'classification': 'INTERFACE_READY' if complete_campaign and all(checks.values()) else
            'INTERFACE_NOT_READY' if complete_campaign else 'NOT_CLASSIFIED_INCOMPLETE',
            'checks': checks, 'valid_by_family': dict(counts), 'leakage_responses': leakage_count}


def improvement(additional_valid, interval, complete_campaign):
    checks = {'additional_valid': additional_valid >= 6, 'interval_lower_positive': interval[0] > 0}
    return {'classification': 'INTERFACE_MEDIATED_IMPROVEMENT' if complete_campaign and all(checks.values())
            else 'NOT_ESTABLISHED' if complete_campaign else 'NOT_CLASSIFIED_INCOMPLETE', 'checks': checks}


def analyze(rows, scenarios, arms, registry, invariants=True, breach=False, terminal_complete=True):
    budget(arms)
    by_id = {s['id']: s for s in scenarios}
    if len(by_id) != 24:
        raise ValueError('M010_ANALYSIS_COHORT')
    seen = set()
    for r in rows:
        key = (r['scenario_id'], r['arm'])
        if key in seen or r['scenario_id'] not in by_id or r['arm'] not in arms:
            raise ValueError('M010_ANALYSIS_IDENTITY')
        s = by_id[r['scenario_id']]
        if (r['family'], r['instance'], r['parent_id']) != (s['family'], s['instance'], s['parent_id']):
            raise ValueError('M010_ANALYSIS_PAIRING')
        seen.add(key)
    complete_campaign = terminal_complete and len(seen) == 24 * len(arms) and all(r.get('state', 'COMPLETE') == 'COMPLETE' for r in rows)
    annotated = diversity(rows, registry)
    result = {'study': 'M0.10A/1', 'complete': complete_campaign, 'arms': {}, 'comparisons': {},
              'automatic_search': False, 'runner_calls': 0, 'rows': annotated}
    for arm in arms:
        group = [r for r in annotated if r['arm'] == arm]
        valid = sum(r['acquired_valid_proposal'] for r in group)
        account = [r.get('account', {}) for r in group]
        from decimal import Decimal
        cost = sum(Decimal(x.get('calculated_charge_usd', '0')) for x in account)
        stage_counts = {key: sum(r['stages'][key] is True for r in group) for key in group[0]['stages']} if group else {}
        field_counts = Counter(f for r in group for f in r.get('mutation_fields', []))
        result['arms'][arm] = {'observed': len(group), 'valid': valid, 'invalid': len(group) - valid,
            'unobserved': 24 - len(group), 'valid_acquisition_rate': valid / 24 if complete_campaign else None,
            'bounds': [valid / 24, (valid + 24 - len(group)) / 24], 'stage_counts': stage_counts,
            'denominators': {'scenario': 24, 'observed': len(group), 'valid': valid},
            'nonempty_completion': sum(r.get('nonempty_content', False) for r in group),
            'truncation_count': sum(r['truncated'] for r in group),
            'provider_accounted_tokens': sum(x.get('provider_accounted_tokens', 0) for x in account),
            'prompt_eval_count': sum(x.get('prompt_eval_count', 0) for x in account),
            'prompt_eval_cached_count': sum(x.get('prompt_eval_cached_count', 0) for x in account),
            'eval_count': sum(x.get('eval_count', 0) for x in account), 'calculated_charge_usd': str(cost),
            'cost_per_valid_usd': str(cost / valid) if valid else None,
            'thinking_bytes': sum(r.get('thinking_bytes') or 0 for r in group),
            'final_bytes': sum(r.get('final_bytes') or 0 for r in group),
            'tool_argument_bytes': sum(r.get('tool_argument_bytes') or 0 for r in group),
            'latency_seconds': [r.get('latency_seconds') for r in group],
            'unique_scaffolds': len({r['scaffold_id'] for r in group if r['acquired_valid_proposal']}),
            'parent_duplicates': sum(r.get('diversity', {}).get('parent_duplicate', False) for r in group),
            'reference_duplicates': sum(r.get('diversity', {}).get('reference_duplicate', False) for r in group),
            'cross_response_duplicates': sum(r.get('diversity', {}).get('cross_response_duplicate', False) for r in group),
            'mutation_field_frequencies': dict(sorted(field_counts.items())),
            'mutated_field_counts': [len(r.get('mutation_fields', [])) for r in group],
            'readiness': interface_ready(group, invariants, complete_campaign, breach)}
        summaries = {}
        for name, stage in (('completion', 'complete_submission'), ('representation_parse', 'transport_parse'),
                            ('schema', 'interface_structure'), ('semantic_vocabulary', 'semantic_vocabulary'),
                            ('scaffold_spec', 'spec_validation'), ('compiler_acceptance', 'compiler')):
            assessed = [r['stages'][stage] for r in group if r['stages'][stage] is not None]
            summaries[name] = {'pass': assessed.count(True), 'assessed': len(assessed),
                               'unassessed': len(group) - len(assessed),
                               'rate': assessed.count(True) / len(assessed) if assessed else None}
        failure_reasons = Counter((r['first_failure'] or {}).get('reason', '') for r in group)
        summaries['category_failures'] = sum(n for reason, n in failure_reasons.items() if 'CATEGOR' in reason)
        summaries['field_type_failures'] = sum(n for reason, n in failure_reasons.items()
            if reason.startswith(('MUTATION_VALUE_', 'MUTATION_CATEGORIES_TYPE', 'SPEC_TEXT', 'SPEC_CALL_ALLOCATION', 'SPEC_OUTPUT_ALLOCATION')))
        summaries['illegal_setting_failures'] = sum(n for reason, n in failure_reasons.items()
            if reason.startswith(('SPEC_', 'MUTATION_FIELD', 'MUTATION_VALUE_')))
        summaries['failure_reasons'] = dict(sorted(failure_reasons.items()))
        for name in ('category_valid', 'field_types_valid', 'illegal_setting'):
            assessments = [r.get('diagnostics', {}).get(name) for r in group
                           if r.get('diagnostics', {}).get(name) is not None]
            summaries[name] = {'true': assessments.count(True), 'assessed': len(assessments),
                               'rate': assessments.count(True) / len(assessments) if assessments else None,
                               'unassessed': len(group) - len(assessments)}
        summaries['truncation_rate'] = sum(r['truncated'] for r in group) / len(group) if group else None
        summaries['duplicate_rate'] = sum(r.get('diversity', {}).get('cross_response_duplicate', False)
                                         for r in group) / valid if valid else None
        result['arms'][arm]['secondary'] = summaries
    if complete_campaign:
        lookup = {(r['scenario_id'], r['arm']): r for r in annotated}
        pvalues = {}
        for arm in arms[1:]:
            differences = {f: [] for f in FAMILIES}
            discordant = [0, 0]
            for s in sorted(scenarios, key=lambda x: (x['family'], x['instance'])):
                a = int(lookup[s['id'], arm]['acquired_valid_proposal'])
                b = int(lookup[s['id'], 'F0']['acquired_valid_proposal'])
                differences[s['family']].append(a - b)
                discordant[0] += a == 1 and b == 0
                discordant[1] += a == 0 and b == 1
            bootstrap, permutation = paired_bootstrap(differences), exact_permutation(differences)
            interval = bootstrap['ci975' if len(arms) == 3 else 'ci95']
            additional = result['arms'][arm]['valid'] - result['arms']['F0']['valid']
            name = arm + '_vs_F0'
            pvalues[name] = permutation['p_value']
            result['comparisons'][name] = {'additional_valid': additional, 'bootstrap': bootstrap,
                'permutation': permutation, 'discordant_interface_only': discordant[0],
                'discordant_F0_only': discordant[1], 'progression_interval': interval,
                'improvement': improvement(additional, interval, True)}
        adjusted = holm(pvalues) if len(arms) == 3 else pvalues
        for name, value in adjusted.items():
            result['comparisons'][name]['adjusted_p_value'] = value
        if len(arms) == 3:
            result['F2_vs_F1_descriptive'] = {'effect': (result['arms']['F2']['valid'] - result['arms']['F1']['valid']) / 24,
                                             'inferential': False}
    return result
