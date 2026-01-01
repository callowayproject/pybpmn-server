"""Behavior for loop characteristics."""

from __future__ import annotations

from typing import Optional

from .behavior import Behavior


class LoopBehavior(Behavior):
    """
    Behavior for handling loop characteristics in BPMN elements.
    """

    @property
    def collection(self) -> Optional[str]:
        """
        Retrieves the collection attribute for loop characteristics.

        Returns None if not applicable or not found.
        """
        if self.is_standard:
            return None

        loop_characteristics = getattr(self.node.def_, "loopCharacteristics", None)
        if not loop_characteristics:
            return None

        collection = getattr(loop_characteristics, "collection", None)
        if collection:
            return collection

        attrs = getattr(loop_characteristics, "$attrs", {})
        return attrs.get("camunda:collection")

    @property
    def is_standard(self) -> bool:
        """
        Checks if the loop behavior is standard (non-camunda specific).

        Returns True if standard, False otherwise.
        """
        loop_characteristics = getattr(self.node.def_, "loopCharacteristics", None)
        if not loop_characteristics:
            return False
        return loop_characteristics.get("$type") == "bpmn:StandardLoopCharacteristics"

    @property
    def is_sequential(self) -> bool:
        """
        Checks if the loop behavior is sequential.

        Returns True if sequential, False otherwise.
        """
        loop_characteristics = getattr(self.node.def_, "loopCharacteristics", None)
        if not loop_characteristics:
            return False
        return getattr(loop_characteristics, "isSequential", False)
