from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, ClassVar, Optional

from isodate import parse_duration

from pybpmn_server.common.configuration import Settings, settings
from pybpmn_server.server.interfaces import ICron

logger = logging.getLogger(__name__)


class Cron(ICron):
    """
    Manages timers and schedules tasks based on configurations and timing expressions.

    This class provides functionality to handle timer-related events and actions such as starting timers,
    scheduling tasks, and processing expired timers. It integrates with various components like the engine,
    data store, and script handler to perform its operations effectively. It also supports scheduling processes
    and items based on cron-like or duration-based expressions.
    """

    timers_fired: ClassVar[int] = 0
    timers_started: ClassVar[bool] = False

    def __init__(self, configuration: Optional[Settings] = None):
        self.configuration = configuration or settings
        self.checking_timers: bool = False
        self.engine = self.configuration.engine
        self.data_store = self.configuration.data_store
        self.script_handler = self.configuration.script_handler
        self.model_data_store = self.configuration.model_data_store

    @classmethod
    def timer_scheduled(cls, _: Any) -> None:
        """
        Increment the count of timers currently active (scheduled or running).
        """
        cls.timers_fired += 1

    @classmethod
    def timer_ended(cls, _: Any) -> None:
        """
        Decrement the count of timers currently active (scheduled or running).
        """
        cls.timers_fired -= 1

    async def start(self) -> None:
        """
        Start the timer management process.
        """
        await self.start_timers()

    async def start_timers(self) -> None:
        """
        Start the timer management process, ensuring only one instance runs at a time.
        """
        if Cron.timers_started:
            return
        Cron.timers_started = True

        try:
            query: dict[str, Any] = {"events.subType": "Timer"}
            events_list = await self.model_data_store.find_events(query)

            for entry in events_list:
                if hasattr(entry, "expression") and entry.expression:  # Using expression as per TS logic
                    self.schedule_process(entry)

            query = {"items.timeDue": {"$exists": True}, "items.status": "wait"}
            items_list = await self.data_store.find_items(query)

            for item in items_list:
                if time_due := item.get("timeDue"):
                    logger.info(f"...checking timer: {time_due}")
                    self.schedule_item(item)
        except Exception as exc:
            logger.exception(exc)

    async def item_timer_expired(self, item_id: str) -> None:
        """
        Handle the expiration of a timer for a specific item by invoking the engine.
        """
        await self.engine.invoke({"items.id": item_id}, {})

    async def process_timer_expired(self, event: Any) -> None:
        """
        Handle the expiration of a timer for a process by updating the data store.

        Update the reference date time, and scheduling the process for execution.
        """
        await self.model_data_store.update_timer(event.model_name)
        # referenceDateTime might need update
        event.reference_date_time = datetime.now().timestamp() * 1000
        self.schedule_process(event)
        await self.engine.start(event.model_name, None, None, event.element_id)

    def schedule_process(self, entry: Any) -> None:
        """
        Schedule a process for execution based on its timer configuration.
        """
        delay = self.time_due(entry.expression, getattr(entry, "reference_date_time", None))
        if delay is None:
            return

        schedule_at = datetime.now() + timedelta(seconds=delay)
        logger.debug(f"scheduling process {entry.model_name} delayed by {delay} seconds, scheduled at: {schedule_at}")

        if delay < 0:
            delay = 0.1

        loop = asyncio.get_event_loop()
        loop.call_later(delay, lambda: asyncio.create_task(self.process_timer_expired(entry)))

    def schedule_item(self, entry: Any) -> None:
        """
        Schedule an item for execution based on its timer configuration.
        """
        now_ms = datetime.now().timestamp() * 1000
        time_due = entry.get("timeDue")
        delay_ms = time_due - now_ms
        if delay_ms < 0:
            delay_ms = 100  # 0.1s

        loop = asyncio.get_event_loop()
        loop.call_later(delay_ms / 1000.0, lambda: asyncio.create_task(self.item_timer_expired(entry.get("id"))))

    @staticmethod
    def check_cron(expression: str, reference_date_time: Optional[float]) -> Optional[float]:
        """
        Check if a cron expression is valid and calculate the next run time.
        """
        from cron_converter import Cron

        now = datetime.now(tz=timezone.utc)
        base_date = datetime.fromtimestamp(reference_date_time / 1000.0) if reference_date_time else now
        if not base_date.tzinfo:
            base_date = base_date.replace(tzinfo=timezone.utc)
        cron_instance = Cron(expression)
        it = cron_instance.schedule(base_date)
        next_run = it.next()
        return (next_run - now).total_seconds()

    @staticmethod
    def time_due(expression: str, reference_date_time: Optional[float]) -> Optional[float]:
        """
        Calculate the time due for a timer based on the expression and reference date time.
        """
        if expression:
            delay = Cron.check_cron(expression, reference_date_time)
            if delay is not None:
                return delay

            delay = parse_duration(expression)
            if reference_date_time:
                now_ms = datetime.now(tz=timezone.utc).timestamp() * 1000
                delay += (reference_date_time - now_ms) / 1000.0
            return delay
        return None
