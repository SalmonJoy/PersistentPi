"""Deterministic acquisition labels with physical parser failures preserved."""
from copy import deepcopy

from ..contracts import canonical
from ..interfaces import decode_json
from .completion import complete
from .config import DEFAULT
from .f0 import parse_f0
from .f2 import arguments
from .frozen import ScaffoldSpecV1, compile_scaffold, parent_spec
from .mutation import structure, vocabulary, expand
from .security import leakage
from .diagnostics import assess

STAGES = ('provider_response', 'complete_submission', 'transport_parse', 'interface_structure',
          'semantic_vocabulary', 'parent', 'construction', 'spec_validation', 'compiler', 'diversity')


def classify(response, arm, allowed_registry, completion_evidence=None):
    out = {'arm': arm, 'stages': {k: None for k in STAGES}, 'acquired_valid_proposal': False,
           'first_failure': None, 'physical_parser_failure': None, 'scaffold_id': None,
           'normalized_spec': None, 'leakage': [], 'payload_pattern_violation': False,
           'mutation_fields': [], 'done_reason': response.get('done_reason') if isinstance(response, dict) else None,
           'truncated': False}
    stage = 1
    value = None
    try:
        if (not isinstance(response, dict) or response.get('model') != 'gpt-oss:120b'
                or not isinstance(response.get('message'), dict)):
            raise ValueError('M010_PROVIDER_IDENTITY')
        out['stages'][STAGES[0]] = True
        stage = 2
        complete(response, completion_evidence)
        message = response['message']
        if arm == 'F2':
            value = arguments(response)
        elif arm in ('F0', 'F1'):
            text = message.get('content')
            if not isinstance(text, str) or not text:
                raise ValueError('M010_EMPTY_FINAL')
            value = None
        else:
            raise ValueError('M010_ARM')
        out['stages'][STAGES[1]] = True
        stage = 3
        if arm != 'F2':
            if len(text.encode()) > 65536:
                raise ValueError('M010_SUBMISSION_BYTES')
            value = decode_json(text)
        elif len(canonical(value)) > 65536:
            raise ValueError('M010_SUBMISSION_BYTES')
        out['leakage'] = leakage(value)
        out['stages'][STAGES[2]] = True
        if arm == 'F0':
            try:
                envelope = parse_f0(text, allowed_registry)
            except (ValueError, TypeError, KeyError, RecursionError) as exc:
                reason = str(exc)
                out['physical_parser_failure'] = reason if reason.startswith(('PROPOSAL_', 'SPEC_')) else 'MALFORMED'
                stage = (6 if reason == 'PROPOSAL_PARENT' else 5 if reason == 'PROPOSAL_CATEGORY'
                         else 8 if reason.startswith('SPEC_') else 4)
                raise
            for name in STAGES[3:9]:
                out['stages'][name] = True
            stage = 9
            compiled = compile_scaffold(envelope.scaffold)
            base = parent_spec(allowed_registry, envelope.parents[0])
            out['mutation_fields'] = sorted(k for k, v in compiled.spec.to_dict().items() if base[k] != v)
        else:
            stage = 4
            structure(value)
            out['stages'][STAGES[3]] = True
            stage = 5
            vocabulary(value)
            out['stages'][STAGES[4]] = True
            stage = 6
            parent_spec(allowed_registry, value['parent_id'])
            out['stages'][STAGES[5]] = True
            stage = 7
            expanded = expand(value, allowed_registry)
            out['stages'][STAGES[6]] = True
            stage = 8
            spec = ScaffoldSpecV1.from_dict(expanded)
            out['stages'][STAGES[7]] = True
            stage = 9
            compiled = compile_scaffold(spec)
            out['stages'][STAGES[8]] = True
            out['mutation_fields'] = sorted(op['field'] for op in value['mutations'])
        out.update(acquired_valid_proposal=True, scaffold_id=compiled.scaffold_id,
                   normalized_spec=compiled.spec.to_dict())
    except (ValueError, TypeError, KeyError, RecursionError) as exc:
        reason = str(exc)
        if arm == 'F0' and stage == 3 and out['physical_parser_failure'] is None:
            out['physical_parser_failure'] = 'MALFORMED'
        out['stages'][STAGES[stage - 1]] = False
        out['first_failure'] = {'stage': stage, 'reason': reason}
        out['truncated'] = reason == 'M010_TRUNCATED'
        out['payload_pattern_violation'] = reason == 'SPEC_BENCHMARK_PAYLOAD'
    message = response.get('message', {}) if isinstance(response, dict) else {}
    final = message.get('content', '')
    thinking = message.get('thinking', '')
    out['nonempty_content'] = (isinstance(final, str) and bool(final)) or (
        arm == 'F2' and isinstance(message.get('tool_calls'), list) and bool(message['tool_calls']))
    out['thinking_bytes'] = len(thinking.encode()) if isinstance(thinking, str) else None
    out['final_bytes'] = len(final.encode()) if isinstance(final, str) else None
    out['diagnostics'] = assess(value, arm)
    out['diagnostics']['illegal_setting'] = ((out['first_failure'] or {}).get('reason', '').startswith(
        ('SPEC_', 'MUTATION_FIELD', 'MUTATION_VALUE_'))) if value is not None else None
    try:
        out['tool_argument_bytes'] = len(canonical(arguments(response))) if arm == 'F2' else 0
    except (ValueError, TypeError, AttributeError):
        out['tool_argument_bytes'] = None
    return out


def diversity(rows, registry):
    results = deepcopy(rows)
    counts = {}
    for row in rows:
        if row['acquired_valid_proposal']:
            counts[row['scaffold_id']] = counts.get(row['scaffold_id'], 0) + 1
    for row in results:
        if not row['acquired_valid_proposal']:
            continue
        sid = row['scaffold_id']
        row['diversity'] = {'parent_duplicate': sid == row['parent_id'],
            'reference_duplicate': sid in registry, 'cross_response_duplicate': counts[sid] > 1,
            'occurrences': counts[sid]}
        row['stages']['diversity'] = True
    return results
