"""
Represents a Gateway node in a workflow, handling the logic for diverging and converging flows.

Gateways determine the flow of execution within a workflow based on specific rules and conditions.
They process outbound paths, evaluate potential paths, manage related tokens, and handle the
convergence of multiple flows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from opentelemetry import trace

from pybpmn_server.elements.node import Node
from pybpmn_server.interfaces.enums import BpmnType, FlowAction, ItemStatus, NodeAction, TokenStatus

if TYPE_CHECKING:
    from pybpmn_server.elements.interfaces import INode
    from pybpmn_server.engine.interfaces import IItem, IToken

tracer = trace.get_tracer(__name__)


class Gateway(Node):
    """
    Represents a Gateway node in a workflow, handling the logic for diverging and converging flows.

    Gateways determine the flow of execution within a workflow based on specific rules and conditions.
    They process outbound paths, evaluate potential paths, manage related tokens, and handle the
    convergence of multiple flows.
    """

    async def get_outbounds(self, item: IItem) -> List[IItem]:
        """
        Fetches outbound items for the given item based on the current configuration.

        This method determines the default flow and processes potential outbounds for the given item.
        If no appropriate outbound items are found, the default flow is selected as a fallback.

        Args:
            item: The item for which outbound items are to be determined.

        Returns:
            A list of outbound items determined for the given item.
        """
        from pybpmn_server.engine.item import Item as ItemClass

        default_flow_id = None
        if hasattr(self.def_, "default"):
            default_flow_id = getattr(self.def_.default, "id", None)
        elif isinstance(self.def_, dict) and "default" in self.def_:
            default_flow_id = self.def_["default"]

        if not default_flow_id:
            return await super().get_outbounds(item)
        default_flow = None
        outbounds: List[IItem] = []

        for flow in self.outbounds:
            if flow.id == default_flow_id:
                default_flow = flow
            else:
                flow_item = ItemClass(flow, item.token)
                if await flow.run(flow_item) == FlowAction.take:
                    outbounds.append(flow_item)

        if not outbounds and default_flow:
            flow_item = ItemClass(default_flow, item.token)
            outbounds.append(flow_item)

        item.token.log(f"..return outbounds {len(outbounds)}")
        return outbounds

    def get_potential_path(self, node: INode, path: Optional[Dict[str, INode]] = None) -> Dict[str, INode]:
        """
        Recursively explores potential paths from a given node, considering all outbound flows.
        """
        if path is None:
            path = {}
        for flow in node.outbounds:
            to_node = flow.to_node
            if to_node.id not in path:
                path[to_node.id] = to_node
                self.get_potential_path(to_node, path)
        return path

    def can_reach(self, node: INode, target: INode) -> bool:
        """
        Checks if a given node can reach a target node through potential paths.
        """
        if node.id == target.id:
            return True
        path = self.get_potential_path(node)
        return target.id in path

    def get_related_tokens(self, item: IItem) -> List[IToken]:
        """
        Retrieves tokens related to the current token, considering its execution context and path.
        """
        related = []
        execution = item.token.execution
        execution.log(f"Gateway.get_related_tokens: for {item.token.id}")

        for token in execution.tokens.values():
            branch = token.origin_item.element_id if token.origin_item else "root"
            parent = token.parent_token.id if token.parent_token else "-"
            p = "->".join([it.node.id for it in token.path])
            execution.log(
                f"        ..token: {token.id} - {token.status} - {token.type} current: "
                f"{token.current_node.id if token.current_node else 'None'} from {branch} child of {parent} path: {p}"
            )

            if token.current_item and (
                token.id != item.token.id
                and token.current_item.status
                not in (
                    ItemStatus.end,
                    ItemStatus.terminated,
                )
                and token.current_node
            ):
                can_reach = self.can_reach(token.current_node, self)
                execution.log(
                    f"            ..canReach: {can_reach} - token status: {token.status} - item status "
                    f"{token.current_item.status}"
                )
                if can_reach:
                    if (
                        token.items_key is None
                        or item.token.items_key is None
                        or (f"{item.token.items_key}.{token.items_key}").startswith(f"{token.items_key}.")
                    ):
                        related.append(token)
        for t in related:
            execution.log(f"    .. related token: {t.id} {t.status} {t.items_key}")
        return related

    def analyze_converging_tokens(self, item: IItem) -> Dict[str, List[IToken]]:
        """
        Analyzes and categorizes tokens related to the current gateway.

        It divides them into pending and waiting tokens based on their status and current node.

        Args:
            item: The item containing the token and element associated with the
                gateway. This token and the element's properties are used to determine
                the category of related tokens.

        Returns:
            A dictionary containing two lists:
                - pending_tokens: Tokens that are not on the current gateway node or have a
                  status other than "end" or "terminated".
                - waiting_tokens: Tokens that are on the current gateway node and are still
                  waiting for processing.
        """
        waiting_tokens = []
        pending_tokens = []
        token = item.token
        related = self.get_related_tokens(item)

        for t in related:
            if t.status not in (TokenStatus.end, TokenStatus.terminated):
                if t.current_node and t.current_node.id == self.id:
                    token.log(
                        f"Gateway({item.element.name}|{item.element.id}).convergeFlows: ... child token {t.id} "
                        f"in current gateway => add to waiting_tokens current_node={t.current_node.id}"
                    )
                    waiting_tokens.append(t)
                else:
                    token.log(
                        f"Gateway({item.element.name}|{item.element.id}).convergeFlows: ... adding to pending_tokens "
                        f"{t.id} node {t.current_node.id if t.current_node else 'None'} target {self.id}"
                    )
                    pending_tokens.append(t)

        for t in waiting_tokens:
            token.log(
                f"Gateway({item.element.name}|{item.element.id}).convergeFlows: ... waiting_tokens token id:{t.id} "
                f"current_node.id:{t.current_node.id if t.current_node else 'None'}"
            )

        token.log(
            f"Gateway({item.element.name}|{item.element.id}).convergeFlows: pending_tokens:{len(pending_tokens)} "
            f"waiting_tokens:{len(waiting_tokens)}"
        )

        return {"pending_tokens": pending_tokens, "waiting_tokens": waiting_tokens}

    @tracer.start_as_current_span("gateway.start")
    async def start(self, item: IItem) -> NodeAction:
        item.token.log(f"Gateway({item.element.name}|{item.element.id}).start: node.type={item.node.type}")
        if len(self.inbounds) > 1:
            item.token.log(
                f"Gateway({item.element.name}|{item.element.id}).start: Starting a converging gateway this.inbounds.length={len(self.inbounds)}"
            )

            result = self.analyze_converging_tokens(item)
            if len(result["pending_tokens"]) > 0:
                if self.type == BpmnType.ExclusiveGateway:
                    item.token.log(
                        f"Gateway({item.element.name}|{item.element.id}).start: cancel other pending_tokens.length={len(result['pending_tokens'])}"
                    )
                    for t in result["pending_tokens"]:
                        item.token.log(f"..cancel ending token #{t.id}")
                        if t.current_item:
                            t.current_item.status = ItemStatus.end
                        await t.terminate()
                else:
                    item.token.log(
                        f"Gateway({item.element.name}|{item.element.id}).start: result.pending_tokens.length = {len(result['pending_tokens'])} > 0 return NODE_ACTION.WAIT"
                    )
                    return NodeAction.WAIT
            elif item.token.type == "Diverge":  # TOKEN_TYPE
                parent_token = item.token.parent_token
                converging_gateway_current_node = item.token.current_node

                item.token.log(
                    f"Gateway({item.element.name}|{item.element.id}).start: let us converge now waiting_tokens.length={len(result['waiting_tokens'])}"
                )
                for t in result["waiting_tokens"]:
                    item.token.log(f"..converging ending token #{t.id}")
                    if t.current_item:
                        t.current_item.status = ItemStatus.end
                    await t.end()

                item.token.log(
                    f"Gateway({item.element.name}|{item.element.id}).start: converged! all waiting tokens ended"
                )

                old_current_token = item.token

                if parent_token:
                    item.token.log(
                        f"Gateway({item.element.name}|{item.element.id}).start: converged! restart the parent token from this item! parentToken={parent_token.id}"
                    )
                    parent_token.status = TokenStatus.running
                    if converging_gateway_current_node:
                        parent_token.current_node = converging_gateway_current_node
                    item.token = parent_token

                    await parent_token.current_node.run(item)
                    await parent_token.current_node.continue_(item)
                    await parent_token.go_next()

                    old_current_token.log(
                        f"Gateway({item.element.name}|{item.element.id}).start: ending current child token {old_current_token.id}"
                    )
                    if old_current_token.current_item:
                        old_current_token.current_item.status = ItemStatus.end
                    await old_current_token.terminate()

                    item.token.log(
                        f"Gateway({item.element.name}|{item.element.id}).start: all token terminate return NODE_ACTION.END"
                    )
                    return NodeAction.END
            else:
                for t in result["waiting_tokens"]:
                    item.token.log(f"..converging ending token #{t.id}")
                    if t.current_item:
                        t.current_item.status = ItemStatus.end
                    await t.end()
                return NodeAction.CONTINUE
        return NodeAction.CONTINUE


class XORGateway(Gateway):
    async def get_outbounds(self, item: IItem) -> List[IItem]:
        outbounds = await super().get_outbounds(item)
        if len(outbounds) > 1:
            item.token.log("..XORGateway : removed other outbounds , took the first")
            return [outbounds[0]]
        return outbounds


class EventBasedGateway(Gateway):
    def __init__(self, id_: str, process: Any, type_: str, def_: Any):
        super().__init__(type_, def_, id_, process)
        self.working = False

    async def restored(self, item: IItem) -> None:
        super().resume(item)

    async def run(self, item: IItem) -> NodeAction:
        return NodeAction.END

    async def cancel_all_branched(self, ending_item: IItem) -> None:
        if self.working:
            return
        self.working = True

        tokens = list(ending_item.token.execution.tokens.values())
        for token in tokens:
            is_waiting = token.status == TokenStatus.wait
            current_item_not_ending = token.current_item and token.current_item.status != ItemStatus.end
            is_origin_item = token.origin_item and token.origin_item.id == ending_item.id

            if is_waiting and current_item_not_ending and is_origin_item:
                ending_item.token.log(
                    f"..EventBasedGateway:<{self.id}>-- cancelling {token.current_node.id if token.current_node else 'None'}"
                )
                await token.terminate()

        self.working = False
