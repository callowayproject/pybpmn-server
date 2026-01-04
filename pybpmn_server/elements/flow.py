"""Flow element representing a connection between nodes in a BPMN process."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pybpmn_server.elements.interfaces import IFlow, INode
from pybpmn_server.interfaces.enums import ExecutionEvent, FlowAction, TokenType

if TYPE_CHECKING:
    from pybpmn_parser.bpmn.foundation.base_element import BaseElement

    from pybpmn_server.engine.interfaces import IItem

    from .node import Node


class Flow(IFlow):
    """Flow element representing a connection between nodes in a BPMN process."""

    def __init__(self, type_: str, def_: type[BaseElement], id_: str, from_node: INode, to_node: INode):
        super().__init__(type_, def_, id_, from_node, to_node)
        self.name: str = getattr(def_, "name", "")
        self.is_flow = True
        self.is_message_flow = False

    async def run(self, item: IItem) -> str:
        """Execute the flow action based on the condition evaluation."""
        item.token.log(
            f"Flow({self.name}|{self.id}).run: from={self.from_node.name} to={self.to_node.name} find action..."
        )
        action = "take"  # FLOW_ACTION.take
        result = await self.evaluate_condition(item)
        if not result:
            action = FlowAction.discard
            await item.token.execution.do_item_event(item, ExecutionEvent.flow_discard, {"flow": self.id})
        else:
            await item.token.execution.do_item_event(item, ExecutionEvent.flow_take, {"flow": self.id})
            item.token.info(f'{{"seq":{item.seq},"type":\'{self.type}\',"id":\'{self.id}\',"action":\'Taken\'}}')
            item.token.log(
                f"(Flow:{self.id})Flow({self.name}|{self.id}).run: going to {self.to_node.id} action : {action}"
            )

        return action

    async def end(self, item: IItem) -> None:
        """End the flow action, typically used for cleanup or finalization."""
        pass

    async def evaluate_condition(self, item: IItem) -> bool:
        """Evaluate the flow condition based on the condition evaluation."""
        if hasattr(self.def_, "conditionExpression") and self.def_.conditionExpression:
            expression = getattr(self.def_.conditionExpression, "body", "")
            item.token.log(f"..conditionExpression:{json.dumps(expression, default=str)}")
            item.token.log(json.dumps(item.token.data, default=str))
            result = await item.context.script_handler.evaluate_expression(item, expression)
            item.token.log(f"..conditionExpression:{expression} result: {result}")
            return bool(result)
        return True

    async def execute(self, item: IItem) -> None:
        """Execute the flow action based on the condition evaluation."""
        pass


class MessageFlow(Flow):
    """Message flow element representing a connection between nodes in a BPMN process for message passing."""

    def __init__(self, id_: str, type_: str, from_node: Node, to_node: Node, def_: Any):
        super().__init__(type_, def_, id_, from_node, to_node)
        self.is_message_flow = True

    async def execute(self, item: IItem) -> None:
        """Execute the flow action based on the condition evaluation."""
        item.token.log(f"..MessageFlow -{self.id} going to {self.to_node.id}")

        execution = item.token.execution
        token = None

        for t in execution.tokens.values():
            if t.current_node and t.current_node.id == self.to_node.id:
                token = t
                break

        if token:
            item.token.log(f"    signalling token:{token.id}")
            # In TS: execution.promises.push(token.signal(null));
            # In Python, we might need to handle this differently if we want parallel execution
            # For now, let's just await it if we are already in an async context
            await token.signal(None)
        else:
            item.token.log("    signalling new token:")
            from pybpmn_server.engine.token import Token

            await Token.start_new_token(TokenType.Primary, execution, self.to_node, None, None, None, None)
