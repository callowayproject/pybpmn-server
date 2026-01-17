"""Execution component for managing process instances and token execution."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from opentelemetry import trace

from pybpmn_server.common.configuration import Settings
from pybpmn_server.common.configuration import settings as default_settings
from pybpmn_server.elements.tasks import CallActivity
from pybpmn_server.engine import data_handler
from pybpmn_server.engine.interfaces import IExecution, IItem, IToken
from pybpmn_server.interfaces.enums import ExecutionEvent, ExecutionStatus, TokenStatus, TokenType

if TYPE_CHECKING:
    from pybpmn_server.datastore.data_objects import InstanceData, ItemData
    from pybpmn_server.elements.interfaces import INode

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class Execution(IExecution):
    """Execution component for managing process instances and token execution."""

    @property
    def execution(self) -> Execution:
        """
        Get the execution instance.
        """
        return self

    async def till_done(self) -> Execution:
        """
        Wait for the execution to complete.
        """
        if self.worker:
            await self.worker
        return self

    def get_node_by_id(self, node_id: str) -> INode:
        """
        Get a node by its ID within the execution definition.
        """
        return self.definition.get_node_by_id(node_id)

    def get_token(self, token_id: str) -> IToken:
        """
        Get a token by its ID within the execution.
        """
        return self.tokens.get(token_id)

    async def _check_end(self) -> None:
        """
        Check if the execution has ended and perform cleanup if necessary.
        """
        active = sum(
            t.status != TokenStatus.end and t.status != TokenStatus.terminated and t.type != TokenType.EventSubProcess
            for t in self.tokens.values()
        )
        if active == 0:
            await self.end()

    async def end(self) -> None:
        """
        End the execution and perform cleanup.
        """
        self.log(".execution ended.")

        self.instance.ended_at = datetime.now(tz=timezone.utc)
        self.instance.status = ExecutionStatus.end
        if getattr(self.instance, "parent_item_id", None):
            await CallActivity.execution_ended(self)

        if self.process:
            await self.process.end(self)
            await self.do_execution_event(self.process, ExecutionEvent.process_end)

    async def terminate(self) -> None:
        """
        Terminate the execution and stop all associated tokens.
        """
        for t in list(self.tokens.values()):
            await t.terminate()

    def stop(self) -> None:
        """
        Stop the execution by stopping all associated tokens.
        """
        for t in self.tokens.values():
            t.stop()

    @tracer.start_as_current_span("execution.execute")
    async def execute(
        self,
        start_node_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        user_name: Optional[str] = None,
    ) -> None:
        """
        Execute the process instance with an optional start node, input data, options, and user name.
        """
        from pybpmn_server.engine.token import Token, TokenType

        trace.get_current_span().set_attributes(
            {
                "execution_id": self.id,
                "type": "execution",
                "label": "Start Process",
                "user_name": user_name or "",
                "action": "execute",
                "name": self.name or self.id,
                "start_node_id": start_node_id or "",
                "input_data": input_data or "",
            }
        )

        input_data = input_data or {}
        self.operation = "execute"
        self.user_name = user_name

        self.log("^ACTION:execute:")

        self.info(
            json.dumps(
                {
                    "type": "execution",
                    "label": "Start Process",
                    "userName": user_name,
                    "action": "execute",
                    "name": self.name,
                    "startNodeId": start_node_id,
                    "inputData": input_data,
                }
            )
        )

        await self.definition.load()
        # self.services_provider = await self.app_delegate.get_services_provider(self)
        self.instance.status = ExecutionStatus.running
        await self.listener.emit_async("execution.execution_started", self)

        self.instance.data = input_data.copy()
        self.instance.started_at = datetime.now(timezone.utc)

        start_node = self.get_node_by_id(start_node_id) if start_node_id else self.definition.get_start_node()

        if not start_node:
            self.error("No Start Node")
            return

        self.process = start_node.process
        await self.do_execution_event(self.process, ExecutionEvent.process_start)

        self.log(f"..starting at : {start_node.id}")

        token = await Token.start_new_token(
            TokenType.Primary, self, start_node, None, None, None, None, input_data, True
        )

        # start all event sub processes for the process
        proc = start_node.process
        await proc.start(self, token)
        await token.execute(input_data)
        await self._check_end()

        if self.promises:
            await asyncio.gather(*self.promises, return_exceptions=True)
            self.promises = []

        self.log(".execute returned")
        await self.do_execution_event(self.process, ExecutionEvent.process_wait)

        self.report()
        if self.promises:
            await asyncio.gather(*self.promises, return_exceptions=True)
            self.promises = []

        await self.save()

    async def assign(
        self,
        item_id: Any,
        input_data: Any,
        assignment: Optional[Dict[str, Any]] = None,
        user_name: Optional[str] = None,
    ) -> None:
        """
        Assign input data to an item within the execution with an optional assignment.
        """
        if assignment is None:
            assignment = {}

        self.log(
            f"Execution({self.name}).assign: item_id={item_id} data {json.dumps(input_data)} "
            f"assignment:{json.dumps(assignment)}"
        )
        self.user_name = user_name
        self.operation = "assign"

        for i in self.get_items():
            if i.id == item_id:
                self.item = i
                break

        if self.item:
            for key, val in assignment.items():
                setattr(self.item, key, val)

            self.append_data(input_data, self.item, None)

            await self.item.node.do_event(self.item, ExecutionEvent.node_assign)
            await self.item.node.validate(self.item)
            self.info(f"Task {self.item.node.name} -{self.item.node.id} Assigned by {self.user_name} to:{assignment}")
            await self.save()
            self.log(f"Execution({self.name}).assign: finished!")

    async def signal_item(  # noqa: C901
        self,
        execution_id: str,
        input_data: dict[str, Any],
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
        no_wait: bool = False,
    ) -> IExecution:
        """
        Signal an item within the execution with input data, user name, and options.

        Args:
            execution_id: The ID of the item to signal.
            input_data: The input data to be assigned to the item.
            user_name: The name of the user performing the signal operation.
            restart: Flag to indicate if this is a restart operation.
            recover: Flag to indicate if this is a recovery operation.
            no_wait: Flag to indicate if this is a no-wait operation.

        Returns:
            The modified execution object.
        """
        import json

        self.log(f"Execution({self.name}).signal_item: item_id={execution_id} data {json.dumps(input_data)}")
        self.operation = "signal"
        self.user_name = user_name
        token = None

        # get process
        if self.tokens:
            first_token = next(iter(self.tokens.values()))
            if first_token.path:
                self.process = first_token.path[0].node.process

        await self.listener.emit_async("execution.execution_started", self)
        if self.process:
            await self.do_execution_event(self.process, ExecutionEvent.process_invoke)

        for t in self.tokens.values():
            if t.current_item and t.current_item.id == execution_id:
                self.item = t.current_item
                token = t
                break

        if token:
            self.info(
                json.dumps(
                    {
                        "type": "execution",
                        "label": "Invoke Item",
                        "action": "signalInput",
                        "id": token.current_node.id,
                        "item_id": execution_id,
                        "user_name": user_name,
                        "restart": restart,
                        "recover": recover,
                        "no_wait": no_wait,
                        "input_data": input_data,
                    }
                )
            )

            self.log(f"Execution({self.name}).signal: .. launching a token signal")
            await token.signal(input_data, restart=restart, recover=recover)

            if no_wait:
                return self

            self.log(f"Execution({self.name}).signal_item: .. signal token is done")

        self.log(
            f"Execution({self.name}).signal_item: returning .. waiting for promises status:{self.instance.status} "
            f"id: {execution_id}"
        )

        await self._check_end()

        if self.promises:
            await asyncio.gather(*self.promises, return_exceptions=True)
            self.promises = []

        if self.process:
            await self.do_execution_event(self.process, ExecutionEvent.process_invoked)

        self.log(
            f"Execution({self.name}).signal_item: returned process status:{self.instance.status} id: {execution_id}"
        )

        self.report()

        if self.promises:
            await asyncio.gather(*self.promises, return_exceptions=True)
            self.promises = []

        await self.save()
        self.log(f"Execution({self.name}).signal_item: finished!")

        return self

    async def restart(self, item_id: Any, input_data: Any, user_name: Optional[str] = None) -> IExecution:
        """
        Restarts the current execution process associated with an ended instance.

        This method transitions the instance back to a running state and recalibrates its status. It applies a restart
        signal to the specified item with the provided input data and options.

        Args:
            item_id: Identifier of the item to restart from.
            input_data: Data to be processed during the restart.
            user_name: Name of the user initiating the restart, if available.

        Returns:
            The modified instance of the current execution, with an updated state.
        """
        self.log(f"Execution({self.name}).restart: from item: {item_id} data {json.dumps(input_data)}")
        self.operation = "signal"
        self.user_name = user_name

        self.log(f"..restarting at : {item_id}")

        # check if the instance has ended
        if self.instance.status != ExecutionStatus.end:
            self.error(
                f"***ERROR*** restart must be for an instance with end status, current instance has status of "
                f"{self.instance.status}"
            )

        self.instance.status = ExecutionStatus.running
        self.instance.ended_at = None

        await self.signal_item(item_id, input_data, user_name, restart=True)
        self.log(f"Execution({self.name}).restart: finished!")

        return self

    async def signal_event(  # noqa: C901
        self,
        execution_id: Any,
        input_data: Any,
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
    ) -> IExecution:
        """
        Signals an event by invoking a specific node in an execution process.

        This method interacts with a token corresponding to the provided execution ID or handles secondary start
        events within a process. It ensures proper signaling, restarts, or recovery operations depending on the
        provided options.

        This method involves various steps, including obtaining the services provider, initiating execution events,
        processing tokens, handling start nodes for restart scenarios, updating execution status, and saving changes
        to the execution instance.

        Args:
            execution_id: Unique identifier of the execution event to signal.
            input_data: Input data required for performing the operation on the target node or token.
            user_name: Optional string representing the user initiating the signal. Defaults to None.
            restart: Flag indicating whether to restart the process from the beginning. Defaults to False.
            recover: Flag indicating whether to recover from a previous failure. Defaults to False.

        Returns:
            The updated execution instance after signaling the event.
        """
        from pybpmn_server.engine.token import Token, TokenType

        self.log(f"Execution({self.name}).signal: execution_id={execution_id}")
        self.operation = "signal"
        self.user_name = user_name
        token = None

        await self.listener.emit_async("execution.execution_started", self)
        if self.process:
            await self.do_execution_event(self.process, ExecutionEvent.process_invoke)

        for t in self.tokens.values():
            if t.current_node and t.current_node.id == execution_id:
                token = t
                break

        if token:
            await token.signal(input_data, restart=restart, recover=recover)
        else:
            # check for secondary start event
            node = None
            first_token = self.tokens.get(0)
            started_node_id = first_token.path[0].element_id if first_token and first_token.path else None

            if self.instance.status == ExecutionStatus.end and not restart:
                self.error("*** ERROR **** can not start a completed process")

            for proc in self.definition.processes.values():
                starts = proc.get_start_nodes()
                for start in starts:
                    if start.id != started_node_id and start.id == execution_id:
                        node = self.get_node_by_id(execution_id)
                        break
                if node:
                    break

            if node:
                if restart:
                    self.instance.status = ExecutionStatus.running
                    self.instance.ended_at = None

                await Token.start_new_token(TokenType.Primary, self, node, None, None, None, None, input_data)
            else:
                self.error(f"*** ERROR *** task id not valid: {execution_id}")

        if self.promises:
            await asyncio.gather(*self.promises, return_exceptions=True)
            self.promises = []

        await self.save()
        return self

    async def signal_repeat_timer_event(self, execution_id: Any, prev_item: Any, input_data: Any) -> IExecution:
        """
        Handles the repeat timer event by signaling the process, creating a new token for the boundary event.

        This is triggered when a repeat timer boundary event occurs in the workflow.

        Args:
            execution_id: The unique identifier of the current execution.
            prev_item: The previous execution item that triggered this timer event.
            input_data: Input data associated with this event.

        Returns:
            The updated execution object after processing the repeat timer event.
        """
        from pybpmn_server.engine.token import Token, TokenType

        self.log(f"Execution({self.name}).signal_repeat_timer: execution_id={execution_id}")
        self.operation = "signal_repeat_timer"

        await self.listener.emit_async("execution.execution_started", self)
        if self.process:
            await self.do_execution_event(self.process, ExecutionEvent.process_invoke)

        new_token = await Token.start_new_token(
            TokenType.BoundaryEvent, self, prev_item.node, None, prev_item.token, prev_item, None
        )

        new_item = new_token.current_item
        if new_item:
            new_item.timer_count = prev_item.timer_count + 1

        await self._check_end()
        if self.promises:
            await asyncio.gather(*self.promises, return_exceptions=True)
            self.promises = []

        await self.save()
        return self

    async def save(self) -> None:
        """
        Saves the current execution state to the data store.
        """
        self.log(f"..Saving instance {self.instance.id} {json.dumps(self.instance.data)}")
        state = self.get_state()
        await self.do_execution_event(self, ExecutionEvent.process_saving)
        await self.data_store.save_instance(state)

    def get_items(self, query: Optional[Any] = None) -> List[IItem]:
        """
        Retrieves a list of items from the execution, optionally filtered by a query.

        Args:
            query: A query to filter the items. Defaults to None.

        Returns:
            A list of items matching the query.
        """
        items: List[IItem] = []
        for t in self.tokens.values():
            items.extend(iter(t.path))
        items.sort(key=lambda x: x.seq)
        return items

    def get_items_data(self) -> List[ItemData]:
        """
        Retrieves a list of item data from the execution, optionally filtered by a query.

        Returns:
            A list of item data matching the query.
        """
        return [item.save() for item in self.get_items()]

    def get_state(self) -> InstanceData:
        """
        Retrieves the current state of the execution, including tokens, loops, and items.

        Returns:
            The current state of the execution.
        """
        tokens = []
        loops_map = {}
        for t in self.tokens.values():
            if t.loop:
                loops_map[t.loop.id] = t.loop
            tokens.append(t.save())

        loops = [loop.save() for loop in loops_map.values()]
        items = [item.save() for item in self.get_items()]

        self.instance.items = items
        self.instance.loops = loops
        self.instance.tokens = tokens

        return self.instance

    @staticmethod
    def _find_save_point(state: Any, item_id: Any) -> Any:
        """
        Finds the save point for a given item ID within the execution state.

        Args:
            state: The execution state to search within.
            item_id: The ID of the item to find the save point for.

        Returns:
            The save point for the item, or None if not found.
        """
        sps = state.get("save_points", {})
        for sp in sps.values():
            for it in sp.get("items", []):
                if it.get("id") == item_id:
                    return sp
        return None

    @staticmethod
    async def restore(  # noqa: C901
        state: InstanceData, configuration: Optional[Settings] = None, item_id: Optional[Any] = None
    ) -> Execution:
        """
        Restores an execution from a given state, optionally starting from a specific item ID.

        Args:
            state: The execution state to restore from.
            configuration: The configuration to restore from.
            item_id: The ID of the item to start the execution from. Defaults to None.

        Returns:
            The restored execution instance.
        """
        from pybpmn_server.engine.item import Item
        from pybpmn_server.engine.loop import Loop
        from pybpmn_server.engine.token import Token

        configuration = configuration or default_settings
        state_tokens = state.tokens
        state_items = state.items
        state_loops = state.loops

        if item_id is not None:
            save_point = Execution._find_save_point(state, item_id)
            if save_point:
                state_tokens = save_point.get("tokens", [])
                state_items = save_point.get("items", [])
                state_loops = save_point.get("loops", [])
            else:
                logger.error(f"***Error*** No savePoint found for item {item_id}")

        source = state.source or await configuration.model_data_store.get_source(state.name)

        execution = Execution(state.name, source, configuration, state)
        await execution.definition.load()

        token_loops = []
        tokens = {}
        for t_data in state_tokens:
            token = Token.load(execution, t_data)
            if t_data.loop_id is not None:
                token_loops.append({"id": token.id, "loop_id": t_data["loop_id"]})
            execution.tokens[token.id] = token
            tokens[token.id] = token

        loops = {}
        for l_data in state_loops:
            loop = Loop.load(execution, l_data)
            loops[loop.id] = loop

        for tl in token_loops:
            token = tokens.get(tl["id"])
            loop = loops.get(tl["loop_id"])
            if token:
                token.loop = loop

        # items
        items_list = []
        for i_data in state_items:
            state_token = execution.get_token(i_data.token_id)
            item = Item.load(execution, i_data, state_token)
            if state_token:
                state_token.path.append(item)
            items_list.append(item)

        # token.origin_item
        for t_data in state_tokens:
            token = execution.get_token(t_data.id)  # type: ignore[assignment]
            origin_item_id = t_data.origin_item
            if token and origin_item_id:
                for it in items_list:
                    if it.id == origin_item_id:
                        token.origin_item = it
                        break

        execution.log(".restore completed")
        await execution.restored()
        return execution

    async def restored(self) -> None:
        """
        Trigger the process restored event and resume tokens.
        """
        await self.do_execution_event(self, ExecutionEvent.process_restored)
        for t in self.tokens.values():
            await t.restored()

    async def resume(self) -> None:
        """
        Resume the process execution and tokens.
        """
        if self.process:
            await self.do_execution_event(self.process, ExecutionEvent.process_resumed)
        for t in self.tokens.values():
            await t.resume()

    def report_token(self, token: IToken, level: int) -> dict[str, Any]:
        """
        Report the state of a token and its children recursively.

        Args:
            token: The token to report.
            level: The indentation level for logging.

        Returns:
            The token report dictionary.
        """
        import json

        if not isinstance(token, IToken):
            raise ValueError(f"token must be an instance of IToken not {type(token)}")
        branch = token.origin_item.element_id if token.origin_item else "root"
        parent = token.parent_token.id if token.parent_token else "-"

        p = "->".join([str(item.node.id) for item in token.path])
        loop_str = f" Loop: {token.loop.id} key:{token.items_key}" if token.loop else ""

        token_report: dict[str, Any] = {
            "level": level,
            "branch": branch,
            "parent": parent,
            "token": (token.id, token.type.value, token.status.value),
            "path": p,
            "current_node": token.current_node.id,
            "loop": token.loop.id if token.loop else None,
            "loop_key": token.items_key if token.loop else None,
            "data": token.data,
            "children": [],
        }

        self.log(
            f"{'  ' * (level + 1)}"
            f"token: {token.id} - {token.type} - {token.status} current: {token.current_node.id} from "
            f"{branch} child of {parent} path: {p} {loop_str} data:{json.dumps(token.data)}"
        )

        for t in token.children_tokens:
            token_report["children"].append(self.report_token(t, level + 1))

        return token_report

    def report(self) -> None:
        """
        Generate a detailed report of the execution state, including tokens and items.
        """
        self.log(".Execution Report ----")
        self.log(f"..Status: {self.instance.status}")
        instance_report = {
            "status": self.instance.status.value,
            "tokens": [self.report_token(token, 0) for token in self.tokens.values() if not token.parent_token],
            "data": self.instance.data,
            "items": [],
        }

        for indx, item in enumerate(self.get_items()):
            item_report = {
                "index": indx,
                "token": item.token.id,
                "element": item.element.id,
                "element_type": item.type,
                "status": item.status.value,
                "start_time": item.started_at,
                "end_time": item.ended_at,
                "loop_key": item.item_key,
            }
            instance_report["items"].append(item_report)  # type: ignore[union-attr]
            if item.element.type == "bpmn:SequenceFlow":
                self.log(
                    f"..Item:{indx} -T# {item.token.id} {item.element.id} Type: {item.element.type} "
                    f"status: {item.status}"
                )
            else:
                start_str = item.started_at.isoformat() if item.started_at else ""
                end_str = item.ended_at.isoformat() if item.ended_at else ""
                key_str = f" key:{item.item_key}" if item.item_key is not None else ""
                self.log(
                    f"..Item:{indx} -T# {item.token.id} {item.element.id} Type: {item.element.type} "
                    f"status: {item.status} from {start_str} to {end_str} id: {item.id}{key_str}"
                )
        # TODO: Create data store for execution reports
        # Otel doesn't like complex data structures. Probably will have to store this object
        # trace.get_current_span().set_attribute("execution_report", instance_report)
        import pprint

        pprint.pprint(instance_report)
        self.log(".data:")
        self.log(json.dumps(self.instance.data))

    def get_new_sequence(self, scope: str) -> int:
        """Get a new unique sequence number for a given scope within the execution."""
        if scope not in self.uids:
            self.uids[scope] = 0
        val = self.uids[scope]
        self.uids[scope] += 1
        return val

    async def do_execution_event(
        self, process: Any, event: Any, event_details: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Emit an event for the execution context.

        Args:
            process: The process associated with the event.
            event: The event type.
            event_details: Additional details for the event. Defaults to None.
        """
        event_details = event_details or {}
        if self.listener:
            await self.listener.emit_async(event, {"event": event, "context": self, "event_details": event_details})
            await self.listener.emit_async("all", {"event": event, "context": self, "event_details": event_details})

    async def do_item_event(self, item: Any, event: Any, event_details: Optional[dict[str, Any]] = None) -> None:
        """
        Emit an event for an item within the execution context.

        Args:
            item: The item associated with the event.
            event: The event type.
            event_details: Additional details for the event. Defaults to None.
        """
        self.item = item
        if self.listener:
            event_details = event_details or {}
            await self.listener.emit_async(event, {"event": event, "context": self, "event_details": event_details})
            await self.listener.emit_async("all", {"event": event, "context": self, "event_details": event_details})

    def log(self, *msg: Any) -> None:
        """
        Log a message at the default log level.

        Args:
            *msg: The message(s) to log.
        """
        logger.info(", ".join(msg))

    def log_s(self, *msg: Any) -> None:
        """
        Log an error message.

        Args:
            *msg: The error message(s) to log.
        """
        logger.info(", ".join(msg))

    def log_e(self, *msg: Any) -> None:
        """
        Log an error message.

        Args:
            *msg: The error message(s) to log.
        """
        logger.info(", ".join(msg))

    def info(self, *msg: Any) -> None:
        """
        Log an informational message.

        Args:
            *msg: The message(s) to log.
        """
        logger.info(", ".join(msg))

    def error(self, msg: Any) -> None:
        """
        Log an error message and trigger a process error event.

        Args:
            msg: The error message to log.
        """
        asyncio.create_task(self.do_execution_event(self, ExecutionEvent.process_error))  # noqa: RUF006
        # self.instance.logs.append(msg)
        logger.error(msg)

    def append_data(self, input_data: Any, item: Any, data_path: Optional[Any] = None) -> None:
        """
        Append data to the items this transaction belongs to.

        Args:
            input_data: The data to append.
            item: The item to which the data should be appended.
            data_path: Optional path within the item's data structure to append the data. Defaults to None.
        """
        data_handler.merge_data(self.instance.data, input_data, item, data_path)

    def get_data(self, data_path: Any) -> Any:
        """
        Retrieves data from the execution instance's data based on the provided data path.

        Args:
            data_path: The path to the data to retrieve.

        Returns:
            The retrieved data.
        """
        return data_handler.get_data(self.instance.data, data_path)

    async def process_queue(self) -> None:
        """Process the queue."""
        while True:
            running = False
            for token in list(self.tokens.values()):
                if token.status == TokenStatus.queued:
                    running = True
                    await token.execute(None)
            if not running:
                break
