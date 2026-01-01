"""
This module contains the behavior class for the escalation events in the BPMN.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from pybpmn_server.elements.behaviors.behavior import Behavior
from pybpmn_server.interfaces.enums import NodeAction, NodeSubtype

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IItem

logger = logging.getLogger(__name__)


class EscalationEventBehavior(Behavior):
    """
    Behavior implementation for escalation events in the BPMN process engine.
    """

    def init(self) -> None:
        """
        Initializes the behavior instance.
        """
        self.node.sub_type = NodeSubtype.escalation

    async def start(self, item: IItem) -> NodeAction:
        """
        Starts the escalation event behavior for the given item.

        Args:
            item: The item instance that will be processed.

        Returns:
            The escalation event action.
        """
        logging.info(f"starting an Escalation Event {self.node.is_catching}")
        if self.node.is_catching:
            return NodeAction.WAIT
        else:
            logging.info("Escalation Event is throwing an escalation")
            item.token.process_escalation(self.escalation_id, item)
            return NodeAction.CONTINUE

    @property
    def escalation_id(self) -> Optional[str]:
        """
        Retrieves the escalation ID from the behavior definition.

        Returns:
            The escalation ID if found, otherwise None.
        """
        ref = self.definition.get("bpmn:escalationRef")
        if ref:
            return ref.get("escalationCode")
        return None
