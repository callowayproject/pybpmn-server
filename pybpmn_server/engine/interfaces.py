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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ulid import ULID

from pybpmn_server.datastore.data_objects import InstanceData, TokenData
from pybpmn_server.interfaces.enums import ItemStatus, TokenStatus

if TYPE_CHECKING:
    from pybpmn_server.common.default_configuration import Settings
    from pybpmn_server.datastore.data_objects import ItemData
    from pybpmn_server.interfaces.common import AppDelegateBase
    from pybpmn_server.interfaces.elements import Element, INode
    from pybpmn_server.interfaces.enums import NodeAction, TokenType
    from pybpmn_server.interfaces.server import IBPMNServer


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
        self.id = ULID()
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

    def __init__(self, server: IBPMNServer, name: str, source: str, state: Optional[InstanceData] = None):
        self.instance = state or InstanceData(id=ULID(), name=name)
        self.server = server
        self.source = source

        self.tokens: Dict[Any, IToken] = {}
        self.process: Any
        self.promises: Any
        self.listener: Any
        self.is_locked = False
        self.errors: Any
        self.item: Any
        self.message_matching_key: Any
        self.worker: Any
        self.user_name: Any
        self.id: Any
        self.status: Any
        self.action: NodeAction
        self.options: Any
        self.uids: Dict[str, Any]
        self.ending: bool
        self.cron: Any
        self.cache: Any
        self.engine: Any
        self.definitions: Any

    @property
    def name(self) -> Optional[str]:
        return self.instance.name

    @property
    @abstractmethod
    def app_delegate(self) -> AppDelegateBase:
        pass

    @property
    @abstractmethod
    def configuration(self) -> Settings:
        """Return the server configuration."""
        pass

    @property
    @abstractmethod
    def script_handler(self) -> ScriptHandler: ...

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
        self, start_node_id: Optional[Any] = None, input_data: Optional[Dict[str, Any]] = None
    ) -> None: ...

    @abstractmethod
    async def signal_item(
        self,
        execution_id: Any,
        input_data: Any,
        user_name: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> IExecution: ...

    @abstractmethod
    async def signal_event(
        self,
        execution_id: Any,
        input_data: Any,
        user_name: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> IExecution: ...

    @abstractmethod
    async def signal_repeat_timer_event(
        self, execution_id: Any, prev_item: Any, input_data: Any, options: Optional[Dict[str, Any]] = None
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
