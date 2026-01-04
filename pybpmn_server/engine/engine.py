"""The process engine."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union

from pybpmn_server.common.configuration import Settings, settings
from pybpmn_server.engine.execution import Execution
from pybpmn_server.interfaces.enums import ExecutionEvent

logger = logging.getLogger(__name__)


class Engine:
    """The process engine."""

    def __init__(self, configuration: Optional[Settings] = None) -> None:
        self.running_counter: int = 0
        self.calls_counter: int = 0
        self.configuration = configuration or settings
        self.cache = self.configuration.cache_manager
        self.data_store = self.configuration.data_store
        self.model_data_store = self.configuration.model_data_store

    async def start(
        self,
        name: str,
        source: str,
        data: Optional[dict[str, Any]] = None,
        start_node_id: Optional[str] = None,
        user_name: Optional[str] = None,
        parent_item_id: Optional[str] = None,
        no_wait: bool = False,
    ) -> Execution:
        """
        Starts the execution of a workflow based on the provided parameters.

        This method initializes and manages the execution of a workflow, applying the
        necessary configurations and handling execution control. It also ensures
        proper resource management such as locking and releasing the execution.

        Args:
            name: The name of the workflow to start.
            source: The definition of the workflow to start.
            data: Input data for the workflow execution. Defaults to an empty dictionary if not provided.
            start_node_id: The ID of the starting node for the workflow execution.
                Defaults to None if not provided.
            user_name: The name of the user initiating the workflow execution. Defaults to None.
            parent_item_id: The ID of the parent node for the workflow execution.
            no_wait: If True, the execution will not wait for the workflow to complete before returning.

        Returns:
            Execution: An instance representing the workflow execution, which includes execution context and state.

        Raises:
            Any exceptions encountered during execution are handled and logged. The
            method attempts to manage resources and gracefully recover from errors.
        """
        data = data or {}
        self.running_counter += 1
        logger.info(f"^Action:engine.start {name}")
        execution = Execution(name, source, configuration=self.configuration)

        execution.instance.parent_item_id = parent_item_id
        execution.user_name = user_name
        execution.operation = "start"

        self.cache.add(execution)

        try:
            await self.lock(str(execution.id))
            execution.is_locked = True

            if no_wait:
                # In Python, we can't easily mimic the .then() of a Promise on a task without awaiting it at some point
                # or using a callback. We'll use a task.
                execution.worker = asyncio.create_task(execution.execute(start_node_id, self.sanitize_data(data)))

                def release_callback(task):
                    asyncio.create_task(self.release(execution))
                    logger.info(f"after worker is done releasing ..{execution.instance.id}")

                execution.worker.add_done_callback(release_callback)
                return execution
            else:
                print(execution)
                await execution.execute(start_node_id, self.sanitize_data(data))
                await self.release(execution)
                logger.info(f".engine.start ended for {name}")
                return execution
        except Exception as exc:
            await self.exception(exc, execution)
        finally:
            self.running_counter -= 1
            if execution and execution.is_locked:
                await self.release(execution)

    async def restart(
        self, item_query: Any, data: Any, user_name: str, options: Optional[Dict[str, Any]] = None
    ) -> Execution:
        if options is None:
            options = {}

        logger.info("^Action:engine.restart")
        execution = None
        self.running_counter += 1
        self.calls_counter += 1

        try:
            item = await self.data_store.find_item(item_query)
            instance = await self.data_store.find_instance({"id": item.instance_id}, None)

            execution = await self.restore(instance.id, item.id)
            await execution.restart(item.id, self.sanitize_data(data), user_name)
            await self.release(execution)
            return execution
        except Exception as exc:
            return await self.exception(exc, execution)
        finally:
            self.running_counter -= 1
            if execution and execution.is_locked:
                await self.release(execution)

    async def get(self, instance_query: Any) -> Execution:
        instance = await self.data_store.find_instance(instance_query, None)
        execution = await self.restore(instance.id)
        await self.release(execution)
        return execution

    async def lock(self, execution_id: str):
        logger.info(f"...locking ..{execution_id}")
        await self.data_store.locker.lock(execution_id)
        logger.info(f"   locking complete{execution_id}")

    async def release(self, execution: Optional[Execution], id_: Optional[str] = None):
        if id_ is None and execution:
            id_ = execution.id
        logger.info(f"...unlocking ..{id_}")
        await self.data_store.locker.release(id_)
        if execution:
            execution.is_locked = False

    async def restore(self, instance_id: str, item_id: Optional[str] = None) -> Execution:
        execution = None
        await self.lock(instance_id)

        instance = await self.data_store.find_instance({"id": instance_id}, "Full")
        live = self.cache.get_instance(instance.id)

        if live:
            execution = live
        else:
            execution = await Execution.restore(self.server, instance, item_id)
            execution.is_locked = True
            self.cache.add(execution)
            logger.info(f"restore completed: {instance.saved}")

        return execution

    async def invoke_item(self, item_query: Any, data: Any = None) -> Execution:
        return await self.invoke(item_query, data)

    async def assign(
        self,
        item_query: Any,
        data: Any = None,
        assignment: Any = None,
        user_name: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Execution:
        data = data or {}
        assignment = assignment or {}
        options = options or {}

        logger.info("^Action:engine.assign")
        logger.info(item_query)
        execution = None
        self.running_counter += 1
        self.calls_counter += 1

        try:
            items = await self.data_store.find_items(item_query)
            if len(items) > 1:
                logger.error(f"query produced more than {len(items)} items expecting only one{json.dumps(item_query)}")

            item = items[0] if items else None
            if not item:
                logger.error(f"query produced no items for {json.dumps(item_query)}")

            execution = await self.restore(item.instance_id)
            # In TS it was assigned to execution.worker but not awaited immediately if noWait?
            # Actually assign is usually synchronous-ish but might trigger things.
            await execution.assign(item.id, self.sanitize_data(data), assignment, user_name)
            await self.release(execution)
            return execution
        except Exception as exc:
            return await self.exception(exc, execution)
        finally:
            self.running_counter -= 1
            if execution and execution.is_locked:
                await self.release(execution)

    async def invoke(
        self,
        item_query: Any,
        data: Any = None,
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
        no_wait: bool = False,
    ) -> Execution:
        data = data or {}

        logger.info("^Action:engine.invoke")
        logger.info(item_query)
        execution = None
        self.running_counter += 1
        self.calls_counter += 1

        try:
            items = await self.data_store.find_items(item_query)
            if len(items) > 1:
                logger.error(f"query produced more than {len(items)} items expecting only one{json.dumps(item_query)}")

            item = items[0] if items else None
            if not item:
                logger.error(f"query produced no items for {json.dumps(item_query)}")

            if item.status != "wait":
                logger.info(
                    f"*****Item status is not in wait state {item.status} {item.element_id}-{item.process_name}"
                )

            execution = await self.restore(item.instance_id)
            await execution.signal_item(item.id, self.sanitize_data(data), user_name, restart, recover, no_wait)

            if no_wait:
                logger.info(".noWait")
                await execution.save()

                execution.worker = asyncio.create_task(
                    execution.signal_item(item.id, None)
                )  # Using signal_item instead of signal_item2 as per Step 5 notes

                def release_callback(task):
                    asyncio.create_task(self.release(execution))
                    logger.info(f"after worker is done releasing ..{item.instance_id}")

                execution.worker.add_done_callback(release_callback)
                return execution
            else:
                logger.info(".engine.continue ended")
                await self.release(execution)
                return execution
        except Exception as exc:
            return await self.exception(exc, execution)
        finally:
            self.running_counter -= 1
            if execution and execution.is_locked:
                await self.release(execution)

    async def start_repeat_timer_event(
        self, instance_id: str, prev_item: Any, data: Any = None, options: Dict[str, Any] = None
    ) -> Execution:
        if data is None:
            data = {}
        if options is None:
            options = {}

        logger.info("startRepeatTimeEvent")
        execution = None
        try:
            execution = await self.restore(instance_id)
            await execution.signal_repeat_timer_event(instance_id, prev_item, self.sanitize_data(data))
            await self.release(execution)
            logger.info(f"StartRepeatTimerEvent completed {execution.is_locked}")
            return execution
        except Exception as exc:
            return await self.exception(exc, execution)
        finally:
            if execution and execution.is_locked:
                await self.release(execution)

    async def start_event(
        self,
        instance_id: str,
        element_id: str,
        data: Any = None,
        user_name: str = None,
        options: Dict[str, Any] = None,
    ) -> Execution:
        if data is None:
            data = {}
        if options is None:
            options = {}

        logger.info("serverinvokeSignal")
        execution = None
        try:
            execution = await self.restore(instance_id)
            await execution.signal_event(element_id, self.sanitize_data(data), user_name, options)
            await self.release(execution)
            logger.info(f"Engine.StartEvent completed {execution.is_locked}")
            return execution
        except Exception as exc:
            return await self.exception(exc, execution)
        finally:
            if execution and execution.is_locked:
                await self.release(execution)

    async def throw_message(
        self, message_id: str, data: Any = None, matching_query: Any = None
    ) -> Optional[Execution]:
        if data is None:
            data = {}
        if matching_query is None:
            matching_query = {}

        logger.info("..^Action:engine.throwMessage ", message_id, self.sanitize_data(data), matching_query)
        if not message_id:
            return None

        events_query = {"events.messageId": message_id}
        events = await self.definitions.find_events(events_query)
        logger.info(f"..findEvents {len(events)}")

        if events:
            event = events[0]
            logger.info(
                f"..^Action:engine.throwMessage found target event {event.model_name} {json.dumps(data)} {event.element_id}"
            )
            return await self.start(event.model_name, data, event.element_id, event.element_id)

        items_query = matching_query.copy()
        items_query["items.messageId"] = message_id
        items_query["items.status"] = "wait"

        items = await self.data_store.find_items(items_query)
        if items:
            item = items[0]
            logger.info(f"Throw Signal {message_id} found target: {item.process_name} {item.id}")
            return await self.invoke({"items.id": item.id}, self.sanitize_data(data))
        else:
            logger.info(f"** engine.throwMessage failed to find a target for {json.dumps(items_query)}")
        return None

    async def throw_signal(self, signal_id: str, data: Any = None, matching_query: Any = None) -> List[Any]:
        if data is None:
            data = {}
        if matching_query is None:
            matching_query = {}

        logger.info("..^Action:engine.Throw Signal ", signal_id, self.sanitize_data(data), matching_query)
        instances = []
        if not signal_id:
            return []

        events_query = {"events.signalId": signal_id}
        events = await self.definitions.find_events(events_query)
        logger.info(f"..findEvents {len(events)}")

        for event in events:
            logger.info(f"..^Action:engine.Throw Signal found target {event.model_name} {data} {event.element_id}")
            res = await self.start(event.model_name, self.sanitize_data(data), event.element_id, None)
            instances.append(res.instance.id)

        items_query = matching_query.copy()
        items_query["items.signalId"] = signal_id
        items_query["items.status"] = "wait"

        items = await self.data_store.find_items(items_query)
        for item in items:
            logger.info(f"..^Action:engine.Throw Signal found target {item.process_name} {item.id}")
            res = await self.invoke({"items.id": item.id}, self.sanitize_data(data))
            instances.append({"instanceId": res.instance.id, "itemId": item.id})

        return instances

    def status(self) -> Dict[str, int]:
        return {"running": self.running_counter, "calls": self.calls_counter}

    async def upgrade(self, model: str, after_node_ids: List[str]) -> Union[List[str], Dict[str, Any]]:
        ds = self.server.data_store
        query: Dict[str, Any] = {"name": model}
        if after_node_ids:
            nors = [{"items": {"elemMatch": {"elementId": node}}} for node in after_node_ids]
            query["$nor"] = nors

        insts = await ds.find_instances(query, {"projection": {"id": 1}})
        source = await self.server.definitions.get_source(model, None)

        res_ids = []
        for inst in insts:
            await self.lock(inst.id)
            try:
                await ds.db.update(
                    ds.db_config["db"],
                    ds.db_config["Instance_collection"],
                    {"id": inst.id},
                    {"$set": {"source": source}},
                )
                res_ids.append(inst.id)
            except Exception as exc:
                return {"errors": str(exc)}
            finally:
                await self.release(None, inst.id)
        return res_ids

    async def exception(self, exc: Exception, execution: Optional[Execution]):
        import traceback

        logger.info(f"Exception: {exc}")
        logger.info(traceback.format_exc())

        if execution:
            await execution.do_execution_event(execution, ExecutionEvent.process_exception)

        return logger.error(exc)

    def sanitize_data(self, data: Any) -> Any:
        if data is None:
            return {}
        try:
            return json.loads(json.dumps(data))
        except:
            return data
