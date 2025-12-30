"""Interfaces for BPMN elements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, Union, runtime_checkable

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
    root_elements: Any
    nodes: Dict[Any, Any]
    flows: List[Any]
    source: Any
    access_rules: List[Any]

    async def load(self) -> Any: ...
    def load_process(self, process_element: Any, parent_process: Any) -> Any: ...
    def get_json(self) -> str: ...
    def get_start_node(self) -> INode: ...
    def get_node_by_id(self, id_: Any) -> INode: ...


class Element(ABC):
    """Base class for Flow and Node elements."""

    def __init__(self, type_: str, def_: Any, id_: str):
        self.id: str = id_
        self.type: str = type_
        self.sub_type: Optional[str] = None
        self.name: str = ""
        self.behaviours: Dict[str, Behavior] = {}
        self.is_flow: bool = False
        self.lane: Optional[str] = None
        self.def_ = def_

    def continue_(self, item: IItem) -> Any:
        return None

    async def describe(self) -> List[List[str]]:
        return []

    async def restored(self, item: IItem) -> None:
        for behav in self.behaviours.values():
            await behav.restored(item)

    async def resume(self, item: IItem) -> None:
        for behav in self.behaviours.values():
            await behav.resume(item)

    def has_behaviour(self, name: str) -> bool:
        return name in self.behaviours

    def get_behaviour(self, name: str) -> Optional[Behavior]:
        return self.behaviours.get(name)

    def add_behaviour(self, name: str, behaviour: Behavior) -> None:
        self.behaviours[name] = behaviour


class IFlow(Element, ABC):
    def __init__(self, type_: str, def_: Any, id_: str, from_node: INode, to_node: INode):
        super().__init__(type_, def_, id_)
        self.id = id_
        self.type = type_
        self.from_node = from_node
        self.to_node = to_node
        self.def_ = def_
        self.is_flow = True

    @abstractmethod
    async def describe(self) -> List[List[str]]:
        pass

    @abstractmethod
    async def run(self, item: IItem) -> str:
        pass

    @abstractmethod
    async def end(self, item: IItem) -> None:
        pass

    @abstractmethod
    async def evaluate_condition(self, item: IItem) -> bool:
        pass

    @abstractmethod
    async def execute(self, item: IItem) -> None:
        pass


class INode(Element, ABC):
    def __init__(self, type_: str, def_: Any, id_: str, process: Any):
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
        return self.process.id if self.process else None

    @property
    def is_catching(self) -> bool:
        return False

    @property
    @abstractmethod
    def loop_definition(self) -> Optional[ILoopBehaviour]: ...

    @classmethod
    @abstractmethod
    def from_element(cls, element: Any) -> INode: ...

    @abstractmethod
    def continue_(self, item: IItem) -> Any: ...  # 'continue' is a keyword in Python

    @abstractmethod
    async def describe(self) -> List[List[str]]: ...

    @abstractmethod
    async def do_event(
        self,
        item: IItem,
        event: ExecutionEvent,
        new_status: Optional[ItemStatus] = None,
        event_details: Optional[Dict[str, Any]] = None,
    ) -> list[Any]: ...

    @abstractmethod
    def enter(self, item: IItem) -> None: ...

    @property
    @abstractmethod
    def requires_wait(self) -> bool: ...

    @property
    @abstractmethod
    def can_be_invoked(self) -> bool: ...

    @abstractmethod
    async def execute(self, item: IItem) -> Union[NodeAction, None]: ...

    @abstractmethod
    async def start(self, item: IItem) -> NodeAction: ...

    @abstractmethod
    async def run(self, item: IItem) -> NodeAction: ...

    @abstractmethod
    async def end(self, item: IItem, cancel: bool = False) -> None: ...

    @abstractmethod
    def init(self, item: IItem) -> None: ...

    @abstractmethod
    async def get_outbounds(self, item: IItem) -> List[IItem]: ...

    @abstractmethod
    async def get_output(self, item: IItem) -> dict[str, Any]: ...
