"""
A module for handling and processing time specs in ISO8601 formats, including durations, cycles, and cron expressions.

This module provides functionalities to calculate the time until due based on
various time specification formats and to extract repeat counts from ISO8601
cycle specifications.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import isodate

logger = logging.getLogger(__name__)


def time_due(spec: str, reference: Optional[datetime] = None) -> float:
    """
    Calculates seconds until due based on spec (Duration, Cycle, or Cron).
    """
    from pybpmn_server.server.cron import Cron

    reference = reference or datetime.now(tz=timezone.utc)

    # ISO8601 Duration (e.g., PT2S, P1D)
    if spec.startswith("P"):
        duration = isodate.parse_duration(spec)
        if isinstance(duration, isodate.Duration):
            # handle isodate.Duration which might have months/years
            due_date = reference + duration
            return (due_date - reference).total_seconds()
        return duration.total_seconds()

    # ISO8601 Cycle (e.g., R3/PT10H)
    if spec.startswith("R"):
        parts = spec.split("/")
        if len(parts) > 1:
            duration_spec = parts[-1]
            return time_due(duration_spec, reference)

    # Cron expression
    try:
        cron_instance = Cron(spec)
        interval = cron_instance(reference)
        next_date = interval.next()
        return (next_date - reference).total_seconds()
    except ValueError as e:
        logger.warning(f"Invalid cron expression: {spec}. {e}")

    return 0.0


def get_repeat(spec: str) -> int:
    """
    Extracts repeat count from ISO8601 cycle spec (e.g., R3/PT10H).

    Returns 999999 for infinite repeats.
    """
    if spec.startswith("R"):
        parts = spec.split("/")
        if len(parts) > 1:
            repeat_str = parts[0][1:]
            if not repeat_str:
                return 999999  # infinite
            return int(repeat_str)
    return 1
