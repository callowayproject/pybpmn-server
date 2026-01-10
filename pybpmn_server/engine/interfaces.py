"""
Defines the interfaces and protocols for core components of a BPMN execution.

The module contains protocol definitions that standardize the expected
behavior of various components required for process execution, such as
token management, script evaluation, and BPMN instance handling. These
abstractions allow different implementations to integrate seamlessly
into the BPMN engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime  # NOQA: TC003
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, Union

from ulid import ULID

from pybpmn_server.datastore.data_objects import InstanceData, TokenData
from pybpmn_server.interfaces.enums import ExecutionStatus, ItemStatus, NodeAction, TokenStatus

if TYPE_CHECKING:
    import asyncio

    from pybpmn_server.common.configuration import Settings
    from pybpmn_server.datastore.data_objects import ItemData
    from pybpmn_server.elements.interfaces import Element, INode
    from pybpmn_server.elements.process import Process
    from pybpmn_server.interfaces.enums import TokenType


class ScriptHandler(ABC):
    """Handles execution of expressions and scripts."""

    @abstractmethod
    def evaluate_expression(self, scope: Union[IItem, IToken], expression: Any) -> Any:
        """Evaluates an expression in the given scope."""
        pass

    @abstractmethod
    def execute_script(self, scope: Union[IItem, IExecution], script: Any) -> Any:
        """Executes a script in the given scope."""
        pass


class IToken(ABC):
    """Interface for token components in the BPMN engine."""

    def __init__(
        self,
        type_: TokenType,
        execution: IExecution,
        start_node: INode,
        data_path: Optional[str] = None,
        parent_token: Optional[IToken] = None,
        origin_item: Optional[IItem] = None,
    ):
        self.execution = execution
        self.type = type_

        if data_path is not None:
            self.data_path = data_path
        elif parent_token:
            self.data_path = parent_token.data_path
        else:
            self.data_path = ""

        self.start_node_id = start_node.id
        self._current_node = start_node
        self.parent_token = parent_token
        self.origin_item = origin_item
        self.id = str(ULID())
        self.process_id = start_node.process_id
        self.path: List[IItem] = []
        self.status: TokenStatus = TokenStatus.running
        self.loop: Optional[Any] = None
        self.items_key: Optional[str] = None

    @property
    @abstractmethod
    def data(self) -> Any: ...

    @property
    @abstractmethod
    def current_node(self) -> Any: ...

    @property
    @abstractmethod
    def current_item(self) -> Optional[IItem]: ...

    @property
    @abstractmethod
    def last_item(self) -> Optional[IItem]: ...

    @property
    @abstractmethod
    def first_item(self) -> Optional[IItem]: ...

    @property
    @abstractmethod
    def children_tokens(self) -> List[IToken]: ...

    @abstractmethod
    def save(self) -> TokenData: ...

    @abstractmethod
    async def resume(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def process_error(self, error_code: Any, calling_event: Any) -> Any: ...

    @abstractmethod
    def process_escalation(self, escalation_code: Any, calling_event: Any) -> Any: ...

    @abstractmethod
    def process_cancel(self, calling_event: Any) -> Any: ...

    @abstractmethod
    async def restored(self) -> None: ...

    @abstractmethod
    def get_children_tokens(self) -> List[IToken]: ...

    @abstractmethod
    async def pre_execute(self) -> bool: ...

    @abstractmethod
    async def pre_next(self) -> bool: ...

    @abstractmethod
    async def execute(self, input_data: Any) -> Any: ...

    @abstractmethod
    def append_data(self, input_data: Any, item: IItem) -> None: ...

    @abstractmethod
    async def terminate(self) -> None: ...

    @abstractmethod
    async def signal(self, data: Any, restart: bool = False, recover: bool = False, no_wait: bool = False) -> Any: ...

    @abstractmethod
    def get_full_path(self, full_path: Optional[Any] = None) -> List[IItem]: ...

    @abstractmethod
    async def end(self, cancel: bool = False) -> None: ...

    @abstractmethod
    async def go_next(self) -> None: ...

    @abstractmethod
    def get_sub_process_token(self) -> IToken: ...

    @abstractmethod
    def log(self, *msg: Any) -> None: ...

    @abstractmethod
    def info(self, *msg: Any) -> None: ...

    @abstractmethod
    def error(self, msg: Any) -> None: ...


class IExecution(ABC):
    """Interface for execution components in the BPMN engine."""

    def __init__(
        self,
        name: str,
        source: str,
        configuration: Optional[Settings] = None,
        state: Optional[InstanceData] = None,
    ):
        from pybpmn_server.common.configuration import settings
        from pybpmn_server.elements.definition import Definition

        self.instance = InstanceData(id=str(ULID()), name=name) if state is None else state
        self.configuration = configuration or settings
        self.source = source
        self.data_store = self.configuration.data_store
        self.listener = self.configuration.listener
        self.definition = Definition(name, source)

        self.tokens: Dict[Any, IToken] = {}
        self.process: Optional[Process] = None
        self.is_locked = False
        self.errors: Any = None
        self.item: Any = None
        self.message_matching_key: Optional[str] = None
        self.worker: Any = None
        self.promises: List[asyncio.Future] = []
        self.user_name: str = ""
        self.action: NodeAction = NodeAction.STOP
        self.uids: Dict[str, int] = {}
        self.ending: bool = False
        self.operation: Optional[str] = None
        self.script_handler = self.configuration.script_handler
        self.engine = self.configuration.engine

    @property
    def id(self) -> str:
        """
        Get the unique identifier of the execution instance.
        """
        return self.instance.id

    @property
    def name(self) -> Optional[str]:
        """
        Get the name of the execution instance.
        """
        return self.instance.name

    @property
    def status(self) -> ExecutionStatus:
        """
        Get the status of the execution instance.
        """
        return self.instance.status

    @abstractmethod
    def get_node_by_id(self, id_: str) -> INode: ...

    @abstractmethod
    def get_token(self, id_: str) -> IToken: ...

    @abstractmethod
    def get_items_data(self) -> List[ItemData]: ...

    @abstractmethod
    async def save(self) -> None: ...

    @abstractmethod
    async def end(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    async def terminate(self) -> None: ...

    @abstractmethod
    async def execute(
        self, start_node_id: Optional[str] = None, input_data: Optional[Dict[str, Any]] = None
    ) -> None: ...

    @abstractmethod
    async def signal_item(
        self,
        execution_id: str,
        input_data: dict[str, Any],
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
    ) -> IExecution: ...

    @abstractmethod
    async def signal_event(
        self,
        execution_id: str,
        input_data: dict[str, Any],
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
    ) -> IExecution: ...

    @abstractmethod
    async def signal_repeat_timer_event(
        self, execution_id: str, prev_item: Any, input_data: dict[str, Any]
    ) -> IExecution: ...

    @abstractmethod
    def get_items(self, query: Optional[Any] = None) -> List[IItem]: ...

    @abstractmethod
    def get_state(self) -> InstanceData: ...

    @abstractmethod
    async def restored(self) -> None: ...

    @abstractmethod
    async def resume(self) -> None: ...

    @abstractmethod
    def report(self) -> None: ...

    @abstractmethod
    def get_new_sequence(self, scope: str) -> int: ...

    @abstractmethod
    async def do_execution_event(self, process: Any, event: Any, event_details: Optional[Any] = None) -> Any: ...

    @abstractmethod
    async def do_item_event(self, item: Any, event: Any, event_details: Optional[Any] = None) -> Any: ...

    @abstractmethod
    def log(self, *msg: Any) -> None: ...

    @abstractmethod
    def log_s(self, *msg: Any) -> None: ...

    @abstractmethod
    def log_e(self, *msg: Any) -> None: ...

    @abstractmethod
    def info(self, msg: Any) -> None: ...

    @abstractmethod
    def error(self, msg: Any) -> None: ...

    @abstractmethod
    def append_data(self, input_data: Any, item: IItem, data_path: Optional[Any] = None) -> None: ...

    @abstractmethod
    def get_data(self, data_path: Any) -> Any: ...

    @abstractmethod
    def process_queue(self) -> Any: ...


class IItem(ABC):
    """
    Protocol for execution items in the engine.
    """

    def __init__(self, element: Element, token: IToken, status: ItemStatus = ItemStatus.start):
        self.element = element
        self.status = status
        self.token = token
        self.input: dict[str, Any] = {}
        self.candidate_groups: List[str] = []
        self.candidate_users: List[str] = []
        self.data: dict[str, Any] = {}
        self.due_date: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self.follow_up_date: Optional[datetime] = None
        self.id: Optional[str] = None
        self.instance_id: Optional[str] = None
        self.item_key: Optional[str] = None
        self.message_id: Optional[str] = None
        self.output: dict[str, Any] = {}
        self.priority: Optional[str] = None
        self.seq: int = 0
        self.signal_id: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.status_details: Optional[dict[str, Any]] = None
        self.time_due: Optional[datetime] = None
        self.user_name: Optional[str] = None
        self.vars: dict[str, Any] = {}
        self.process: Optional[Any] = None
        self.timer_count: int = 0

    @property
    @abstractmethod
    def context(self) -> IExecution:
        """BPMN execution context."""
        ...

    @property
    @abstractmethod
    def node(self) -> INode:
        """BPMN node."""
        ...

    @property
    @abstractmethod
    def element_id(self) -> str:
        """BPMN element id."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of bpmn element."""
        ...

    @property
    @abstractmethod
    def type(self) -> str:
        """BPMN element type."""
        ...

    @property
    @abstractmethod
    def token_id(self) -> Any:
        """Execution Token."""
        ...


