"""Tests for the Token class in the engine module."""
from pathlib import Path

import pytest

from pybpmn_server.elements.interfaces import INode
from pybpmn_server.elements.node import Node
from pybpmn_server.engine.execution import Execution
from pybpmn_server.engine.item import Item
from pybpmn_server.engine.token import Token
from pybpmn_server.interfaces.enums import TokenStatus, TokenType

fixture_dir = Path(__file__).parent.parent / "fixtures"


class TestToken:
    """Tests for the Token class in the engine module."""

    def test_append_data_updates_instance_data(self, mocker):
        """
        Verify that append_data correctly delegates to the execution's append_data method.

        This is critical because tokens are the primary mechanism for moving data through a process.
        """
        mock_execution = mocker.MagicMock(spec=Execution)
        mock_node = mocker.MagicMock(spec=Node)
        mock_node.id = "start_node_1"
        mock_node.process_id = "process_1"

        token = Token(TokenType.Primary, mock_execution, mock_node)
        mock_item = mocker.MagicMock()
        input_data = {"key": "value"}

        token.append_data(input_data, mock_item)

        # Ensure the execution's append_data is called with correct pathing
        mock_execution.append_data.assert_called_once_with(input_data, mock_item, token.data_path)

    def test_get_full_path_includes_parent_items(self, mocker):
        """
        Verify that get_full_path recursively collects items from parent tokens.

        This ensures that the engine can reconstruct the full history of an execution branch.
        """
        mock_execution = mocker.MagicMock(spec=Execution)
        mock_node = mocker.MagicMock(spec=Node)
        mock_node.id = "node_1"

        # Setup parent token with one item
        parent_token = Token(TokenType.Primary, mock_execution, mock_node)
        parent_item = mocker.MagicMock()
        parent_token.path = [parent_item]

        # Setup child token with one item
        child_token = Token(TokenType.SubProcess, mock_execution, mock_node, parent_token=parent_token)
        child_item = mocker.MagicMock()
        child_token.path = [child_item]

        full_path = child_token.get_full_path()

        # Expected: [parent_item, child_item]
        assert len(full_path) == 2
        assert full_path[0] == parent_item
        assert full_path[1] == child_item

    @pytest.mark.asyncio
    async def test_terminate_stops_token_and_children(self, mocker):
        """
        Ensure that terminating a token sets its status to terminated and affects children.

        Proper termination prevents 'zombie' tokens from continuing execution after a process cancels.
        """
        mock_execution = mocker.MagicMock(spec=Execution)
        mock_node = mocker.MagicMock(spec=Node)
        mock_node.id = "node_1"

        token = Token(TokenType.Primary, mock_execution, mock_node)

        # Mock children_tokens property logic
        child_token = mocker.AsyncMock()
        mocker.patch.object(Token, "get_children_tokens", new_callable=mocker.MagicMock, return_value=[child_token])

        await token.terminate()

        from pybpmn_server.interfaces.enums import TokenStatus

        assert token.status == TokenStatus.terminated
        child_token.terminate.assert_called_once()


