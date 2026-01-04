from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from pyee.asyncio import AsyncIOEventEmitter

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IExecution


class Listener(AsyncIOEventEmitter):
    async def do_event(
        self, event: str, execution: IExecution, item: Any = None, event_details: Dict[str, Any] = None
    ):
        if event_details is None:
            event_details = {}

        execution.item = item
        await self.delegate_event(event, execution, event_details)
        await self.emit(event, {"event": event, "context": execution, "event_details": event_details})
        await self.emit("all", {"event": event, "context": execution, "event_details": event_details})

    async def delegate_event(self, event: str, execution: IExecution, event_details: Dict[str, Any]):
        app = execution.app_delegate

        if hasattr(app, event) and callable(getattr(app, event)):
            # method exists in the component
            method = getattr(app, event)
            await method(event, execution, event_details)

        # def_delegate logic was commented out in TS