class IEngine(Protocol):
    """Represents the execution engine handling business process executions."""

    running_counter: int
    calls_counter: int

    async def start(
        self,
        name: Any,
        data: Optional[Any] = None,
        start_node_id: Optional[str] = None,
        user_name: Optional[str] = None,
        options: Optional[Any] = None,
    ) -> IExecution: ...
    async def get(self, instance_query: Any) -> IExecution: ...
    async def invoke(
        self,
        item_query: Any,
        data: Dict[str, Any],
        user_name: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> IExecution: ...
    async def assign(
        self,
        item_query: dict[str, Any],
        data: Dict[str, Any],
        assignment: Dict[str, Any],
        user_name: str,
    ) -> IExecution: ...
    async def start_repeat_timer_event(
        self,
        instance_id: str,
        prev_item: IItem,
        data: Optional[Dict[str, Any]] = None,
    ) -> IExecution: ...
    async def start_event(
        self,
        instance_id: str,
        element_id: str,
        data: Optional[Dict[str, Any]] = None,
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
    ) -> IExecution: ...
    async def throw_message(
        self, message_id: Any, data: Dict[str, Any], matching_query: Dict[str, Any]
    ) -> IExecution: ...
    async def throw_signal(self, signal_id: Any, data: Dict[str, Any], matching_query: Dict[str, Any]) -> Any: ...
    async def restart(self, item_query: Any, data: Any, user_name: Any, options: Any) -> IExecution: ...
    async def upgrade(self, model: str, after_node_ids: List[str]) -> Union[List[str], Dict[str, Any]]: ...
