from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pybpmn_server.elements.behaviors.behavior_loader import BehaviorName
from pybpmn_server.elements.node import Node
from pybpmn_server.interfaces.enums import ItemStatus, NodeAction, TokenStatus

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IItem


class Event(Node):
    def has_message(self) -> bool:
        return self.has_behaviour(BehaviorName.MessageEventDefinition)

    def has_signal(self) -> bool:
        return self.has_behaviour(BehaviorName.SignalEventDefinition)

    def has_timer(self) -> bool:
        return self.has_behaviour(BehaviorName.TimerEventDefinition)

    async def start(self, item: IItem) -> NodeAction:
        return await super().start(item)

    async def end(self, item: IItem, cancel: bool = False) -> None:
        await super().end(item, cancel)

    @property
    def can_be_invoked(self) -> bool:
        return True

    @staticmethod
    async def terminate(item: IItem) -> None:
        if not item.token.parent_token:
            return

        item.token.log(
            f"BoundaryEvent({item.node.id}).run: is_cancelling .. parentToken: {item.token.parent_token.id}"
        )

        if item.token.parent_token.current_item:
            item.token.parent_token.current_item.status = ItemStatus.end

        item.status = ItemStatus.end

        # check for loop:
        if item.node.attached_to and item.node.attached_to.loop_definition:
            from ..engine.loop import Loop

            await Loop.cancel(item)

        p_token = item.token.parent_token

        # In TS: if (pToken.type==TOKEN_TYPE.SubProcess && pToken.parentToken && pToken.parentToken.type==TOKEN_TYPE.Instance)
        if p_token.type == "SubProcess" and p_token.parent_token and p_token.parent_token.type == "Instance":
            await p_token.parent_token.terminate()
        else:
            await p_token.terminate()

        if (
            p_token.origin_item
            and item.node.attached_to
            and p_token.origin_item.element_id == item.node.attached_to.id
        ):
            await p_token.origin_item.node.end(p_token.origin_item, True)


class CatchEvent(Event):
    @property
    def is_catching(self) -> bool:
        return True

    @property
    def requires_wait(self) -> bool:
        return True

    @property
    def can_be_invoked(self) -> bool:
        return True

    async def start(self, item: IItem) -> NodeAction:
        return await super().start(item)


class BoundaryEvent(Event):
    def __init__(self, type_: str, def_: Any, id_: str, process: Any):
        super().__init__(type_, def_, id_, process)
        self.is_cancelling = True
        if (hasattr(self.def_, "cancelActivity") and self.def_.cancelActivity is False) or (
            isinstance(self.def_, dict) and self.def_.get("cancelActivity") is False
        ):
            self.is_cancelling = False

    @property
    def is_catching(self) -> bool:
        return True

    @property
    def requires_wait(self) -> bool:
        return True

    @property
    def can_be_invoked(self) -> bool:
        return True

    async def start(self, item: IItem) -> NodeAction:
        return await super().start(item)

    async def run(self, item: IItem) -> NodeAction:
        ret = await super().run(item)

        if self.is_cancelling:
            item.token.status = TokenStatus.terminated
            await Event.terminate(item)
            item.token.status = TokenStatus.wait
            item.token.status = TokenStatus.running

        return ret


class ThrowEvent(Event):
    @property
    def is_catching(self) -> bool:
        return False

    async def start(self, item: IItem) -> NodeAction:
        return await super().start(item)

    async def run(self, item: IItem) -> NodeAction:
        return NodeAction.END


class EndEvent(Event):
    @property
    def is_catching(self) -> bool:
        return False

    async def end(self, item: IItem, cancel: bool = False) -> None:
        sub_process_token = item.token.get_sub_process_token()
        if sub_process_token and item.status != ItemStatus.end:
            await sub_process_token.end(cancel)

        await super().end(item, cancel)


class StartEvent(Event):
    def __init__(self, type_: str, def_: Any, id_: str, process: Any):
        super().__init__(type_, def_, id_, process)
        attrs = getattr(self.def_, "$attrs", {})
        self.candidate_groups = attrs.get("camunda:candidateGroups")
        self.candidate_users = attrs.get("camunda:candidateUsers")
        self.initiator = attrs.get("camunda:initiator")

    async def start(self, item: IItem) -> NodeAction:
        if self.initiator:
            item.token.data[self.initiator] = item.user_name
        return await super().start(item)

    @property
    def is_catching(self) -> bool:
        return True
