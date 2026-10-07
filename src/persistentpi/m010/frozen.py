"""Explicit references to unchanged historical data contracts, never execution."""
import hashlib
from copy import deepcopy

from ..contracts import digest
from ..m09.spec import ScaffoldSpecV1, compile_scaffold, references
from .config import ROOT

ANCHORS = {
    'src/persistentpi/m09/spec.py': 'f12c7fb774a0a4dbf4ae753c94907f00f2eb30654bb488df751bda694233dd7d',
    'src/persistentpi/m09/manager.py': 'd70d5a328c00339acca1cb9d64aef5dee700262437a3c606e944e21e138fb434',
    'src/persistentpi/m09/disclosure.py': 'd5cc1787715281f79a6d2b790723ebd506d67f0562135e518a658f3c37e88a70',
    'src/persistentpi/interfaces.py': '0e886cb4599b4aab4637a222bc34516430c921c440704b65407a632423f672ed',
}


def verify_anchors():
    observed = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in ANCHORS}
    if observed != ANCHORS:
        raise ValueError('M010_HISTORICAL_CONTRACT_DRIFT')
    return observed


def parent_registry():
    verify_anchors()
    result = {}
    for name, spec in references().items():
        compiled = compile_scaffold(spec)
        normalized = compiled.spec.to_dict()
        result[compiled.scaffold_id] = {'name': name, 'id': compiled.scaffold_id,
            'spec': normalized, 'spec_hash': digest(normalized), 'catalog_hash': compiled.catalog_hash,
            'compiler': compiled.compiler, 'renderer': compiled.renderer, 'protocol': compiled.protocol}
    return result


def parent_spec(registry, parent_id):
    if parent_id not in registry:
        raise ValueError('MUTATION_PARENT')
    row = registry[parent_id]
    value = deepcopy(row['spec'])
    compiled = compile_scaffold(ScaffoldSpecV1.from_dict(value))
    if row['id'] != parent_id or compiled.scaffold_id != parent_id or digest(value) != row['spec_hash']:
        raise ValueError('MUTATION_PARENT_INTEGRITY')
    if value != compiled.spec.to_dict():
        raise ValueError('MUTATION_PARENT_NOT_NORMALIZED')
    for key in ('catalog_hash', 'compiler', 'renderer', 'protocol'):
        if row.get(key) != getattr(compiled, key):
            raise ValueError('MUTATION_PARENT_PROVENANCE')
    return value
