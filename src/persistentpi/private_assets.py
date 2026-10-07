"""Explicit boundary for benchmark assets withheld from the public snapshot."""


class PrivateAssetUnavailable(RuntimeError):
    """A requested private research asset or constructor is not distributed."""
