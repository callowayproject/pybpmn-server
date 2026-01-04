"""Tests for common scenarios."""
import logging
from pathlib import Path

import pytest

from pybpmn_server.common.configuration import Settings
from pybpmn_server.engine.engine import Engine


@pytest.mark.asyncio
async def test_simple_execution(settings: Settings, fixtures_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test that a simple start-token-end workflow executes correctly."""
    caplog.set_level(logging.INFO)
    source = fixtures_path.joinpath("simple.bpmn").read_text(encoding="utf-8")
    engine = Engine(settings)
    execution = await engine.start("simple_test", source)
    print(execution)
    print(caplog.text)
    1/0
