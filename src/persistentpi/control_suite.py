"""Public snapshot boundary: private benchmark assets are intentionally absent."""
from persistentpi.private_assets import PrivateAssetUnavailable

def _unavailable(*args, **kwargs):
    raise PrivateAssetUnavailable("Private benchmark payload/constructor is not distributed.")


def __getattr__(name):
    if name.startswith("__"):
        raise AttributeError(name)
    return _unavailable
