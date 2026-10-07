"""Public snapshot boundary: private benchmark assets are intentionally absent."""
from persistentpi.private_assets import PrivateAssetUnavailable

def _unavailable(*args, **kwargs):
    raise PrivateAssetUnavailable("Private benchmark payload/constructor is not distributed.")

FAMILIES = ('coupled_conditions', 'boundary_empty', 'initialization_accumulation', 'early_returns', 'state_machine', 'parsing', 'two_functions', 'duplicates_order')
TIERS = ('L1', 'L2', 'L3')

def __getattr__(name):
    if name.startswith("__"):
        raise AttributeError(name)
    return _unavailable
