"""
This module contains the behavior class for the error events in the BPMN.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from pybpmn_server.elements.behaviors.behavior import Behavior
from pybpmn_server.interfaces.enums import BpmnType, NodeAction, NodeSubtype, TokenStatus

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IItem

logger = logging.getLogger(__name__)


class ErrorEventBehavior(Behavior):
    """
    Behavior for error events in a BPMN process.
    """

    def init(self) -> None:
        """
        Initializes the error event behavior instance.
        """
        self.node.sub_type = NodeSubtype.error

    async def run(self, item: IItem) -> None:
        """
        Executes the run operation by invoking the termination process and updating its token status to 'running'.

        Args:
            item: The item instance that will be terminated and have its token status updated to 'running'.
        """
        # await Event.terminate(item) - stub for now or translate Events.ts
        from ..events import Event

        await Event.terminate(item)
        item.token.status = TokenStatus.running

    async def start(self, item: IItem) -> NodeAction:
        """
        Starts the error event behavior for the given item.
        """
        logger.info(f"starting an Error Event {self.node.is_catching}")
        if self.node.is_catching:
            return NodeAction.WAIT
        else:
            logger.info("Error Event is throwing an error")

            trans_item = None
            if item.token.origin_item and item.token.origin_item.type == BpmnType.Transaction:
                trans_item = item.token.origin_item
            elif item.token.parent_token and item.token.parent_token.origin_item:
                trans_item = item.token.parent_token.origin_item

            item.token.process_error(self.error_id, item)

            if trans_item:
                from ..transaction import Transaction

                await Transaction.cancel(trans_item)
                trans_item.token.status = TokenStatus.terminated
                await trans_item.node.end(trans_item, True)

            await item.node.end(item, False)
            return NodeAction.ERROR

    @property
    def error_id(self) -> Optional[str]:
        """
        Retrieves the error ID associated with the error event.

        Returns:
            The error ID if defined, otherwise None.
        """
        ref = self.definition.get("bpmn:errorRef") or self.definition.get("errorRef")
        if ref:
            return ref.get("errorCode")
        return None
