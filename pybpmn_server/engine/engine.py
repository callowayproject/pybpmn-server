"""The process engine."""

from __future__ import annotations

import asyncio
import json
import logging
from asyncio import Future
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from opentelemetry import trace

from pybpmn_server.engine.execution import Execution
from pybpmn_server.engine.interfaces import IEngine, IExecution
from pybpmn_server.interfaces.enums import ExecutionEvent

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IItem

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def sanitize_data(data: Any) -> dict[str, Any]:
    """
    Sanitizes the provided data by converting it to a dictionary if possible.

    Args:
        data: The data to be sanitized.

    Returns:
        The sanitized data as a dictionary, or an empty dictionary if the input is None.
    """
    if data is None:
        return {}
    try:
        return json.loads(json.dumps(data))
    except json.JSONDecodeError:
        return data


async def exception(exc: Exception, execution: Optional[IExecution]) -> None:
    """
    Handles an exception by logging its details and triggering an optional execution event.

    This method logs the provided exception and its stack trace. If an execution is provided, it triggers the
    `process_exception` event. Finally, the exception is logged as an error.

    Args:
        exc: The exception to be handled and logged.
        execution: The optional execution context that defines the handling behavior, if applicable.
    """
    trace.get_current_span().record_exception(exc)

    if execution:
        await execution.do_execution_event(execution, ExecutionEvent.process_exception)

    logger.exception(exc, stack_info=True)


