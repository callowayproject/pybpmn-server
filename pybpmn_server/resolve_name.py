"""Resolve a value from a dotted name."""

from typing import Any


def resolve_name(obj: Any, name: str, default: Any = None) -> Any:
    """
    Get a key or attr ``name`` from obj or default value.

    Copied and modified from Django Template variable resolutions
    Resolution methods:
    - Mapping key lookup
    - Attribute lookup
    - Sequence index

    Args:
        obj: The object to access
        name: A dotted name to the value, such as ``mykey.0.name``
        default: If the name cannot be resolved from the object, return this value

    Returns:
        The value at the resolved name or the default value.
    """
    lookups = name.split(".")
    current = obj
    try:  # catch-all for unexpected failures
        for bit in lookups:
            try:  # dictionary lookup
                current = current[bit]
                # ValueError/IndexError are for numpy.array lookup on
                # numpy < 1.9 and 1.9+ respectively
            except (TypeError, AttributeError, KeyError, ValueError, IndexError):
                try:  # attribute lookup
                    current = getattr(current, bit)
                except (TypeError, AttributeError):
                    # Reraise if the exception was raised by a @property
                    if bit in dir(current):
                        raise
                    try:  # list-index lookup
                        current = current[int(bit)]
                    except (
                        IndexError,  # list index out of range
                        ValueError,  # invalid literal for int()
                        KeyError,  # current is a dict without `int(bit)` key
                        TypeError,
                    ):  # un-subscript-able object
                        return default
        return current
    except Exception:  # noqa: BLE001 # pragma: no cover
        return default
