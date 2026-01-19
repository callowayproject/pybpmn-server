"""Shared helpers for PolyFactory factories."""

from datetime import datetime, timezone
from typing import Any


def generate_ulid() -> str:
    """Generate a ULID-formatted ID for tokens and items."""
    from ulid import ULID

    return str(ULID())


def now_utc() -> datetime:
    """Get the current datetime in UTC."""
    return datetime.now(timezone.utc)


def sequence_int(n: int) -> int:
    """Helper for predictable integer sequences."""
    return n
