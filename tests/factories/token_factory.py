"""Token factory for generating realistic test tokens."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from pybpmn_server.datastore.data_objects import ItemData
from pybpmn_server.engine.token import Token
from pybpmn_server.interfaces.enums import ItemStatus, TokenStatus, TokenType

if TYPE_CHECKING:
    from pybpmn_server.elements.interfaces import INode
    from pybpmn_server.engine.interfaces import IExecution, IItem


from tests.factories.helpers import generate_ulid
from tests.factories.item_data_factory import ItemFactory


class TokenFactory:
    """Factory for creating Token objects for testing."""

    @classmethod
    def build(
        cls,
        execution: IExecution,
        current_node: INode,
        start_node: Optional[INode] = None,
        path: Optional[List[IItem]] = None,
        parent_token: Optional[Token] = None,
        origin_item: Optional[IItem] = None,
        **kwargs: Any,
    ) -> Token:
        """
        Build a Token instance with the required dependencies.

        Args:
            execution: The execution context for the token.
            current_node: The current node the token is at.
            start_node: The node where token started (defaults to current_node).
            path: List of items in the token's path.
            parent_token: Parent token.
            origin_item: Origin item.
            **kwargs: Additional factory overrides.

        Returns:
            A fully initialized Token instance.
        """
        start_node = start_node or current_node
        path = path or []

        # Extract fields that TokenFactory handles
        token_id = kwargs.pop("id", generate_ulid())
        token_type = kwargs.pop("type", TokenType.Primary)
        status = kwargs.pop("status", TokenStatus.running)
        data_path = kwargs.pop("data_path", None)
        items_key = kwargs.pop("items_key", None)
        # Other kwargs can be ignored or handled if needed

        # Manually construct Token since it requires positional args
        token = Token(
            type_=token_type,
            execution=execution,
            start_node=start_node,
            data_path=data_path,
            parent_token=parent_token,
            origin_item=origin_item,
        )

        # Set additional attributes
        token.id = token_id
        token.status = status
        token.items_key = items_key
        token._current_node = current_node

        # Add path items if provided
        for item in path:
            token.path.append(item)

        return token

    @classmethod
    async def async_build(
        cls,
        execution: IExecution,
        current_node: INode,
        start_node: Optional[INode] = None,
        path: Optional[List[IItem]] = None,
        parent_token: Optional[Token] = None,
        origin_item: Optional[IItem] = None,
        **kwargs: Any,
    ) -> Token:
        """Async version of build for async test contexts."""
        return cls.build(
            execution=execution,
            current_node=current_node,
            start_node=start_node,
            path=path,
            parent_token=parent_token,
            origin_item=origin_item,
            **kwargs,
        )
