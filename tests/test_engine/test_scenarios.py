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
    await engine.start("simple_test", source)
    print(caplog.text)
    for span in sorted(settings._span_exporter.get_finished_spans(), key=lambda x: x.start_time):
        print(f"{span.name}: {span.attributes}")
    settings._span_exporter.clear()
    assert len(settings._span_exporter.get_finished_spans()) == 99
    1 / 0


@pytest.mark.asyncio
async def test_parallel_gateway_execution(
    settings: Settings, fixtures_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that a simple start-token-end workflow executes correctly."""
    caplog.set_level(logging.INFO)
    source = fixtures_path.joinpath("parallel-gateway.bpmn").read_text(encoding="utf-8")
    engine = Engine(settings)
    await engine.start("parallel gateway", source)
    print(caplog.text)
    for span in sorted(settings._span_exporter.get_finished_spans(), key=lambda x: x.start_time):
        print(f"{span.name}: {span.attributes}")
    settings._span_exporter.clear()
    assert len(settings._span_exporter.get_finished_spans()) == 99
    1 / 0
