"""
Default implementation of an application delegate handling core events and process interactions.

This module provides a default implementation of the `AppDelegateBase` class, responsible for handling
various BPMN-related lifecycle events. The main purpose of the delegate is to process events, manage services,
and handle messaging and signaling within the workflow engine.
"""

from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any, Dict

from pybpmn_server.interfaces.common import AppDelegateBase, IServiceProvider
from pybpmn_server.mail import send_mail

if TYPE_CHECKING:
    from pybpmn_server.common.configuration import Settings
    from pybpmn_server.engine.interfaces import IExecution, IItem

logger = logging.getLogger(__name__)


class DefaultAppDelegate(AppDelegateBase):
    """
    A class to process events, manage services, and handle messaging and signaling within the workflow engine.
    """

    async def _on_all_event(self, data: Dict[str, Any]) -> None:
        """
        Handle all events received by the application.
        """
        context = data.get("context")
        event = data.get("event")
        await self.execution_event(context, event)

    async def get_services_provider(self, context: IExecution) -> IServiceProvider:
        """
        Retrieve the services provider for the given execution context.
        """
        from types import MappingProxyType

        return MappingProxyType(self.service_providers)

    async def start_up(self, settings: Settings) -> None:
        """
        Perform initialization tasks when the application starts up.
        """
        print("server started..")
        locked_items = await self.data_store.locker.list({"items.status": "start"})
        if locked_items:
            logger.info(f"** There are {len(locked_items)} locked items")
            for item in locked_items:
                logger.debug(
                    f"   item hung: '{item.elementId}' seq: {item.seq} {item.type} {item.status} "
                    f"in process:'{item.processName}' - Instance id: '{item.instanceId}'"
                )

        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        await self.data_store.locker.delete({"time": {"$lte": yesterday}})
        return None

    def send_email(self, to: str | list[str], subject: str, body: str) -> None:
        """
        Send an email.

        Args:
            to: Recipient(s) of the email.
            subject: Subject line of the email.
            body: Body content of the email.
        """
        if isinstance(to, str):
            to = [to]

        send_mail(to, subject, body=body)

    async def execution_started(self, execution: IExecution) -> None:
        """
        Handle execution start event.
        """
        pass

    async def execution_event(self, context: Any, event: Any) -> None:
        """
        Handle execution event.
        """
        pass

    async def message_thrown(
        self, message_id: str, data: dict[str, Any], message_matching_key: Any, item: IItem
    ) -> None:
        """
        Handle message thrown event.

        Args:
            message_id: The message id.
            data: The message data.
            message_matching_key: The message matching key.
            item: The item to process.
        """
        msg_id = getattr(item.node, "message_id", message_id)
        logger.info(f"Message Issued: {msg_id}")

        # issue it back for others to receive
        resp = await item.context.engine.throw_message(msg_id, data, message_matching_key)
        if resp and resp.instance:
            logger.info(f" invoked another process {resp.instance.id} for {resp.instance.name}")
        else:
            await self.issue_message(message_id, data)

    async def issue_message(self, message_id: str, data: dict[str, Any]) -> None:
        """
        Issue a message to the engine.
        """
        pass

    async def issue_signal(self, signal_id: str, data: dict[str, Any]) -> None:
        """
        Issue a signal to the engine.
        """
        pass

    async def signal_thrown(
        self, signal_id: str, data: dict[str, Any], message_matching_key: Any, item: IItem
    ) -> None:
        """
        Handle signal thrown event.
        """
        logger.info(f"Signal Issued: {signal_id}")

        # issue it back for others to receive
        resp = await item.context.engine.throw_signal(signal_id, data, message_matching_key)
        if resp and resp.instance:
            logger.info(f" invoked another process {resp.instance.id} for {resp.instance.name}")
        else:
            await self.issue_signal(signal_id, data)

    async def service_called(self, input_data: Dict[str, Any], execution: IExecution, item: IItem) -> None:
        """
        Handle service call event.

        Args:
            input_data: The input data for the service.
            execution: The current execution context.
            item: The item being processed.
        """
        logger.info(f"Service called: {input_data}")
        return None
