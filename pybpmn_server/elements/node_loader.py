"""This module populates the node definitions."""

from __future__ import annotations

from dataclasses import fields
from typing import TYPE_CHECKING

from pybpmn_server.elements.events import BoundaryEvent, CatchEvent, EndEvent, StartEvent, ThrowEvent
from pybpmn_server.elements.gateway import EventBasedGateway, Gateway, XORGateway
from pybpmn_server.elements.node import Node
from pybpmn_server.elements.tasks import (
    AdHocSubProcess,
    BusinessRuleTask,
    CallActivity,
    ReceiveTask,
    ScriptTask,
    SendTask,
    ServiceTask,
    SubProcess,
    UserTask,
)

from .transaction import Transaction

if TYPE_CHECKING:
    from pybpmn_server.elements.process import Process

    from .interfaces import INode


def populate_non_process_nodes(process: Process) -> list[INode]:  # NOQA: C901
    """Load all the node definitions as their appropriate elements."""
    nodes: list[INode] = []
    definition = process.def_
    field_metadata = {f.name: f.metadata for f in fields(definition)}

    for el in definition.user_tasks:
        type_ = f"bpmn:{field_metadata['user_tasks']}"
        nodes.append(UserTask(type_, el, el.id, process))

    for el in definition.script_tasks:
        type_ = f"bpmn:{field_metadata['script_tasks']}"
        nodes.append(ScriptTask(type_, el, el.id, process))

    for el in definition.service_tasks:
        type_ = f"bpmn:{field_metadata['service_tasks']}"
        nodes.append(ServiceTask(type_, el, el.id, process))

    for el in definition.business_rule_tasks:
        type_ = f"bpmn:{field_metadata['business_rule_tasks']}"
        nodes.append(BusinessRuleTask(type_, el, el.id, process))

    for el in definition.receive_tasks:
        type_ = f"bpmn:{field_metadata['receive_tasks']}"
        nodes.append(ReceiveTask(type_, el, el.id, process))

    for el in definition.send_tasks:
        type_ = f"bpmn:{field_metadata['send_tasks']}"
        nodes.append(SendTask(type_, el, el.id, process))

    for el in definition.parallel_gateways:
        type_ = f"bpmn:{field_metadata['parallel_gateways']}"
        nodes.append(Gateway(type_, el, el.id, process))

    for el in definition.inclusive_gateways:
        type_ = f"bpmn:{field_metadata['inclusive_gateways']}"
        nodes.append(Gateway(type_, el, el.id, process))

    for el in definition.exclusive_gateways:
        type_ = f"bpmn:{field_metadata['exclusive_gateways']}"
        nodes.append(XORGateway(type_, el, el.id, process))

    for el in definition.event_based_gateways:
        type_ = f"bpmn:{field_metadata['event_based_gateways']}"
        nodes.append(EventBasedGateway(type_, el, el.id, process))

    for el in definition.intermediate_catch_events:
        type_ = f"bpmn:{field_metadata['intermediate_catch_events']}"
        nodes.append(CatchEvent(type_, el, el.id, process))

    for el in definition.intermediate_throw_events:
        type_ = f"bpmn:{field_metadata['intermediate_throw_events']}"
        nodes.append(ThrowEvent(type_, el, el.id, process))

    for el in definition.boundary_events:
        type_ = f"bpmn:{field_metadata['boundary_events']}"
        nodes.append(BoundaryEvent(type_, el, el.id, process))

    for el in definition.end_events:
        type_ = f"bpmn:{field_metadata['end_events']}"
        nodes.append(EndEvent(type_, el, el.id, process))

    for el in definition.start_events:
        type_ = f"bpmn:{field_metadata['start_events']}"
        nodes.append(StartEvent(type_, el, el.id, process))

    for el in definition.call_activities:
        type_ = f"bpmn:{field_metadata['call_activities']}"
        nodes.append(CallActivity(type_, el, el.id, process))

    for el in definition.manual_tasks:
        type_ = f"bpmn:{field_metadata['manual_tasks']}"
        nodes.append(Node(type_, el, el.id, process))

    return nodes


def populate_process_nodes(process: Process) -> list[INode]:
    """Populate process nodes."""
    nodes: list[INode] = []
    definition = process.def_
    field_metadata = {f.name: f.metadata for f in fields(definition)}

    for el in definition.sub_processes:
        type_ = f"bpmn:{field_metadata['sub_processes']}"
        nodes.append(SubProcess(type_, el, el.id, process))

    for el in definition.ad_hoc_sub_processes:
        type_ = f"bpmn:{field_metadata['ad_hoc_sub_processes']}"
        nodes.append(AdHocSubProcess(type_, el, el.id, process))

    for el in definition.transactions:
        type_ = f"bpmn:{field_metadata['transactions']}"
        nodes.append(Transaction(type_, el, el.id, process))

    return nodes
