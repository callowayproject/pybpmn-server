"""This module contains the message event behavior."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, List, Optional

from pybpmn_server.elements.behaviors.behavior import Behavior
from pybpmn_server.interfaces.enums import NodeSubtype

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IItem

logger = logging.getLogger(__name__)


class MessageEventBehavior(Behavior):
    """
    Behavior for handling message events in BPMN elements.
    """

    def init(self) -> None:
        """
        Initializes the message event behavior by setting the message ID and node subtype.
        """
        self.node.message_id = self.message_id
        self.node.sub_type = NodeSubtype.message

    async def start(self, item: IItem) -> None:
        """
        Handles the start of a message event behavior, either catching or throwing a message.
        """
        logger.info("message event behaviour start")
        if self.node.is_catching:
            item.message_id = self.message_id
        else:  # throw a message
            output = await self.node.get_output(item)
            matching_key = item.context.message_matching_key
            item.token.log(
                f".Throwing Message <{self.message_id}> - output: {json.dumps(output, default=str)} - matching key "
                f": {json.dumps(matching_key, default=str)}"
            )
            item.context.app_delegate.message_thrown(self.message_id, output, matching_key, item)

    @property
    def message_id(self) -> Optional[str]:
        """
        Retrieves the message identifier for the message event behavior.

        Returns None if not applicable or not found.
        """
        message_ref = self.definition.get("messageRef")
        return message_ref.get("name") if message_ref else None

    async def describe(self) -> List[List[str]]:
        """
        Provides a description of the message event behavior, including whether it catches or throws a message.

        Returns a list of lists with the description details.
        """
        if self.node.is_catching:
            return [["Message", f"catches message '{self.message_id}'"]]
        else:
            return [["Message", f"throws message '{self.message_id}'"]]


class SignalEventBehavior(Behavior):
    """
    Behavior for handling signal events in BPMN elements.
    """

    def init(self) -> None:
        """
        Initializes the signal event behavior by setting the signal ID and node subtype.
        """
        self.node.signal_id = self.signal_id
        self.node.sub_type = NodeSubtype.signal

    async def start(self, item: IItem) -> None:
        """
        Handles the start of a signal event behavior, either catching or throwing a signal.
        """
        if self.node.is_catching:
            item.signal_id = self.signal_id
        else:  # throw a signal
            output = await self.node.get_output(item)
            matching_key = item.context.message_matching_key
            item.token.log(
                f".Throwing Signal <{self.signal_id}> - output: {json.dumps(output, default=str)} - "
                f"matching key : {json.dumps(matching_key, default=str)}"
            )
            item.context.app_delegate.signal_thrown(self.signal_id, output, matching_key, item)

    @property
    def signal_id(self) -> Optional[str]:
        """
        Retrieves the signal identifier for the signal event behavior.

        Returns None if not applicable or not found.
        """
        signal_ref = self.definition.get("signalRef")
        if signal_ref:
            return signal_ref.get("name")
        return None
