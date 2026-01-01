"""Behavior for script execution in BPMN elements."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from pybpmn_server.elements.behaviors.behavior import Behavior

if TYPE_CHECKING:
    from pybpmn_parser.bpmn.common.flow_element import FlowElement

    from pybpmn_server.elements.interfaces import INode


class ScriptBehavior(Behavior):
    """
    Behavior for executing scripts in BPMN elements.
    """

    def __init__(self, node: INode, definition: FlowElement):
        super().__init__(node, definition)
        self.scripts: List[str] = []

    def init(self) -> None:
        """
        Initializes the behavior for script execution in BPMN elements.
        """
        scrs = self.definition.get("$children", [])
        for scr in scrs:
            body = scr.get("$body")
            if body:
                self.scripts.append(body)

        event = self.definition.get("event")
        if event:
            if event not in self.node.scripts:
                self.node.scripts[event] = []
            self.node.scripts[event].extend(self.scripts)
