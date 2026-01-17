"""Definition implementation for BPMN."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TypeAlias

from opentelemetry import trace
from pybpmn_parser.bpmn.activities.sub_process import SubProcess as SubProcessDefinition
from pybpmn_parser.bpmn.activities.sub_process import Transaction as TransactionDefinition
from pybpmn_parser.bpmn.process.process import Process as ProcessDefinition
from pybpmn_parser.parse import Parser, ParseResult, Reference
from pymitter import EventEmitter

from pybpmn_server.elements.flow import Flow, MessageFlow
from pybpmn_server.elements.interfaces import IDefinition, IFlow, INode
from pybpmn_server.elements.node_loader import populate_non_process_nodes, populate_process_nodes
from pybpmn_server.elements.process import Process
from pybpmn_server.interfaces.enums import ExecutionEvent

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)
Processable: TypeAlias = ProcessDefinition | SubProcessDefinition | TransactionDefinition


class Definition(IDefinition):
    """Behavioral model for BPMN."""

    def __init__(self, name: str, source: str):
        self.elements_by_id: dict[str, Any] = {}
        self.listener = EventEmitter()
        self.name = name
        self.source = source
        self.processes: Dict[str, Process] = {}
        self.nodes: Dict[str, Any] = {}
        self.flows: List[IFlow] = []
        self.access_rules: List[Any] = []
        self.parser: Parser = Parser()
        self.parse_result: Optional[ParseResult] = None

    @tracer.start_as_current_span("definition.load")
    async def load(self) -> Any:
        """Load definition from source."""
        if not self.source:
            self.parse_result = None
            return self.parse_result

        self.parse_result = self.parser.parse_string(self.source)

        try:
            # Follow TS logic: rootElements -> processes
            for process in self.parse_result.definition.processes:
                proc = self.load_process(process, None)
                proc.name = self.name
                self.processes[process.id] = proc

            self._link_references()
            event = ExecutionEvent.process_loaded
            await self.listener.emit_async(event, {"event": event, "context": self})

            return self.parse_result.definition
        except Exception as exc:
            logger.error(f"Error in loading definition for {self.name}: {exc}")
            raise exc

    @tracer.start_as_current_span("definition.load_process")
    def load_process(self, process_element: Processable, parent_process: Optional[Process]) -> Process:
        """Load process definition."""
        process = Process(process_element, parent_process)

        event_sub_processes = []
        children: list[INode] = populate_non_process_nodes(process)

        for child in children:
            self.nodes[child.id] = child

        for node in populate_process_nodes(process):
            node.child_process = self.load_process(node.def_, process)
            if getattr(node.def_, "triggered_by_event", False):
                event_sub_processes.append(node.child_process)

            self.nodes[node.id] = node
            children.append(node)

        process.init(children, event_sub_processes)

        # Lanes
        for ls in getattr(process_element, "lane_sets", []):
            for lane in ls.lanes:
                for fnr in lane.flow_node_refs:
                    if target := self.nodes.get(fnr.id):
                        target.lane = lane.name

        return process

    def get_node_by_id(self, node_id: str) -> Optional[INode]:
        """
        Retrieve a node by its unique identifier.

        Args:
            node_id: The unique identifier of the node to retrieve.

        Returns:
            Optional[INode]: The node with the specified ID, or None if not found.

        Raises:
            ValueError: If the node does not exist.
        """
        if node := self.nodes.get(node_id):
            return node
        else:
            raise ValueError(f"Node {node_id} does not exist in {', '.join(self.nodes.keys())}.")

    def _link_references(self) -> None:
        """Link references to other nodes."""
        if not self.parse_result:
            raise ValueError("Parse result is None.")

        flow_references: dict[str, dict[str, Any]] = {}
        """Contains partial references to sequence flows. It takes two references to complete: a from and a to."""

        for ref in self.parse_result.references:
            if ref.element_id is None:
                continue
            element = self.parse_result.elements_by_id[ref.element_id]
            element_type = element.Meta.name if hasattr(element, "Meta") else "unknown"

            if element_type == "sequenceFlow":
                ref_element = self.parse_result.elements_by_id[ref.reference_id]

                flow_references[ref.element_id] = update_sequence_flow(
                    flow_references, ref.element_id, ref.property, ref_element
                )
            elif element_type == "boundaryEvent" and ref.property == "attached_to_ref":
                self._link_boundary_event(ref)

        for ref in flow_references.values():
            element = self.parse_result.elements_by_id[ref["id"]]
            element_type = element.Meta.name if hasattr(element, "Meta") else "unknown"

            from_node = self.get_node_by_id(ref["from"])
            to_node = self.get_node_by_id(ref["to"])
            flow = Flow(f"bpmn:{element_type}", element, ref["id"], from_node, to_node)
            self._update_flow_nodes(flow, from_node, to_node)

        for collab in self.parse_result.definition.collaborations:
            for message_flow in collab.message_flows:
                from_node = self.get_node_by_id(message_flow.source_ref)
                to_node = self.get_node_by_id(message_flow.target_ref)

                flow = MessageFlow(message_flow.id, message_flow.Meta.name, from_node, to_node, message_flow)
                from_node.outbounds.append(flow)
                to_node.inbounds.append(flow)

    def _link_boundary_event(self, ref: Reference) -> None:
        """
        Links a boundary event to its owner node.
        """
        event = self.get_node_by_id(ref.element_id)
        owner = self.get_node_by_id(ref.reference_id)

        owner.attachments.append(event)

        if event.attached_to is None:
            event.attached_to = owner
        else:
            logger.info(f"event already attached to {event.attached_to}")

        logger.info(f"boundary event {ref.element_id} attached to {ref.reference_id}")

    def _update_flow_nodes(self, flow: IFlow, from_node: INode, to_node: INode) -> None:
        """
        Updates the flow by adding it to the definition's flows list and linking it to the source and target nodes.
        """
        logger.info(f"Updating flow {flow.id} and linking it to {from_node.id} and {to_node.id}")
        self.flows.append(flow)
        from_node.outbounds.append(flow)
        to_node.inbounds.append(flow)

    def get_json(self) -> str:
        """
        Retrieves the JSON representation of the definition.
        """
        import json

        elements = []
        processes = [
            {
                "id": process.id,
                "name": process.name,
                "isExecutable": process.is_executable,
                "docs": getattr(process.def_, "documentation", None),
            }
            for process in self.processes.values()
        ]

        for node in self.nodes.values():
            if node.type != "bpmn:SequenceFlow":
                behaviours = [behav.describe() for behav in node.behaviours.values()]
                elements.append(
                    {
                        "id": node.id,
                        "name": node.name,
                        "type": node.type,
                        "process": node.process_id,
                        "def": node.def_,
                        "description": node.describe(),
                        "behaviors": behaviours,
                        "docs": getattr(node.def_, "documentation", None),
                    }
                )

        flows = [
            {
                "id": flow.id,
                "name": flow.name,
                "from": flow.from_node.id,
                "to": flow.to_node.id,
                "type": flow.type,
            }
            for flow in self.flows
        ]

        return json.dumps({"processes": processes, "elements": elements, "flows": flows})

    def get_start_nodes(self, user_invokable: bool = False) -> List[Any]:
        """
        Retrieves the start nodes for all processes within the definition, considering user-invokable start events.
        """
        starts = []
        for proc in self.processes.values():
            starts.extend(proc.get_start_nodes(user_invokable))
        return starts

    def get_start_node(self) -> Optional[Any]:
        """
        Retrieves the start node for the definition, considering user-invokable start events.
        """
        nodes = self.get_start_nodes()
        return nodes[0] if nodes else None


def update_sequence_flow(
    flow_map: dict[str, Any], element_id: str, property_name: str, ref_element: Any
) -> dict[str, str]:
    """
    Updates or creates a new flow record.

    A sequence flow record requires two touches: setting the source and target nodes.

    Args:
        flow_map: The dictionary mapping flow IDs to flow details
        element_id: The ID of the flow element
        property_name: The property name indicating the direction of the flow
        ref_element: The reference element associated with the flow

    Returns:
        The updated flow record.
    """
    default_flow = {"id": element_id, "from": None, "to": None}
    flow = flow_map.get(element_id, default_flow)
    if property_name == "source_ref":
        flow["from"] = ref_element.id
    else:
        flow["to"] = ref_element.id
    return flow
