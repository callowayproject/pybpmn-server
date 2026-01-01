"""Behavior for terminating execution in BPMN elements."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .behavior import Behavior

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IItem


class TerminateBehavior(Behavior):
    """
    Behavior for terminating execution in BPMN elements.
    """

    async def end(self, item: IItem) -> None:
        """
        Handles the end of a signal event.
        """
        for tok in item.token.execution.tokens.values():
            await tok.terminate()
