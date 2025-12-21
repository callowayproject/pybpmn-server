"""Enum definitions for BPMN elements."""

from __future__ import annotations

from enum import IntEnum, StrEnum


class BpmnType(StrEnum):
    """BPMN element types."""

    UserTask = "bpmn:UserTask"
    ScriptTask = "bpmn:ScriptTask"
    ServiceTask = "bpmn:ServiceTask"
    SendTask = "bpmn:SendTask"
    ReceiveTask = "bpmn:ReceiveTask"
    BusinessRuleTask = "bpmn:BusinessRuleTask"
    SubProcess = "bpmn:SubProcess"
    AdHocSubProcess = "bpmn:AdHocSubProcess"
    ParallelGateway = "bpmn:ParallelGateway"
    EventBasedGateway = "bpmn:EventBasedGateway"
    InclusiveGateway = "bpmn:InclusiveGateway"
    ExclusiveGateway = "bpmn:ExclusiveGateway"
    BoundaryEvent = "bpmn:BoundaryEvent"
    StartEvent = "bpmn:StartEvent"
    IntermediateCatchEvent = "bpmn:IntermediateCatchEvent"
    IntermediateThrowEvent = "bpmn:IntermediateThrowEvent"
    EndEvent = "bpmn:EndEvent"
    SequenceFlow = "bpmn:SequenceFlow"
    MessageFlow = "bpmn:MessageFlow"
    CallActivity = "bpmn:CallActivity"
    Transaction = "bpmn:Transaction"


class NodeSubtype(StrEnum):
    """Node subtypes."""

    timer = "timer"
    message = "message"
    signal = "signal"
    error = "error"
    escalation = "escalation"
    cancel = "cancel"
    compensate = "compensate"


class ExecutionEvent(StrEnum):
    """
    Enumeration of execution events in a process-based system.

    This class defines a set of string constants representing various execution
    events that occur in a process-based system. These events can pertain to node
    actions, flow transitions, process states, and token states. It is used to
    uniformly identify and handle these events during the lifecycle of a process
    execution.

    Attributes:
        node_enter: Event representing the entry of a node.
        node_assign: Event triggered for a node assignment operation.
        node_validate: Event triggered during node validation.
        node_start: Event marking the start of a node.
        node_wait: Event indicating a node is in a waiting state.
        node_end: Event signaling the completion of a node execution.
        node_terminated: Event indicating a node execution has been terminated.
        transform_input: Event for input data transformation.
        transform_output: Event for output data transformation.
        flow_take: Event representing the transition to the next node or flow.
        flow_discard: Event indicating a discarded flow path.
        process_loaded: Event triggered when a process is fully loaded.
        process_start: Event marking the initiation of a process.
        process_started: Event confirming a process has started.
        process_invoke: Event representing the invocation of a subprocess.
        process_invoked: Event confirming the completion of a subprocess invocation.
        process_saving: Event triggered when a process is being saved.
        process_restored: Event indicating a process has been restored from a saved state.
        process_resumed: Event marking the resumption of a process.
        process_wait: Event triggered when a process enters a waiting state.
        process_end: Event indicating the termination of a process.
        process_terminated: Event signaling a process has been forcefully terminated.
        process_exception: Event indicating an exception has occurred in the process.
        token_start: Event representing the creation or start of a token.
        token_wait: Event indicating a token is in a waiting state.
        token_end: Event signaling the completion of a token's lifecycle.
        token_terminated: Event representing a forceful termination of a token.
        process_error: Event triggered when an error occurs in the process.
    """

    node_enter = "enter"
    node_assign = "assign"
    node_validate = "validate"
    node_start = "start"
    node_wait = "wait"
    node_end = "end"
    node_terminated = "terminated"
    transform_input = "transformInput"
    transform_output = "transformOutput"
    flow_take = "take"
    flow_discard = "discard"
    process_loaded = "process.loaded"
    process_start = "process.start"
    process_started = "process.started"
    process_invoke = "process.invoke"
    process_invoked = "process.invoked"
    process_saving = "process.saving"
    process_restored = "process.restored"
    process_resumed = "process_resumed"
    process_wait = "process.wait"
    process_end = "process.end"
    process_terminated = "process.terminated"
    process_exception = "process.exception"
    token_start = "token.start"  # noqa: S105
    token_wait = "token.wait"  # noqa: S105
    token_end = "token.end"  # noqa: S105
    token_terminated = "token.terminated"  # noqa: S105
    process_error = "process.error"


class NodeAction(IntEnum):
    """
    Represents various actions that a node can perform in a system.

    This enumeration class defines a set of constant values corresponding to
    different actions a node can take. It is typically used in contexts where
    nodes in a workflow or system have to decide between multiple possible
    actions based on real-time conditions or inputs.

    Attributes:
        CONTINUE: Indicates that the node should proceed with its operation.
        WAIT: Indicates that the node should pause and wait for an external
            trigger or event.
        END: Indicates that the node has successfully completed its task.
        CANCEL: Indicates that the node's current operation is canceled.
        STOP: Indicates that the node should halt its processing entirely.
        ERROR: Indicates that the node encountered an error.
        ABORT: Indicates that the node's operation is forcibly aborted.
    """

    CONTINUE = 1
    WAIT = 2
    END = 3
    CANCEL = 4
    STOP = 5
    ERROR = 6
    ABORT = 7


class ItemStatus(StrEnum):
    enter = "enter"
    start = "start"
    wait = "wait"
    end = "end"
    terminated = "terminated"
    cancelled = "cancelled"
    discard = "discard"


class ExecutionStatus(StrEnum):
    running = "running"
    wait = "wait"
    end = "end"
    terminated = "terminated"


class TokenStatus(StrEnum):
    running = "running"
    wait = "wait"
    end = "end"
    terminated = "terminated"
    queued = "queued"


class FlowAction(StrEnum):
    take = "take"
    discard = "discard"
