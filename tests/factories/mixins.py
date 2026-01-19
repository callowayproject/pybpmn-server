"""Factory mixins for common token testing scenarios."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from pybpmn_server.interfaces.enums import TokenStatus, TokenType

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IItem
    from tests.factories.token_factory import TokenFactory


from tests.factories.token_factory import TokenFactory


class RunningTokenMixin:
    """Mixin for creating tokens in running state."""

    status: TokenStatus = TokenStatus.running


class WaitingTokenMixin:
    """Mixin for creating tokens in wait state."""

    status: TokenStatus = TokenStatus.wait


class CompletedTokenMixin:
    """Mixin for creating completed tokens with execution path."""

    status: TokenStatus = TokenStatus.end

    @classmethod
    def build_path(cls) -> List[IItem]:
        """Generate a completed execution path."""
        from tests.factories import ItemFactory

        return [
            ItemFactory.build(element_id="start_1", element_type="bpmn:StartEvent"),
            ItemFactory.build(element_id="task_1", element_type="bpmn:UserTask"),
            ItemFactory.build(element_id="end_1", element_type="bpmn:EndEvent"),
        ]


class TerminatedTokenMixin:
    """Mixin for creating terminated tokens."""

    status: TokenStatus = TokenStatus.terminated


class PrimaryTokenMixin:
    """Mixin for primary execution tokens."""

    type: TokenType = TokenType.Primary


class SubProcessTokenMixin:
    """Mixin for subprocess tokens."""

    type: TokenType = TokenType.SubProcess


class InstanceTokenMixin:
    """Mixin for multi-instance tokens."""

    type: TokenType = TokenType.Instance


class DivergeTokenMixin:
    """Mixin for diverging token paths."""

    type: TokenType = TokenType.Diverge


class EventSubProcessTokenMixin:
    """Mixin for event subprocess tokens."""

    type: TokenType = TokenType.EventSubProcess


class RunningPrimaryTokenFactory(RunningTokenMixin, PrimaryTokenMixin, TokenFactory):
    """Factory for running primary tokens."""

    pass


class WaitingPrimaryTokenFactory(WaitingTokenMixin, PrimaryTokenMixin, TokenFactory):
    """Factory for waiting primary tokens."""

    pass


class CompletedPrimaryTokenFactory(CompletedTokenMixin, PrimaryTokenMixin, TokenFactory):
    """Factory for completed primary tokens."""

    pass


class SubProcessTokenFactory(SubProcessTokenMixin, WaitingTokenMixin, TokenFactory):
    """Factory for subprocess tokens (typically wait for children)."""

    pass


class MultiInstanceTokenFactory(InstanceTokenMixin, RunningTokenMixin, TokenFactory):
    """Factory for multi-instance tokens."""

    pass
