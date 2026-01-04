"""Behavior for form."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pybpmn_server.elements.behaviors.behavior import Behavior

if TYPE_CHECKING:
    from pybpmn_server.elements.interfaces import INode
    from pybpmn_server.engine.interfaces import IItem

logger = logging.getLogger(__name__)


class IOParameter:
    """Represents an input/output parameter in a BPMN process."""

    def __init__(self, io_object: Dict[str, Any]):
        self.type: str = io_object.get("$type", "")
        self.name: str = io_object.get("name", "")
        self.sub_type: Optional[str] = None
        self.value: Any = None

        if io_object.get("$body"):
            self.value = io_object["$body"]
        elif io_object.get("$children"):
            details = io_object["$children"]
            for detail in details:
                self.sub_type = detail.get("$type")
                if self.sub_type == "camunda:list":
                    if detail.get("$children"):
                        self.value = []
                        for entry in detail["$children"]:
                            self.value.append(entry.get("$body"))
                elif self.sub_type == "camunda:map":
                    if detail.get("$children"):
                        self.value = {}
                        for entry in detail["$children"]:
                            self.value[entry.get("key")] = entry.get("$body")
                elif self.sub_type == "camunda:script":
                    self.value = detail.get("$body")
                else:
                    self.value = detail.get("$children")

    def is_input(self) -> bool:
        """Indicates if the parameter is an input parameter."""
        return self.type == "camunda:inputParameter"

    def is_output(self) -> bool:
        """Indicates if the parameter is an output parameter."""
        return self.type == "camunda:outputParameter"

    async def evaluate(self, item: IItem) -> Any:
        """Evaluates the parameter value based on its type and returns the result."""
        val = None
        if self.sub_type == "camunda:text":
            val = self.value
        elif self.sub_type == "camunda:list":
            val = []
            for entry in self.value:
                eval_value = item.context.script_handler.evaluate_expression(item, entry)
                val.append(eval_value)
        elif self.sub_type == "camunda:map":
            val = {}
            for key, value in self.value.items():
                eval_value = item.context.script_handler.evaluate_expression(item, value)
                val[key] = eval_value
        elif self.sub_type == "camunda:script":
            val = item.context.script_handler.evaluate_expression(item, self.value)
        else:
            if isinstance(self.value, str) and self.value.startswith("$"):
                val = item.context.script_handler.evaluate_expression(item, self.value[1:])
            else:
                val = self.value
        return val


class IOBehavior(Behavior):
    """
    Behavior for handling input/output parameters in BPMN elements.
    """

    def __init__(self, node: INode, definition: Any):
        super().__init__(node, definition)
        self.parameters: List[IOParameter] = []

    def init(self) -> None:
        """
        Initialize the input/output parameters based on the provided definition.
        """
        ios = self.definition.get("$children", [])
        for io in ios:
            self.parameters.append(IOParameter(io))

    async def enter(self, item: IItem) -> None:
        """
        Handles the input/output parameters at the start of an item's execution.
        """
        has_input = False
        for param in self.parameters:
            if param.is_input():
                has_input = True
                val = await param.evaluate(item)
                item.input[param.name] = val
                logging.info(f"...set at enter data input : input.{param.name} = {val}")

        if not has_input:
            for param in self.parameters:
                if param.is_output():
                    val = item.context.script_handler.evaluate_expression(item, param.value)
                    item.output[param.name] = val
                    logging.info(f"...set at enter data output : output.{param.name} = {val}")

    async def exit(self, item: IItem) -> None:
        """
        Handles the input/output parameters at the end of an item's execution.
        """
        for param in self.parameters:
            if param.is_output():
                if param.value is not None and param.value:
                    val = item.context.script_handler.evaluate_expression(item, param.value)
                    logger.info(f"...set at exit data output : data.{param.name} = {val}")
                    item.token.data[param.name] = val
                else:
                    item.token.data[param.name] = item.output
                    logger.info(f"...set at exit data output : data.{param.name} = {item.output}")
