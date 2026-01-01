"""
Behavior for form.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from pybpmn_server.elements.behaviors.behavior import Behavior

if TYPE_CHECKING:
    from pybpmn_server.elements.interfaces import INode


class CamundaFormData(Behavior):
    """
    Behavior for handling form data in a BPMN process.
    """

    def __init__(self, node: INode, definition: Any):
        super().__init__(node, definition)
        self.fields: List[Any] = []

    def init(self) -> None:
        """
        Initialize the form fields based on the provided definition.
        """
        self.fields = self.definition.get("$children", [])

    def get_fields(self) -> List[Any]:
        """
        Retrieve the list of form fields.
        """
        return self.fields
