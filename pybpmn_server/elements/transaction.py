from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, cast

from pybpmn_server.elements.tasks import SubProcess
from pybpmn_server.interfaces.enums import BpmnType, ItemStatus, NodeAction, NodeSubtype, TokenType

if TYPE_CHECKING:
    from pybpmn_parser.bpmn.activities.sub_process import Transaction as TransactionDef

    from pybpmn_server.elements.process import Process
    from pybpmn_server.engine.interfaces import IItem, IToken


class Transaction(SubProcess):
    """Transaction task implementation."""

    def __init__(self, type_: str, def_: TransactionDef, id_: str, process: Process):
        super().__init__(type_, def_, id_, process)

    @property
    def requires_wait(self) -> bool:
        """Does the transaction require waiting?"""
        return True

    async def end(self, item: IItem, cancel: bool = False) -> None:
        """End a transaction."""
        await super().end(item, cancel)

    @property
    def is_transaction(self) -> bool:
        """Is this node a transaction?"""
        return True

    @staticmethod
    async def cancel(transaction_item: IItem) -> None:
        """Cancel a transaction."""
        await Transaction.compensate(transaction_item)

    @staticmethod
    async def compensate(trans_item: IItem) -> None:
        """Compensate a transaction."""
        from pybpmn_server.engine.token import Token

        if not trans_item.node.is_transaction:
            return

        trans = cast("Transaction", trans_item.node)
        items = trans.get_items(trans_item)

        for item in items:
            if item.status != ItemStatus.end:
                continue

            events = item.node.attachments
            to_fire = [event for event in events if event.sub_type == NodeSubtype.compensate]

            for event in to_fire:
                new_token = await Token.start_new_token(
                    TokenType.BoundaryEvent, item.token.execution, event, None, item.token, item, None
                )
                await new_token.execution.signal_item(new_token.current_item.id, None)

    def get_nodes(self) -> List[Any]:
        """Get the nodes this transaction belongs to."""
        return self.child_process.children_nodes if self.child_process else []

    def get_items_for_token(self, token: IToken) -> List[IItem]:
        """Get the items this transaction belongs to."""
        items: List[IItem] = []
        for t in token.get_children_tokens():
            items.extend(it for it in t.path if it.node.type != BpmnType.SequenceFlow)
            items.extend(self.get_items_for_token(t))
        return items

    def get_items(self, item: IItem) -> List[IItem]:
        """Get the items this transaction belongs to."""
        return self.get_items_for_token(item.token)

    async def start(self, item: IItem) -> NodeAction:
        """Start a transaction."""
        return await super().start(item)
