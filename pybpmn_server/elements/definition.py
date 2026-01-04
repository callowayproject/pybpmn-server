"""Definition implementation for BPMN."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TypeAlias

from pybpmn_parser.bpmn.activities.sub_process import SubProcess as SubProcessDefinition
from pybpmn_parser.bpmn.activities.sub_process import Transaction as TransactionDefinition
from pybpmn_parser.bpmn.process.process import Process as ProcessDefinition
from pybpmn_parser.parse import Parser, ParseResult
from pymitter import EventEmitter

from pybpmn_server.elements.flow import Flow
from pybpmn_server.elements.interfaces import IDefinition, INode
from pybpmn_server.elements.node_loader import populate_non_process_nodes, populate_process_nodes
from pybpmn_server.elements.process import Process
from pybpmn_server.interfaces.enums import ExecutionEvent

logger = logging.getLogger(__name__)
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
        self.flows: List[Flow] = []
        self.access_rules: List[Any] = []
        self.parser: Parser = Parser()
        self.parse_result: Optional[ParseResult] = None

    async def load(self) -> Any:
        """Load definition from source."""
        if not self.source:
            self.parse_result = None
            return self.parse_result

        parse_result = self.parser.parse_string(self.source)

        try:
            # Follow TS logic: rootElements -> processes
            for process in parse_result.definition.processes:
                proc = self.load_process(process, None)
                proc.name = self.name
                self.processes[process.id] = proc

            # Handle references (SequenceFlows, BoundaryEvents)
            # This is complex in TS because bpmn-moddle handles refs.
            # Here we need to manually link them.
            self._link_references()

            event = ExecutionEvent.process_loaded
            await self.listener.emit_async(event, {"event": event, "context": self})

            self.parse_result = parse_result
            return parse_result.definition
        except Exception as exc:
            logger.error(f"Error in loading definition for {self.name}: {exc}")
            raise exc

    def load_process(self, process_element: Processable, parent_process: Optional[Process]) -> Process:
        """Load process definition."""
        process = Process(process_element, parent_process)

        # TODO (pybpmn-server-bgb): Process extension elements. Especially execution and task listeners
        # if process_element.extension_elements:
        #     for ext in process_element.extension_elements.process_element.extension_elements.values():
        #         if ext.get("event"):
        #             scripts = [c.get("$body") for c in ext.get("$children", []) if c.get("$body")]
        #             process.scripts[ext["event"]] = scripts

        event_sub_processes = []
        children: list[INode] = populate_non_process_nodes(process)

        for node in populate_process_nodes(process):
            node.child_process = self.load_process(node.def_, process)
            if getattr(node.def_, "triggered_by_event", False):
                event_sub_processes.append(node.child_process)

            self.nodes[process_element.id] = node
            children.append(node)

        process.init(children, event_sub_processes)

        # Lanes
        for ls in getattr(process_element, "lane_sets", []):
            for lane in ls.lanes:
                for fnr in lane.flow_node_refs:
                    if target := self.nodes.get(fnr.id):
                        target.lane = lane.name

        return process

    def _link_references(self) -> None:
        """Link references to other nodes."""
        # TODO (pybpmn-server-f77): re-implement this method using pybpmn-parser
        # In a real parser, this would be handled.
        # Here we need to find SequenceFlows and link them to nodes.
        if not self.parse_result:
            return

        for el in self.parse_result.elements_by_id.values():
            if not el:
                continue
            if el["$type"] == "bpmn:SequenceFlow":
                from_id = el.get("sourceRef")
                to_id = el.get("targetRef")
                if from_id and to_id:
                    from_node = self.nodes.get(from_id)
                    to_node = self.nodes.get(to_id)
                    if from_node and to_node:
                        flow = Flow(el["$type"], el, el["id"], from_node, to_node)
                        self.flows.append(flow)
                        from_node.outbounds.append(flow)
                        to_node.inbounds.append(flow)

            elif el["$type"] == "bpmn:BoundaryEvent":
                attached_to_id = el.get("attachedToRef")
                if attached_to_id:
                    event = self.nodes.get(el["id"])
                    owner = self.nodes.get(attached_to_id)
                    if event and owner:
                        event.attached_to = owner
                        owner.attachments.append(event)

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

    def get_node_by_id(self, id_: str) -> Optional[Any]:
        """
        Retrieves the node by its id.
        """
        return self.nodes.get(id_)
