from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from pybpmn_server.common.configuration import MongoDBSettings, Settings


@pytest.fixture
def fixtures_path() -> Path:
    """Returns the path to the `fixtures` directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def db_config() -> MongoDBSettings:
    """Returns a MongoDBSettings instance with default values."""
    return MongoDBSettings(db_url="mongodb://localhost:27017", enable_profiler=False, db="test_db")


@pytest_asyncio.fixture
async def settings(db_config: MongoDBSettings, fixtures_path: Path) -> AsyncGenerator[Settings, None]:
    """Returns a MongoDBSettings instance with default values."""
    settings = Settings(
        definitions_path=fixtures_path / "definitions",
        templates_path=fixtures_path / "templates",
        database_settings=db_config,
    )
    datastore = settings.data_store
    _ = datastore.db.client["test_db"]

    yield settings

    await datastore.db.client.drop_database("test_db")


# ============================================
# Token Factory Fixtures
# ============================================


@pytest.fixture
def mock_execution(mocker):
    """Create a mocked execution with required attributes for tokens."""
    from pybpmn_server.engine.interfaces import IExecution

    execution = mocker.MagicMock(spec=IExecution)
    execution.tokens = {}
    execution.log = mocker.MagicMock()
    execution.log_s = mocker.MagicMock()
    execution.log_e = mocker.MagicMock()
    return execution


@pytest.fixture
def mock_start_node(mocker):
    """Create a mocked start node for token initialization."""
    from pybpmn_server.elements.interfaces import INode

    node = mocker.MagicMock(spec=INode)
    node.id = "start_event_1"
    node.type = "bpmn:StartEvent"
    return node


@pytest.fixture
def mock_current_node(mocker):
    """Create a mocked current node for token execution."""
    from pybpmn_server.elements.interfaces import INode

    node = mocker.MagicMock(spec=INode)
    node.id = "service_task_1"
    node.type = "bpmn:ServiceTask"
    return node


@pytest.fixture
def running_token(mock_execution, mock_current_node):
    """A running primary token for basic tests."""
    from pybpmn_server.interfaces.enums import TokenStatus, TokenType
    from tests.factories import TokenFactory

    return TokenFactory.build(
        execution=mock_execution,
        current_node=mock_current_node,
        type=TokenType.Primary,
        status=TokenStatus.running,
    )


@pytest.fixture
def waiting_token(mock_execution, mock_current_node):
    """A waiting primary token at a user task."""
    from pybpmn_server.interfaces.enums import ItemStatus, TokenStatus, TokenType
    from tests.factories import ItemFactory, TokenFactory

    return TokenFactory.build(
        execution=mock_execution,
        current_node=mock_current_node,
        type=TokenType.Primary,
        status=TokenStatus.wait,
        path=[
            ItemFactory.build(element_id="start_1", element_type="bpmn:StartEvent"),
            ItemFactory.build(element_id="user_task_1", element_type="bpmn:UserTask", status=ItemStatus.wait),
        ],
    )


@pytest.fixture
def completed_token(mock_execution, mock_current_node):
    """A completed token with a full execution path."""
    from pybpmn_server.interfaces.enums import ItemStatus, TokenStatus, TokenType
    from tests.factories import ItemFactory, TokenFactory

    end_node = mock_current_node
    end_node.id = "end_event_1"
    end_node.type = "bpmn:EndEvent"

    return TokenFactory.build(
        execution=mock_execution,
        current_node=end_node,
        type=TokenType.Primary,
        status=TokenStatus.end,
        path=[
            ItemFactory.build(element_id="start_1", element_type="bpmn:StartEvent", status=ItemStatus.end),
            ItemFactory.build(element_id="task_1", element_type="bpmn:ServiceTask", status=ItemStatus.end),
            ItemFactory.build(element_id="end_1", element_type="bpmn:EndEvent", status=ItemStatus.end),
        ],
    )


@pytest.fixture
def subprocess_token(mock_execution, mock_start_node, mocker):
    """A subprocess token with a child instance token."""
    from pybpmn_server.interfaces.enums import TokenStatus, TokenType
    from tests.factories import TokenFactory

    # Parent subprocess token
    parent = TokenFactory.build(
        execution=mock_execution,
        current_node=mock_start_node,
        type=TokenType.SubProcess,
        status=TokenStatus.wait,
    )

    # Child instance token
    child_node = mocker.MagicMock()
    child_node.id = "call_activity_1"
    child_node.type = "bpmn:CallActivity"

    child = TokenFactory.build(
        execution=mock_execution,
        current_node=child_node,
        type=TokenType.Instance,
        status=TokenStatus.running,
        parent_token_id=parent.id,
    )

    # Add child to execution tokens
    mock_execution.tokens[child.id] = child

    return parent


@pytest.fixture
def parent_with_children(mock_execution, mock_start_node, mocker):
    """A parent token with multiple child tokens for parallel execution."""
    from pybpmn_server.interfaces.enums import TokenStatus, TokenType
    from tests.factories import TokenFactory

    # Parent diverging token
    parent = TokenFactory.build(
        execution=mock_execution,
        current_node=mock_start_node,
        type=TokenType.Diverge,
        status=TokenStatus.wait,
    )

    # Create multiple child tokens
    child_nodes = []
    for i in range(3):
        child_node = mocker.MagicMock()
        child_node.id = f"parallel_task_{i}"
        child_node.type = "bpmn:ServiceTask"
        child_nodes.append(child_node)

        child = TokenFactory.build(
            execution=mock_execution,
            current_node=child_node,
            type=TokenType.Primary,
            status=TokenStatus.running,
            parent_token_id=parent.id,
        )
        mock_execution.tokens[child.id] = child

    return parent
