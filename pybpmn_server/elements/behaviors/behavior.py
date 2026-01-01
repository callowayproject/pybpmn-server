"""Base class for behavior implementations in BPMN elements."""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from pybpmn_server.elements.interfaces import INode
    from pybpmn_server.engine.interfaces import IItem


class Behavior(ABC):
    """
    Base class for behavior implementations in BPMN elements.
    """

    def __init__(self, node: INode, definition: Any):
        self.node = node
        self.definition = definition
        self.init()

    def init(self) -> None:
        """
        Initializes the behavior instance.
        """
        return None

    async def enter(self, item: IItem) -> None:
        """
        Enters the behavior for the given item.

        Args:
            item: The item instance that will be processed.
        """
        return None

    async def start(self, item: IItem) -> Any:
        """
        Starts the behavior for the given item.

        Args:
            item: The item instance that will be processed.

        Returns:
            The behavior results.
        """
        return None

    async def run(self, item: IItem) -> None:
        return None

    async def end(self, item: IItem) -> None:
        return None

    async def exit(self, item: IItem) -> None:
        return None

    async def resume(self, item: IItem) -> None:
        return None

    async def restored(self, item: IItem) -> None:
        return None

    async def describe(self) -> List[List[str]]:
        return []

    async def get_node_attributes(self, attributes: List[Any]) -> None:
        return None

    async def get_item_attributes(self, item: IItem, attributes: List[Any]) -> None:
        return None