class Engine(IEngine):
    """The process engine."""

    @tracer.start_as_current_span("engine.start")
    async def start(
        self,
        name: str,
        source: str,
        data: Optional[dict[str, Any]] = None,
        start_node_id: Optional[str] = None,
        user_name: Optional[str] = None,
        parent_item_id: Optional[str] = None,
        no_wait: bool = False,
    ) -> Optional[Execution]:
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
            An instance representing the workflow execution, which includes execution context and state.
        """
        data = data or {}
        self.running_counter += 1
        logger.info(f"^Action:engine.start {name}")
        trace.get_current_span().set_attribute("workflow_name", name)
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
                execution.worker = asyncio.create_task(execution.execute(start_node_id, sanitize_data(data)))

                def release_callback(_: Future) -> None:
                    """Callback to release execution after the worker is done."""
                    asyncio.create_task(self.release(execution))  # noqa: RUF006
                    logger.info(f"after worker is done releasing ..{execution.instance.id}")

                execution.worker.add_done_callback(release_callback)
                return execution
            else:
                await execution.execute(start_node_id, sanitize_data(data))
                await self.release(execution)
                logger.info(f".engine.start ended for {name}")
                return execution
        except Exception as exc:  # noqa: BLE001
            await exception(exc, execution)
            return None
        finally:
            self.running_counter -= 1
            if execution and execution.is_locked:
                await self.release(execution)

    @tracer.start_as_current_span("engine.restart")
    async def restart(self, item_query: dict[str, Any], data: dict[str, Any], user_name: str) -> Optional[IExecution]:
        """
        Restarts an execution based on the provided item query, data, and user information.

        The method retrieves the item and its associated instance from the data store, restores the execution state,
        re-initializes the execution with the provided data, and releases the execution lock after completion.

        Args:
            item_query: A query object or identifier used to locate the item in the data store.
            data: The data required to restart the execution. This may include input parameters or state information.
            user_name: The name of the user initiating the restart operation. Used for auditing or logging purposes.

        Returns:
            An instance of the `Execution` object representing the restarted execution process.
            This includes all relevant state and runtime information.
        """
        logger.info("^Action:engine.restart")
        execution = None
        self.running_counter += 1
        self.calls_counter += 1

        try:
            item = await self.data_store.find_item(item_query)
            instance = await self.data_store.find_instance({"id": item.instance_id}, None)

            execution = await self.restore(instance.id, item.id)
            await execution.restart(item.id, sanitize_data(data), user_name)
            await self.release(execution)
            return execution
        except Exception as exc:  # noqa: BLE001
            await exception(exc, execution)
            return None
        finally:
            self.running_counter -= 1
            if execution and execution.is_locked:
                await self.release(execution)

    async def get(self, instance_query: dict[str, Any]) -> IExecution:
        """
        Retrieves an execution instance based on the provided query.

        Args:
            instance_query: The query used to find the execution instance.

        Returns:
            The execution instance if found, otherwise None.
        """
        instance = await self.data_store.find_instance(instance_query, None)
        execution = await self.restore(instance.id)
        await self.release(execution)
        return execution

    @tracer.start_as_current_span("execution.lock")
    async def lock(self, execution_id: str) -> None:
        """
        Locks the execution with the specified ID, ensuring exclusive access.
        """
        trace.get_current_span().set_attribute("execution_id", execution_id)
        logger.info(f"...locking ..{execution_id}")
        await self.data_store.locker.lock(execution_id)

    @tracer.start_as_current_span("execution.unlock")
    async def release(self, execution: Optional[IExecution], id_: Optional[str] = None) -> None:
        """
        Releases the lock on the execution with the specified ID, allowing other operations to proceed.
        """
        if id_ is None and execution:
            id_ = execution.id
        trace.get_current_span().set_attribute("execution_id", id_)
        logger.info(f"...unlocking ..{id_}")
        await self.data_store.locker.release(id_)
        if execution:
            execution.is_locked = False

    async def restore(self, instance_id: str, item_id: Optional[str] = None) -> IExecution:
        """
        Restores the execution context for a given instance ID, optionally specifying an item ID to restore.

        Args:
            instance_id: The ID of the instance to restore.
            item_id: Optional ID of the specific item to restore within the instance.

        Returns:
            The restored execution context.
        """
        await self.lock(instance_id)

        instance = await self.data_store.find_instance({"id": instance_id}, "Full")
        if live := self.cache.get_instance(instance.id):
            execution = live
        else:
            execution = await Execution.restore(instance, self.configuration, item_id)
            execution.is_locked = True
            self.cache.add(execution)
            logger.info(f"restore completed: {instance.saved}")

        return execution

    @tracer.start_as_current_span("execution.invoke_item")
    async def invoke_item(self, item_query: dict[str, Any], data: Optional[dict[str, Any]] = None) -> IExecution:
        """
        Invokes an item in the execution context.

        Args:
            item_query: Query to identify the item to be invoked.
            data: Optional data to be passed to the item during invocation.

        Returns:
            The execution context after the item has been invoked.
        """
        return await self.invoke(item_query, data)

    async def assign(
        self,
        item_query: dict[str, Any],
        data: Optional[dict[str, Any]] = None,
        assignment: Any = None,
        user_name: Optional[str] = None,
    ) -> Optional[IExecution]:
        """
        Assigns an item to a user or task while maintaining proper execution and data flow.

        This method processes the assignment of an item by searching the data store for the
        item specified by the query, restoring its execution context, and assigning it to
        a task or user. It performs necessary error handling, logging, and ensures that resources
        are properly released in all scenarios.

        Args:
            item_query: Query used to locate the item in the data store.
            data: Additional data to be passed during assignment.
            assignment: Assignment-specific data used to configure the task or user allocation.
            user_name: Name of the user to whom the item is being assigned, if applicable.

        Returns:
            Execution: The execution instance that processes the assigned item.
        """
        data = data or {}
        assignment = assignment or {}

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
            await execution.assign(item.id, sanitize_data(data), assignment, user_name)
            await self.release(execution)
            return execution
        except Exception as exc:  # noqa: BLE001
            await exception(exc, execution)
            return None
        finally:
            self.running_counter -= 1
            if execution and execution.is_locked:
                await self.release(execution)

    @tracer.start_as_current_span("execution.invoke")
    async def invoke(
        self,
        item_query: dict[str, Any],
        data: Optional[dict[str, Any]] = None,
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
        no_wait: bool = False,
    ) -> Optional[IExecution]:
        """
        Invokes an execution action within the engine, interacting with an item based on the provided query and data.

        This method manages the execution's lifecycle, including signal processing and state updates.
        It also incorporates error handling and concurrency management.

        Args:
            item_query: Query parameters used to find the specific item in the data store.
            data: Additional data passed to the execution signal. Defaults to an empty dictionary if not provided.
            user_name: Name of the user triggering the action. Could be None if no user context is required.
            restart: Flag indicating whether the execution should be restarted. Default is False.
            recover: Flag indicating whether the execution should attempt recovery. Default is False.
            no_wait: Flag indicating whether the process should avoid waiting for completion before returning.
                Default is False.

        Returns:
            The execution instance processed by the action, if successfully invoked. Returns None if the invocation
            fails due to errors or an invalid state.

        Raises:
            Exception: Propagates exceptions encountered during execution lifecycle management,
                if not handled internally.
        """
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
            await execution.signal_item(item.id, sanitize_data(data), user_name, restart, recover, no_wait)

            if no_wait:
                logger.info(".noWait")
                await execution.save()

                execution.worker = asyncio.create_task(
                    execution.signal_item(item.id, {})
                )  # Using signal_item instead of signal_item2 as per Step 5 notes

                def release_callback(_: Future) -> None:
                    """Callback to release execution after the worker is done."""
                    asyncio.create_task(self.release(execution))  # noqa: RUF006
                    logger.info(f"after worker is done releasing ..{item.instance_id}")

                execution.worker.add_done_callback(release_callback)
                return execution
            else:
                logger.info(".engine.continue ended")
                await self.release(execution)
                return execution
        except Exception as exc:  # noqa: BLE001
            await exception(exc, execution)
            return None
        finally:
            self.running_counter -= 1
            if execution and execution.is_locked:
                await self.release(execution)

    async def start_repeat_timer_event(
        self, instance_id: str, prev_item: IItem, data: Optional[dict[str, Any]] = None
    ) -> Optional[IExecution]:
        """
        Starts a repeat timer event for a specific execution instance.

        Handles the restoration, signal processing, and release of the execution context.

        Args:
            instance_id: Identifier of the execution instance to start the repeat timer event for.
            prev_item: Previous item associated with the execution instance.
            data: Optional data to be passed during the repeat timer event signal.

        Returns:
            The execution instance that processes the repeat timer event, or None if an error occurs.

        Raises:
            Exception: Propagates exceptions encountered during execution lifecycle management,
                if not handled internally.
        """
        if data is None:
            data = {}

        logger.info("startRepeatTimeEvent")
        execution = None
        try:
            execution = await self.restore(instance_id)
            await execution.signal_repeat_timer_event(instance_id, prev_item, sanitize_data(data))
            await self.release(execution)
            logger.info(f"StartRepeatTimerEvent completed {execution.is_locked}")
            return execution
        except Exception as exc:  # noqa: BLE001
            await exception(exc, execution)
            return None
        finally:
            if execution and execution.is_locked:
                await self.release(execution)

    async def start_event(
        self,
        instance_id: str,
        element_id: str,
        data: Optional[dict[str, Any]] = None,
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
    ) -> Optional[IExecution]:
        """
        Starts an event by signaling it within an execution context.

        Handles initialization, signal invocation, and execution state management, ensuring the proper release process
        even in error scenarios.

        Args:
            instance_id: The unique identifier for the instance to be restored before signaling.
            element_id: The unique identifier representing the event element to be signaled.
            data: Optional data payload associated with the event, defaulting to an empty dictionary.
            user_name: Optional user name of the individual triggering the event, default is None.
            restart: Indicates whether the event should trigger a restart, default is False.
            recover: Indicates whether the event should trigger a recovery, default is False.

        Returns:
            The execution context after the event is processed.
        """
        data = data or {}

        logger.info("serverinvokeSignal")
        execution = None
        try:
            execution = await self.restore(instance_id)
            await execution.signal_event(element_id, sanitize_data(data), user_name, restart, recover)
            await self.release(execution)
            logger.info(f"Engine.StartEvent completed {execution.is_locked}")
            return execution
        except Exception as exc:  # noqa: BLE001
            await exception(exc, execution)
            return None
        finally:
            if execution and execution.is_locked:
                await self.release(execution)

    @tracer.start_as_current_span("engine.throw_message")
    async def throw_message(
        self, message_id: str, data: Any = None, matching_query: Any = None
    ) -> Optional[Execution]:
        """
        Throw a message event to trigger a process instance.
        """
        if data is None:
            data = {}
        if matching_query is None:
            matching_query = {}

        trace.get_current_span().set_attributes(
            {"message_id": message_id, "data": data, "matching_query": matching_query}
        )
        logger.info(f"..^Action:engine.throwMessage {message_id}, {sanitize_data(data)}, {matching_query}")
        if not message_id:
            return None

        events_query = {"events.messageId": message_id}
        events = await self.model_data_store.find_events(events_query)
        logger.info(f"..findEvents {len(events)}")

        if events:
            event = events[0]
            logger.info(
                "..^Action:engine.throwMessage found target event "
                f"{event.model_name} {json.dumps(data)} {event.element_id}"
            )
            return await self.start(event.model_name, data, event.element_id, event.element_id)

        items_query = matching_query.copy()
        items_query["items.messageId"] = message_id
        items_query["items.status"] = "wait"

        items = await self.data_store.find_items(items_query)
        if items:
            item = items[0]
            logger.info(f"Throw Signal {message_id} found target: {item.process_name} {item.id}")
            return await self.invoke({"items.id": item.id}, sanitize_data(data))
        else:
            logger.info(f"** engine.throwMessage failed to find a target for {json.dumps(items_query)}")
        return None

    async def throw_signal(self, signal_id: str, data: Any = None, matching_query: Any = None) -> List[Any]:
        """
        Process the given signal by finding and invoking relevant events and items that are waiting for it.

        The method triggers necessary actions and collects the results of the signal propagation.

        Args:
            signal_id: Identifier of the signal to be processed.
            data: Additional data to be passed during the signal processing. Default is an empty dictionary.
            matching_query: Query that specifies additional matching conditions for items.
                Default is an empty dictionary.

        Returns:
            A list containing the IDs of the instances or items that were affected by the signal propagation.
        """
        if data is None:
            data = {}
        if matching_query is None:
            matching_query = {}

        logger.info(f"..^Action:engine.Throw Signal {signal_id}, {sanitize_data(data)}, {matching_query}")
        instances = []
        if not signal_id:
            return []

        events_query = {"events.signalId": signal_id}
        events = await self.model_data_store.find_events(events_query)
        logger.info(f"..findEvents {len(events)}")

        for event in events:
            model_source = await self.model_data_store.get_source(event.model_name)
            logger.info(f"..^Action:engine.Throw Signal found target {event.model_name} {data} {event.element_id}")
            res = await self.start(event.model_name, model_source, sanitize_data(data), event.element_id, None)
            instances.append(res.instance.id)

        items_query = matching_query.copy()
        items_query["items.signalId"] = signal_id
        items_query["items.status"] = "wait"

        items = await self.data_store.find_items(items_query)
        for item in items:
            logger.info(f"..^Action:engine.Throw Signal found target {item.process_name} {item.id}")
            res = await self.invoke({"items.id": item.id}, sanitize_data(data))
            instances.append({"instanceId": res.instance.id, "itemId": item.id})

        return instances

    def status(self) -> dict[str, int]:
        """
        Returns the current status of the object.

        The method compiles a summary of the object's current state, including the count of running processes and the
        number of calls processed. This data is returned as a dictionary.

        Returns:
            A dictionary containing:
                - "running": The number of currently running processes.
                - "calls": The cumulative number of processed calls.
        """
        return {"running": self.running_counter, "calls": self.calls_counter}

    async def upgrade(self, model: str, after_node_ids: List[str]) -> list[str] | dict[str, Any]:
        """
        Upgrade the source of specified model instances in the data store.

        Returns a list of updated instance IDs or a dictionary containing error information.

        Args:
            model: The name of the model whose instances need to be upgraded.
            after_node_ids: A list of node IDs. Instances related to these nodes will be excluded
                from the upgrade process.

        Returns:
            A list of successfully upgraded instance IDs, or a dictionary with
                error details if an exception occurs during the upgrade process.
        """
        ds = self.data_store
        query: Dict[str, Any] = {"name": model}
        if after_node_ids:
            nors = [{"items": {"elemMatch": {"elementId": node}}} for node in after_node_ids]
            query["$nor"] = nors

        insts = await ds.find_instances(query, {"projection": {"id": 1}})
        source = await self.model_data_store.get_source(model)

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
            except Exception as exc:  # noqa: BLE001
                return {"errors": str(exc)}
            finally:
                await self.release(None, inst.id)
        return res_ids
