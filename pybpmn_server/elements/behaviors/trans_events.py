"""Transaction events."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from pybpmn_server.elements.behaviors.behavior import Behavior
from pybpmn_server.interfaces.enums import ItemStatus, NodeAction, NodeSubtype, TokenStatus

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IItem

logger = logging.getLogger(__name__)


class CancelEventBehavior(Behavior):
    """
    Behavior for handling Cancel events in BPMN elements.
    """

    def init(self) -> None:
        """
        Initializes the CancelEventBehavior, setting the node subtype to NodeSubtype.cancel.
        """
        self.node.sub_type = NodeSubtype.cancel

    async def run(self, item: IItem) -> None:
        """
        Runs the CancelEventBehavior, terminating the item and setting its status to wait.
        """
        from pybpmn_server.elements.events import Event

        await Event.terminate(item)
        item.status = ItemStatus.wait
        item.token.status = TokenStatus.running

    async def start(self, item: IItem) -> NodeAction:
        """
        Starts the CancelEventBehavior, checking if the event is catching or throwing and taking appropriate action.
        """
        logger.info(f"starting a Cancel Event {self.node.is_catching}")
        if self.node.is_catching:
            return NodeAction.WAIT
        else:
            logger.info("Cancel Event is throwing a TransactionCancel")

            trans_item = None
            if item.token.parent_token:
                trans_item = item.token.parent_token.origin_item

            item.token.process_cancel(item)

            if trans_item:
                from pybpmn_server.elements.transaction import Transaction

                await Transaction.cancel(trans_item)

            return NodeAction.ERROR


class CompensateEventBehavior(Behavior):
    """
    Behavior for handling Compensate events in BPMN elements.
    """

    def init(self) -> None:
        """
        Initializes the CompensateEventBehavior, setting the node subtype to NodeSubtype.compensate.
        """
        self.node.sub_type = NodeSubtype.compensate

    async def start(self, item: IItem) -> NodeAction:
        """
        Starts the CompensateEventBehavior, taking appropriate action if the event is catching or throwing.
        """
        logger.info(f"starting a Compensate Event {self.node.is_catching}")
        if self.node.is_catching:
            return NodeAction.CONTINUE
        else:
            logger.info("Compensate Event")
            transaction_id = self.transaction_id

            trans_item = None
            for t in item.token.execution.tokens.values():
                for i in t.path:
                    if i.node.id == transaction_id:
                        trans_item = i
                        break
                if trans_item:
                    break

            if trans_item:
                from pybpmn_server.elements.transaction import Transaction

                await Transaction.compensate(trans_item)

            return NodeAction.CONTINUE

    @property
    def transaction_id(self) -> Optional[str]:
        """
        Retrieves the transaction ID for the Compensate Event behavior.
        """
        if self.definition.get("activityRef"):
            return self.definition["activityRef"].get("id")
        return None
