"""Interfaces for BPMN elements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, Protocol, TypeVar, Union, runtime_checkable

from pybpmn_parser.parse import ParseResult

if TYPE_CHECKING:
    from pybpmn_server.elements.behaviors.behavior import Behavior
    from pybpmn_server.engine.interfaces import IItem
    from pybpmn_server.interfaces.enums import ExecutionEvent, ItemStatus, NodeAction


@runtime_checkable
class ILoopBehaviour(Protocol):
    collection: Any

    def is_sequential(self) -> bool: ...
    def is_standard(self) -> bool: ...


class IDefinition(Protocol):
    name: Any
    processes: Dict[Any, Any]
    nodes: Dict[Any, Any]
    flows: List[Any]
    source: str
    access_rules: List[Any]
    parse_result: Optional[ParseResult]

    async def load(self) -> Any: ...
    def load_process(self, process_element: Any, parent_process: Any) -> Any: ...
    def get_json(self) -> str: ...
    def get_start_node(self) -> INode: ...
    def get_node_by_id(self, id_: Any) -> INode: ...


T = TypeVar("T")


class Element(Generic[T]):
    """Base class for Flow and Node elements."""

    def __init__(self, type_: str, def_: T, id_: str):
        self.id: str = id_
        self.type: str = type_
        self.sub_type: Optional[str] = None
        self.name: str = ""
        self.behaviours: Dict[str, Behavior] = {}
        self.is_flow: bool = False
        self.lane: Optional[str] = None
        self.def_ = def_

    def continue_(self, item: IItem) -> Any:
        """Continue the behavior."""
        return None

    async def restored(self, item: IItem) -> None:
        """Restore the element's state after deserialization."""
        for behav in self.behaviours.values():
            await behav.restored(item)

    async def resume(self, item: IItem) -> None:
        """Resume the element's behavior after deserialization."""
        for behav in self.behaviours.values():
            await behav.resume(item)

    def has_behaviour(self, name: str) -> bool:
        """Check if the element has a specific behavior by name."""
        return name in self.behaviours

    def get_behaviour(self, name: str) -> Optional[Behavior]:
        """Retrieve a behavior by name."""
        return self.behaviours.get(name)

    def add_behaviour(self, name: str, behaviour: Behavior) -> None:
        """Add a behavior to the element."""
        self.behaviours[name] = behaviour


class IFlow(Element, ABC, Generic[T]):
    """Base class for Flow elements."""

    def __init__(self, type_: str, def_: T, id_: str, from_node: INode, to_node: INode):
        super().__init__(type_, def_, id_)
        self.id = id_
        self.type = type_
        self.from_node = from_node
        self.to_node = to_node
        self.def_ = def_
        self.is_flow = True

    @abstractmethod
    async def run(self, item: IItem) -> str:
        """Execute the flow action based on the condition evaluation."""
        pass

    @abstractmethod
    async def end(self, item: IItem) -> None:
        """End the flow action, typically used for cleanup or finalization."""
        pass

    @abstractmethod
    async def evaluate_condition(self, item: IItem) -> bool:
        """Evaluate the flow condition based on the condition evaluation."""
        pass

    @abstractmethod
    async def execute(self, item: IItem) -> None:
        """Execute the flow action based on the condition evaluation."""
        pass


class INode(Element, ABC, Generic[T]):
    """Base class for Node elements."""

    def __init__(self, type_: str, def_: T, id_: str, process: Any):
        super().__init__(type_, def_, id_)
        self.id = id_
        self.process = process
        self.type = type_
        self.def_ = def_
        self.name: str = self.def_.name
        self.sub_type: Optional[str] = None
        self.inbounds: List[IFlow] = []
        self.outbounds: List[IFlow] = []
        self.attachments: List[INode] = []
        self.attached_to: Optional[INode] = None
        self.message_id: Optional[str] = getattr(self.def_, "message_id", None)
        self.signal_id: Optional[str] = getattr(self.def_, "signal_id", None)
        self.initiator: Optional[str] = None
        self.assignee: Optional[str] = None
        self.candidate_groups: Optional[List[str]] = None
        self.candidate_users: Optional[List[str]] = None
        self.scripts: Dict[ExecutionEvent, List[str]] = {}
        self.lane: Any = None
        self.behaviours: Dict[Any, Any] = {}
        self.child_process: Optional[Any] = None

    @property
    def process_id(self) -> Optional[str]:
        """Get the process ID associated with the node."""
        return self.process.id if self.process else None

    @property
    def is_catching(self) -> bool:
        """Check if the node is catching events."""
        return False

    @property
    def is_transaction(self) -> bool:
        """Indicates whether the node is a transaction event."""
        return False

    @property
    @abstractmethod
    def loop_definition(self) -> Optional[ILoopBehaviour]:
        """Get the loop definition associated with the node."""
        ...

    @classmethod
    @abstractmethod
    def from_element(cls, element: Any) -> INode:
        """Create a node instance from a BPMN element."""
        ...

    @abstractmethod
    def continue_(self, item: IItem) -> Any:
        """Continue the node execution."""
        ...

    @abstractmethod
    async def do_event(
        self,
        item: IItem,
        event: ExecutionEvent,
        new_status: Optional[ItemStatus] = None,
        event_details: Optional[Dict[str, Any]] = None,
    ) -> list[Any]:
        """Handle an execution event for the node."""
        ...

    @abstractmethod
    def enter(self, item: IItem) -> None:
        """Hook for entering the node for execution."""
        ...

    @property
    @abstractmethod
    def requires_wait(self) -> bool:
        """Check if the node requires waiting for an event or condition."""
        ...

    @property
    @abstractmethod
    def can_be_invoked(self) -> bool:
        """Check if the node can be invoked."""
        ...

    @abstractmethod
    async def execute(self, item: IItem) -> Union[NodeAction, None]:
        """Execute the node."""
        ...

    @abstractmethod
    async def start(self, item: IItem) -> NodeAction:
        """Start the node."""
        ...

    @abstractmethod
    async def run(self, item: IItem) -> NodeAction:
        """Run the node."""
        ...

    @abstractmethod
    async def end(self, item: IItem, cancel: bool = False) -> None:
        """End the node execution, typically used for cleanup or finalization."""
        ...

    @abstractmethod
    def init(self, item: IItem) -> None:
        """Initialize the node for execution."""
        ...

    @abstractmethod
    async def get_outbounds(self, item: IItem) -> List[IItem]:
        """Get the outbound items from the node."""
        ...

    @abstractmethod
    async def get_output(self, item: IItem) -> dict[str, Any]:
        """Get the output data from the node."""
        ...
