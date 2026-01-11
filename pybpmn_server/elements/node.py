"""
A workflow process node and its associated behaviors, events, and execution logic.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, TypeVar

from opentelemetry import trace

from pybpmn_server.elements.behaviors.behavior_loader import BehaviorName
from pybpmn_server.elements.interfaces import Element, ILoopBehavior, INode
from pybpmn_server.interfaces.enums import (
    BpmnType,
    ExecutionEvent,
    FlowAction,
    ItemStatus,
    NodeAction,
    NodeSubtype,
    TokenType,
)

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IItem, IToken

T = TypeVar("T")
tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class Node(INode, Generic[T]):
    """
    Represents a workflow process node and its associated behaviors, events, and execution logic.

    This class serves as a crucial component in the workflow processing engine, providing
    methods to manage node execution, validate input and output, trigger events, handle loop
    behaviors, and interact with the execution token. Nodes represent logical units in a
    workflow and can process events, scripts, and data transformations specific to their type.
    """

    def _get_def_attr(self, name: str, default: Any = None) -> Any:
        return getattr(self.def_, name, default)

    @classmethod
    def from_element(cls, element: Element) -> INode:
        """
        Create a Node instance from an Element.
        """
        if isinstance(element, INode):
            return element
        else:
            raise ValueError(f"Element {element.id} is not a valid node: {type(element)}")

    @property
    def process_id(self) -> Optional[str]:
        """
        Get the process ID associated with the node.
        """
        return self.process.id if self.process else None

    async def validate(self, item: IItem) -> None:
        """
        Validate the node before execution.
        """
        validate_results = await self.do_event(item, ExecutionEvent.node_validate, item.status)
        for ret_val in validate_results:
            if isinstance(ret_val, dict) and "error" in ret_val:
                item.token.execution.error(f"Validation failed with error: {ret_val['error']}")

    @tracer.start_as_current_span("node.do_event")
    async def do_event(
        self,
        item: IItem,
        event: ExecutionEvent,
        new_status: Optional[ItemStatus] = None,
        event_details: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        Executes the event for the given item.

        It also updates its status, executes associated scripts, and processes any escalations or errors.

        This function triggers the execution logic for the event and returns the results of all executed
        scripts and processes.

        Args:
            item: The item instance on which the event will be executed. It encapsulates the current context and state
                for the execution.
            event: The event that is being executed. Defines the type of event being processed
                and the associated context.
            new_status: The optional new status to set for the item during the event execution. If not provided,
                the item's status remains unchanged.
            event_details: A dictionary containing additional details related to the event execution. If not provided,
                an empty dictionary will be used.

        Returns:
            A list of results from the scripts executed as part of the event processing,
            as well as the result of the item's event execution. Includes outputs such as escalation
            processing results or error handling feedback.
        """
        trace.get_current_span().set_attributes(
            {"node_name": self.name or self.id, "node_id": self.id, "event": str(event), "new_status": str(new_status)}
        )
        item.token.log(
            f"Node({self.name}|{self.id}).do_event: executing script for event: {event} new_status: {new_status}"
        )
        event_details = event_details or {}

        if new_status:
            item.status = new_status

        scripts = self.scripts.get(event, [])
        rets = []
        for script in scripts:
            item.token.log(f"--executing script for event: {event}")
            ret = item.context.script_handler.execute_script(item, script)
            rets.append(ret)

            if isinstance(ret, dict):
                if ret.get("escalation"):
                    item.token.process_escalation(ret["escalation"], item)
                if ret.get("bpmn_error"):
                    item.token.process_error(ret["bpmn_error"], item)

        ret1 = await item.token.execution.do_item_event(item, event, event_details)
        rets.append(ret1)
        item.token.log(f"Node({self.name}|{self.id}).do_event: executing script for event: {event} ended")
        return rets

    @tracer.start_as_current_span("node.set_input")
    async def set_input(self, item: IItem, input_data: Any) -> None:
        """
        Sets the input data for the item and triggers the transformation event.

        Args:
            item: The item instance on which the input will be set. It encapsulates the current context and
                state for the execution.
            input_data: The input data to be set for the item.
        """
        trace.get_current_span().set_attributes(
            {"node_name": self.name or self.id, "node_id": self.id, "input": input_data}
        )
        item.token.log(f"Node({self.name}|{self.id}).set_input: input {json.dumps(input_data, default=str)}")
        data = await self.get_input(item, input_data)
        item.token.append_data(data, item)

    @tracer.start_as_current_span("node.get_input")
    async def get_input(self, item: IItem, input_data: Any) -> Any:
        """
        Retrieves the input data for the item after transformation.

        Args:
            item: The item instance for which the input will be retrieved. It encapsulates the current context and
                state for the execution.
            input_data: The input data to be transformed and retrieved for the item.

        Returns:
            Any: The transformed input data for the item.
        """
        trace.get_current_span().set_attributes(
            {"node_name": self.name or self.id, "node_id": self.id, "input": input_data}
        )
        item.token.log(f"Node({self.name}|{self.id}).get_input: input {json.dumps(input_data, default=str)}")
        item.input = input_data
        await self.do_event(item, ExecutionEvent.transform_input, None)
        return item.input

    async def get_output(self, item: IItem) -> Any:
        """
        Retrieves the output data for the item after transformation.

        Args:
            item: The item instance for which the output will be retrieved. It encapsulates the current context and
                state for the execution.

        Returns:
            The transformed output data for the item.
        """
        return item.output

    @tracer.start_as_current_span("node.enter")
    def enter(self, item: IItem) -> None:
        """
        Enters the node and logs the event.

        Args:
            item: The item instance entering the node. It encapsulates the current context and state for the execution.
        """
        trace.get_current_span().set_attributes(
            {"node_name": self.name or self.id, "node_id": self.id, "item_id": item.id}
        )
        item.token.log(f"Node({self.name}|{self.id}).enter: item={item.id}")
        item.started_at = datetime.now()

    @property
    def requires_wait(self) -> bool:
        """
        Indicates whether the node requires waiting for completion before proceeding.

        Returns:
            True if the node requires waiting, False otherwise.
        """
        return False

    @property
    def can_be_invoked(self) -> bool:
        """
        Indicates whether the node can be invoked for execution.

        Returns:
            True if the node can be invoked, False otherwise.
        """
        return False

    @property
    def loop_definition(self) -> Optional[ILoopBehavior]:
        """
        Retrieves the loop definition associated with the node.

        Returns:
            The loop behavior if defined, None otherwise.
        """
        from pybpmn_server.elements.interfaces import ILoopBehavior

        result = self.get_behaviour(BehaviorName.LoopCharacteristics)
        return result if isinstance(result, ILoopBehavior) else None

    @property
    def is_catching(self) -> bool:
        """
        Indicates whether the node is catching events.

        Returns:
            True if the node is catching events, False otherwise.
        """
        return False

    @tracer.start_as_current_span("node.execute")
    async def execute(self, item: IItem) -> Optional[NodeAction]:
        """
        Executes the node's behavior and logs the execution details.

        Args:
            item: The item instance for which the node is being executed. It encapsulates the current context and
                state for the execution.

        Returns:
            The action to be taken after execution, or None if no action is required.
        """
        trace.get_current_span().set_attributes(
            {"node_name": self.name or self.id, "node_id": self.id, "item_id": item.id, "token_id": item.token.id}
        )
        item.token.log(f"Node({self.name}|{self.id}).execute: item={item.id} token:{item.token.id} execute enter ...")

        await self.do_event(item, ExecutionEvent.node_enter, ItemStatus.enter)
        self.enter(item)

        behaviours = list(self.behaviours.values())
        for b in behaviours:
            await b.enter(item)

        logger.debug(f'{{"seq":{item.seq},"type":\'{self.type}\',"id":\'{self.id}\',"action":\'Started\'}}')
        item.token.log(f"Node({self.name}|{self.id}).execute: execute start ...")

        await self.do_event(item, ExecutionEvent.node_start, ItemStatus.start)

        ret = await self.start(item)
        item.token.log(f"Node({self.name}|{self.id}).execute: start complete ...token:{item.token.id} ret:{ret}")

        for b in behaviours:
            b_ret = await b.start(item)
            if b_ret and isinstance(b_ret, (int, NodeAction)) and b_ret > ret:
                ret = b_ret

        if ret in (NodeAction.ERROR, NodeAction.ABORT):
            logger.debug(f'{{"seq":{item.seq},"type":\'{self.type}\',"id":\'{self.id}\',"action":\'Aborted\'}}')
            item.token.log(f"Node({self.name}|{self.id}).execute: start complete ...token:{item.token.id} ret:{ret}")
            return ret
        elif ret == NodeAction.WAIT:
            await self.do_event(item, ExecutionEvent.node_wait, ItemStatus.wait)
            item.token.info(f'{{"seq":{item.seq},"type":\'{self.type}\',"id":\'{self.id}\',"action":\'Waiting\'}}')
            item.token.log(f"Node({self.name}|{self.id}).execute: start complete ...token:{item.token.id} ret:{ret}")
            return ret
        elif ret == NodeAction.END:
            await self.do_event(item, ExecutionEvent.node_end, ItemStatus.end)
            item.token.info(f'{{"seq":{item.seq},"type":\'{self.type}\',"id":\'{self.id}\',"action":\'Ended\'}}')
            item.token.log(f"Node({self.name}|{self.id}).execute: start complete ...token:{item.token.id} ret:{ret}")
            return ret

        await item.token.execution.save()

        item.token.log(f"Node({self.name}|{self.id}).execute: execute run ...token:{item.token.id}")
        ret = await self.run(item)
        if ret in (NodeAction.ERROR, NodeAction.ABORT):
            item.token.log(f"Node({self.name}|{self.id}).execute: start complete ...token:{item.token.id} ret:{ret}")
            return ret

        ret2 = await self.continue_(item)
        item.token.log(f"Node({self.name}|{self.id}).execute: execute continue...")
        return ret2

    @tracer.start_as_current_span("node.continue")
    async def continue_(self, item: IItem) -> Optional[NodeAction]:
        """
        Continues the execution of the node and logs the continuation details.

        Args:
            item: The item instance for which the node continuation is being executed. It encapsulates the
                current context and state for the execution.

        Returns:
            The action to be taken after continuation, or None if no action is required.
        """
        trace.get_current_span().set_attributes(
            {"node_name": self.name or self.id, "node_id": self.id, "item_id": item.id}
        )
        item.token.log(f"Node({self.name}|{self.id}).continue_: item={item.id}")
        await self.end(item)
        return None

    @tracer.start_as_current_span("node.start")
    async def start(self, item: IItem) -> NodeAction:
        """
        Starts the execution of the node and logs the start details.

        Args:
            item: The item instance for which the node start is being executed. It encapsulates the
                current context and state for the execution.

        Returns:
            The action to be taken after start, or None if no action is required.
        """
        trace.get_current_span().set_attributes(
            {"node_name": self.name or self.id, "node_id": self.id, "item_id": item.id}
        )
        item.token.log(f"Node({self.name}|{self.id}).start: item={item.id}")
        await self.start_boundary_events(item, item.token)
        return NodeAction.WAIT if self.requires_wait else NodeAction.CONTINUE

    @tracer.start_as_current_span("node.run")
    async def run(self, item: IItem) -> NodeAction:
        """
        Runs the node's behavior and logs the execution details.

        Args:
            item: The item instance for which the node run is being executed. It encapsulates the
                current context and state for the execution.

        Returns:
            The action to be taken after run, or None if no action is required.
        """
        trace.get_current_span().set_attributes(
            {"node_name": self.name or self.id, "node_id": self.id, "item_id": item.id}
        )
        item.token.log(f"Node({self.name}|{self.id}).run: item={item.id}")
        return NodeAction.END

    async def cancel_ebg(self, item: IItem) -> None:
        """
        Cancels all branched instances of an Event-Based Gateway (EBG) associated with the origin item.

        Args:
            item: The item instance for which the EBG cancellation is being executed. It encapsulates the
                current context and state for the execution.
        """
        origin_item = item.token.origin_item
        if origin_item and origin_item.node.type == BpmnType.EventBasedGateway:
            # We need to cast it or just call if it exists
            ebg = origin_item.node
            if hasattr(ebg, "cancel_all_branched"):
                await ebg.cancel_all_branched(item)

    @tracer.start_as_current_span("node.cancel_boundary_events")
    async def cancel_boundary_events(self, item: IItem) -> None:
        """
        Cancels all boundary events attached to the node for the given item.

        Args:
            item: The item instance for which the boundary event cancellation is being executed. It encapsulates the
                current context and state for the execution.
        """
        for boundary_event in self.attachments:
            with tracer.start_as_current_span(
                "node.cancel_boundary_event", attributes={"boundary_event_id": boundary_event.id}
            ):
                item.token.log(f"        cancel_boundary_event:{boundary_event.id}")
                children_tokens = []
                if self.type in (BpmnType.SubProcess, BpmnType.AdHocSubProcess, BpmnType.Transaction):
                    for tok in item.token.execution.tokens.values():
                        if tok.origin_item and tok.origin_item.id == item.id and tok.type == TokenType.SubProcess:
                            children_tokens = tok.get_children_tokens()
                else:
                    children_tokens = item.token.get_children_tokens()

                if children_tokens:
                    for token in children_tokens:
                        if token.first_item:
                            with tracer.start_as_current_span(
                                "node.cancel_boundary_event_child", attributes={"token_id": token.id}
                            ):
                                item.token.log(
                                    f"     cancel_boundary_events childToken:{token.id} "
                                    f"startnode:{token.start_node_id} status:{token.first_item.status}"
                                )
                                if (
                                    token.start_node_id == boundary_event.id
                                    and token.first_item.status != ItemStatus.end
                                ):
                                    await token.terminate()

    def get_boundary_event_items(self, item: IItem) -> List[IItem]:
        """
        Retrieves the boundary event items associated with the node for the given item.

        Args:
            item: The item instance for which the boundary event items are being retrieved. It encapsulates the
                current context and state for the execution.

        Returns:
            A list of boundary event items associated with the node.
        """
        boundary_items = []
        for boundary_event in self.attachments:
            item.token.log(f"        boundary_event:{boundary_event.id}")
            children_tokens = []
            if self.type in (BpmnType.SubProcess, BpmnType.AdHocSubProcess, BpmnType.Transaction):
                for tok in item.token.execution.tokens.values():
                    if tok.origin_item and tok.origin_item.id == item.id and tok.type == TokenType.SubProcess:
                        children_tokens = tok.get_children_tokens()
            else:
                children_tokens = item.token.get_children_tokens()

            if children_tokens:
                for token in children_tokens:
                    item.token.log(
                        f"     childToken:{token.id} startnode:{token.start_node_id} "
                        f"status:{token.current_item.status if token.current_item else 'None'}"
                    )
                    if token.start_node_id == boundary_event.id and token.current_item:
                        boundary_items.append(token.current_item)
        return boundary_items

    @tracer.start_as_current_span("node.end")
    async def end(self, item: IItem, cancel: bool = False) -> None:
        """
        Handles the completion process of an item in the current node.

        The process flow varies depending on the `cancel` flag and also includes logging, status updates, and
        event processing. If the item is not valid or is already completed, the method exits early. Sequentially,
        it updates logs, processes behaviors, fires events, cancels boundary events, and executes outbound
        message flows.

        Args:
            item: The item to be marked as ended. Must be an instance of the expected item type.
            cancel: Indicates whether to cancel the item (True) or to end it normally (False). Defaults to False.
        """
        if not item or item.status == ItemStatus.end:
            return

        action = "Cancelled" if cancel else "Ended"
        item.token.info(f'{{"seq":{item.seq},"type":\'{self.type}\',"id":\'{self.id}\',"action":\'{action}\'}}')
        item.token.log(
            f"Node({self.name}|{self.id}|{item.seq}).end: item={item.id} cancel:{cancel} "
            f"attachments:{len(self.attachments)}"
        )
        trace.get_current_span().set_attributes(
            {
                "node_name": self.name or self.id,
                "node_id": self.id,
                "item_id": item.id,
                "item_sequence": item.seq,
                "action": action,
            }
        )
        for b in self.behaviours.values():
            await b.end(item)

        await self.do_event(item, ExecutionEvent.node_end, ItemStatus.end, {"cancel": cancel})
        item.token.log(
            f"Node({self.name}|{self.id}).end: setting item status to end itemId={item.id} "
            f"itemStatus={item.status} cancel: {cancel}"
        )

        for b in self.behaviours.values():
            await b.exit(item)

        item.token.log(f"Node({self.name}|{self.id}).end: finished")
        await self.cancel_boundary_events(item)

        if not cancel:
            await self.cancel_ebg(item)

        for flow in self.outbounds:
            if flow.type == BpmnType.MessageFlow:
                from ..engine.item import Item as ItemClass

                flow_item = ItemClass(flow, item.token)
                await flow.execute(flow_item)

        item.status = ItemStatus.end
        item.ended_at = None if cancel else datetime.now()
        item.token.log(f"Node({self.name}|{self.id}).end: ended item={item.id}")

    def resume(self, item: IItem) -> None:
        """
        Resumes the processing of a given item.

        This method is used to resume operations or tasks that are associated with the provided item.

        Args:
            item: The item to process or operate on.
        """
        pass

    def init(self, item: IItem) -> None:
        """
        Initializes the processing of a given item.

        This method is used to set up the initial state or configuration for the provided item.

        Args:
            item: The item to process or operate on.
        """
        pass

    async def get_outbounds(self, item: IItem) -> List[IItem]:
        """
        Retrieves the outbound items for the given item.

        Args:
            item: The item for which outbound items are to be retrieved.

        Returns:
            A list of outbound items associated with the given item.
        """
        from pybpmn_server.engine.item import Item as ItemClass

        item.token.log(f"Node({self.name}|{self.id}).get_outbounds: itemId={item.id}")
        outbounds: List[IItem] = []
        logger.debug(f"Getting outbounds for itemId={item.id} this node {self.id}")
        for flow in self.outbounds:
            logger.debug(f" ##### {flow.type}")
            if flow.type != BpmnType.MessageFlow:
                flow_item = ItemClass(flow, item.token)
                if await flow.run(flow_item) == FlowAction.take:
                    outbounds.append(flow_item)
                else:
                    flow_item.token = None

        item.token.log(f"Node({self.name}|{self.id}).get_outbounds: return outbounds={len(outbounds)}")
        return outbounds

    async def start_boundary_events(self, item: IItem, token: IToken) -> None:
        """
        Starts the boundary events for the given item.

        Args:
            item: The item for which boundary events are to be started.
            token: The token associated with the item.
        """
        from ..engine.token import Token as TokenClass
        from ..engine.token import TokenType

        for event in self.attachments:
            if event.sub_type != NodeSubtype.compensate:
                await TokenClass.start_new_token(
                    TokenType.BoundaryEvent, item.token.execution, event, None, token, item, None
                )
