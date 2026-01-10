"""Behavior for handling timer events in BPMN elements."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from pybpmn_server.common import cron_utils
from pybpmn_server.elements.behaviors.behavior import Behavior
from pybpmn_server.interfaces.enums import ItemStatus, NodeAction, NodeSubtype

if TYPE_CHECKING:
    from pybpmn_parser.bpmn.common.flow_element import FlowElement

    from pybpmn_server.elements.interfaces import INode
    from pybpmn_server.engine.interfaces import IItem

logger = logging.getLogger(__name__)


class TimerBehavior(Behavior):
    """
    Behavior for handling timer events in BPMN elements.
    """

    def __init__(self, node: INode, definition: FlowElement):
        super().__init__(node, definition)
        self.duration: Optional[str] = None
        self.repeat: int = 1
        self.time_cycle: Optional[str] = None
        self.time_date: Optional[str] = None
        self.task: Optional[asyncio.Task] = None

    def init(self) -> None:
        """
        Initializes the behavior for timer event handling in BPMN elements.
        """
        self.node.sub_type = NodeSubtype.timer

        event_definitions = getattr(self.node.def_, "eventDefinitions", [])
        for ed in event_definitions:
            if ed.get("$type") == "bpmn:TimerEventDefinition":
                if ed.get("timeDuration"):
                    self.duration = ed["timeDuration"].get("body")
                elif ed.get("timeCycle"):
                    self.time_cycle = ed["timeCycle"].get("body")
                elif ed.get("timeDate"):
                    self.time_date = ed["timeDate"].get("body")

    async def get_time_due(self, item: IItem, timer_modifier: Optional[int] = None) -> Optional[datetime]:  # noqa: C901
        """
        Calculates the due time for a timer event based on the defined duration, cycle, or date.
        """
        time_due: Optional[datetime] = None

        if timer_modifier:
            seconds = timer_modifier / 1000.0
            return datetime.now() + timedelta(seconds=seconds)

        if self.duration:
            duration = self.duration
            if duration.startswith("$"):
                duration = item.context.script_handler.evaluate_expression(item, duration)

            seconds = cron_utils.time_due(duration)
            return datetime.now() + timedelta(seconds=seconds)

        elif self.time_cycle:
            time_cycle = self.time_cycle
            if time_cycle.startswith("$"):
                time_cycle = item.context.script_handler.evaluate_expression(item, time_cycle)

            seconds = cron_utils.time_due(time_cycle)
            self.repeat = cron_utils.get_repeat(time_cycle)
            return datetime.now() + timedelta(seconds=seconds)

        elif self.time_date:
            time_date = self.time_date
            if time_date.startswith("$"):
                time_date = item.context.script_handler.evaluate_expression(item, time_date)

            if isinstance(time_date, str):
                try:
                    time_due = datetime.fromisoformat(time_date.replace("Z", "+00:00"))
                except ValueError:
                    time_due = None
            elif isinstance(time_date, datetime):
                time_due = time_date

        return time_due

    async def start(self, item: IItem) -> NodeAction:
        """
        Starts the timer behavior for the given item.
        """
        if item.node.type == "bpmn:StartEvent":
            return NodeAction.CONTINUE

        item.token.log("..------timer running --- ")
        await self.start_timer(item)
        item.timer_count = 0

        return NodeAction.WAIT

    async def start_timer(self, item: IItem) -> None:
        """
        Starts the timer for the given item, setting the time due and scheduling the expiration task.
        """
        timer_modifier = None
        config = item.context.configuration
        if hasattr(config, "timers") and config.timers.get("forceTimersDelay"):
            timer_modifier = config.timers["forceTimersDelay"]
            item.token.log(f"...Timer duration modified by the configuration to {timer_modifier}")

        due = await self.get_time_due(item, timer_modifier)
        item.time_due = due

        if due:
            item.token.log(f"timer is set at {due} - {due.isoformat()}")
            seconds = (due - datetime.now()).total_seconds()
            logger.info(f"..setting timer for {seconds} seconds for: {item.id}")

            # Use asyncio instead of setTimeout
            self.task = asyncio.create_task(self.expires_task(item, seconds))

    async def expires_task(self, item: IItem, seconds: float) -> None:
        """
        Task to handle timer expiration, ensuring the timer is cancelled if the item is no longer waiting.
        """
        if seconds > 0:
            await asyncio.sleep(seconds)
        await self.expires(item)

    async def expires(self, item: IItem) -> None:
        """
        Handles timer expiration, signaling the item and checking for repeat timers.
        """
        exec_ = item.token.execution
        item.token.log(f"Action:---timer Expired --- lock:{exec_.is_locked} for {item.id}")

        if item.status == ItemStatus.wait:
            if exec_.is_locked:
                # In TS: exec.promises.push(exec.signalItem(item.id, {}));
                await exec_.signal_item(item.id, {})
            else:
                await exec_.engine.invoke({"items.id": item.id}, {})

        # Check for repeat
        if self.time_cycle and self.repeat > getattr(item, "timer_count", 0):
            await exec_.engine.start_repeat_timer_event(exec_.id, item, {})

    def end(self, item: IItem) -> None:
        """
        Cleans up the timer behavior for the given item, canceling the task if active.
        """
        # Cron.timerEnded(item) - stubbed or handled by server
        item.time_due = None
        if self.task:
            self.task.cancel()

    def resume(self, item: IItem) -> None:
        """
        Resumes the timer behavior for the given item, restarting the timer if necessary.
        """
        pass
