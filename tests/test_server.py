"""Tests for pybpmn_server.server."""
import asyncio
from unittest.mock import MagicMock

import pytest

from pybpmn_server.api.api import BPMNAPI
from pybpmn_server.api.secure_user import SecureUser
from pybpmn_server.common.configuration import Settings
from pybpmn_server.server.bpmn_server import BPMNServer


@pytest.mark.asyncio
async def test_server_initialization():
    config = Settings()
    # config.cache_manager = MagicMock(return_value=MagicMock())
    # config.data_store = MagicMock(return_value=MagicMock())
    # config.definitions = MagicMock(return_value=MagicMock())
    # config.app_delegate = MagicMock(return_value=MagicMock())
    # config.script_handler = MagicMock(return_value=MagicMock())
    # config.datastore =
    # config.timers = {}

    server = BPMNServer(config)

    assert server is not None
    assert server.engine is not None
    assert server.cron is not None


@pytest.mark.asyncio
async def test_api_engine_start():
    server = MagicMock()
    server.engine = MagicMock()
    server.engine.start = MagicMock(side_effect=lambda *args, **kwargs: asyncio.ensure_future(asyncio.sleep(0)))

    api = BPMNAPI(server)
    api.default_user = SecureUser(user_name="test_user", user_groups=[])

    await api.engine.start("TestModel", data={"foo": "bar"})

    server.engine.start.assert_called_once()
    args, _ = server.engine.start.call_args
    assert args[0] == "TestModel"
    assert args[1] == {"foo": "bar"}
    assert args[3] == "test_user"


@pytest.mark.asyncio
async def test_secure_user_qualify_instances():
    user = SecureUser(user_name="bob", user_groups=["group1"], tenant_id="tenant1")

    query = {"status": "active"}
    qualified = user.qualify_instances(query)

    assert qualified["tenantId"] == "tenant1"
    assert "$or" in qualified
    or_clause = qualified["$or"]
    assert {"items.assignee": "bob"} in or_clause
    assert {"items.candidateGroups": "group1"} in or_clause