class TestStartNewToken:
    """Tests for the `start_new_token` method in the token module."""

    @pytest.mark.asyncio
    async def test_with_no_execute_does_not_execute(self, mocker):
        # Mock objects
        mock_execution = mocker.MagicMock(spec=Execution, tokens={})
        mock_start_node = mocker.MagicMock(spec=Node)
        mock_start_node.id = "start_node_1"
        mock_data = {"key1": "value1"}
        mock_parent_token = mocker.MagicMock(spec=Token, items_key=None)

        mock_origin_item = mocker.MagicMock(spec=Item)
        mock_loop = mocker.MagicMock()

        # Call the method
        result = await Token.start_new_token(
            type_=TokenType.Instance,
            execution=mock_execution,
            start_node=mock_start_node,
            data_path="some.data.path",
            parent_token=mock_parent_token,
            origin_item=mock_origin_item,
            loop=mock_loop,
            data=mock_data,
            no_execute=True,
            items_key="item_key_1",
        )

        # Assertions
        assert result.execution == mock_execution
        assert result.start_node_id == mock_start_node.id
        assert result.parent_token == mock_parent_token
        assert result.origin_item == mock_origin_item
        assert result.loop == mock_loop
        assert result.items_key == "item_key_1"
        mock_execution.append_data.assert_called_once_with(mock_data, mock_origin_item, "some.data.path")

    @pytest.mark.asyncio
    async def test_start_new_token_with_execute(self, mocker):
        # Mock objects
        mock_execution = mocker.MagicMock()
        mock_start_node = mocker.MagicMock()
        mock_start_node.id = "start_node_2"
        mock_data = {"key2": "value2"}
        mock_parent_token = mocker.MagicMock()
        mock_origin_item = mocker.MagicMock()
        mock_loop = mocker.MagicMock()

        with mocker.patch.object(Token, "execute"):
            # Call the method
            result = await Token.start_new_token(
                type_=TokenType.Primary,
                execution=mock_execution,
                start_node=mock_start_node,
                data_path=None,
                parent_token=mock_parent_token,
                origin_item=mock_origin_item,
                loop=mock_loop,
                data=mock_data,
                no_execute=False,
                items_key=None,
            )

            result.execute.assert_awaited_with(mock_data)

        # Assertions
        assert result.execution == mock_execution
        assert result.start_node_id == mock_start_node.id
        assert result.data_path
        assert result.parent_token == mock_parent_token
        assert result.origin_item == mock_origin_item
        assert result.loop == mock_loop
        mock_execution.tokens.__setitem__.assert_called_with(result.id, result)


    @pytest.mark.asyncio
    async def test_inherits_parent_items_key(self, mocker):
        # Mock objects
        mock_execution = mocker.MagicMock()
        mock_start_node = mocker.MagicMock()
        mock_start_node.id = "start_node_3"
        mock_parent_token = mocker.MagicMock()
        mock_parent_token.items_key = "parent_key"
        mock_origin_item = mocker.MagicMock()

        # Call the method
        result = await Token.start_new_token(
            type_=TokenType.SubProcess,
            execution=mock_execution,
            start_node=mock_start_node,
            data_path=None,
            parent_token=mock_parent_token,
            origin_item=mock_origin_item,
            loop=None,
            data=None,
            no_execute=True,
            items_key=None,
        )

        # Assertions
        assert result.items_key == "parent_key"
        mock_execution.tokens.__setitem__.assert_called_with(result.id, result)


    @pytest.mark.asyncio
    async def test_no_parent_items_key(self, mocker):
        # Mock objects
        mock_execution = mocker.MagicMock()
        mock_start_node = mocker.MagicMock()
        mock_start_node.id = "start_node_4"
        mock_parent_token = mocker.MagicMock()
        mock_parent_token.items_key = "parent_key"
        mock_origin_item = mocker.MagicMock()

        # Call the method
        result = await Token.start_new_token(
            type_=TokenType.EventSubProcess,
            execution=mock_execution,
            start_node=mock_start_node,
            data_path=None,
            parent_token=mock_parent_token,
            origin_item=mock_origin_item,
            loop=None,
            data=None,
            no_execute=True,
            items_key="item_child_key",
        )

        # Assertions
        assert result.items_key == "parent_key.item_child_key"
        mock_execution.tokens.__setitem__.assert_called_with(result.id, result)


@pytest.mark.asyncio
async def test_execute_with_end_status(mocker):
    """
    Test that the `execute` method returns None if the token's status is already `end`.
    """
    mock_execution = mocker.MagicMock(spec=Execution)
    mock_node = mocker.MagicMock(spec=INode)
    mock_node.id = "node_1"

    token = Token(TokenType.Primary, mock_execution, mock_node)
    token.status = TokenStatus.end
    token.log_e = mocker.MagicMock()
    result = await token.execute(input_data={"key": "value"})

    assert result is None
    token.log_e.assert_called_with(
        f"Token({token.id}).execute:end token status is end: return from execute!!"
    )
