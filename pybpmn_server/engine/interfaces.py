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
    def data(self) -> Any:
        """Data accessible by the Token based on its data path."""
        ...

    @property
    @abstractmethod
    def current_node(self) -> INode:
        """The node currently associated with the Token."""
        ...

    @property
    @abstractmethod
    def current_item(self) -> Optional[IItem]:
        """The current execution item in the Token's path."""
        ...

    @property
    @abstractmethod
    def last_item(self) -> Optional[IItem]:
        """The current execution item in the Token's path."""
        ...

    @property
    @abstractmethod
    def first_item(self) -> Optional[IItem]:
        """The first execution item in the Token's path."""
        ...

    @property
    @abstractmethod
    def children_tokens(self) -> List[IToken]:
        """List of child tokens associated with this token."""
        ...

    @abstractmethod
    def set_current_node(self, node: INode) -> None:
        """Set the current node for the token."""
        ...

    @abstractmethod
    def save(self) -> TokenData:
        """Serialize the token data for storage or transmission."""
        ...

    @abstractmethod
    async def resume(self) -> None:
        """Resume the execution token."""
        ...

    @abstractmethod
    def stop(self) -> None:
        """Stop the execution token."""
        ...

    @abstractmethod
    def process_error(self, error_code: Any, calling_event: Any) -> Any:
        """Process an error event and return the appropriate action."""
        ...

    @abstractmethod
    def process_escalation(self, escalation_code: Any, calling_event: Any) -> Any:
        """Process an escalation event and return the appropriate action."""
        ...

    @abstractmethod
    def process_cancel(self, calling_event: Any) -> Any:
        """Process a cancel event and return the appropriate action."""
        ...

    @abstractmethod
    async def restored(self) -> None:
        """Restore the execution token."""
        ...

    @abstractmethod
    def get_children_tokens(self) -> List[IToken]:
        """Retrieve the list of child tokens associated with this token."""
        ...

    @abstractmethod
    async def pre_execute(self) -> bool:
        """Perform pre-execution checks and setup."""
        ...

    @abstractmethod
    async def pre_next(self) -> bool:
        """Perform pre-next checks and setup."""
        ...

    @abstractmethod
    async def execute(self, input_data: Any) -> Any:
        """Execute the token with the provided input data."""
        ...

    @abstractmethod
    def append_data(self, input_data: Any, item: IItem) -> None:
        """Append input data to the token's execution item."""
        ...

    @abstractmethod
    async def terminate(self) -> None:
        """
        Terminates the token and its associated resources.

        This method ensures that the token and its children are properly terminated,
        and any ongoing processes are canceled.
        """
        ...

    @abstractmethod
    async def signal(
        self, data: Optional[dict[str, Any]], restart: bool = False, recover: bool = False, no_wait: bool = False
    ) -> None:
        """
        Asynchronously handles the signal processing for the current token and node.

        This method executes the signal operation based on the current node and item state.
        It handles various scenarios such as restarting nodes, recovering from specific states,
        and optionally skipping waiting states. This is an essential method for maintaining
        workflow control in the application.

        Args:
            data: Arbitrary data to be passed to the current node during signal invocation.
            restart: Indicates whether to restart the processing of the current node.
            recover: Indicates whether to recover from a waiting state or bypass invalid states.
            no_wait: Indicates whether to skip waiting states and immediately proceed to the next step.
        """
        ...

    @abstractmethod
    def get_full_path(self, full_path: Optional[Any] = None) -> List[IItem]:
        """Retrieve the full path of items from the token's execution history."""
        ...

    @abstractmethod
    async def end(self, cancel: bool = False) -> None:
        """
        Asynchronously ends the token's execution, handling cancellation and finalizing the current node.

        Args:
            cancel: Indicates whether the token execution is being canceled.
        """
        ...

    @abstractmethod
    async def go_next(self) -> None:
        """
        Processes the transition of the token to the next node within the workflow.

        This coroutine facilitates the movement of the token within a processing chain. It handles various
        conditions, such as whether the token path is defined, the current item status, the token's own
        status, and the availability of outbound connections. The method also manages diverging paths
        when multiple outbound connections exist, creating new tokens for parallel processing as necessary.

        Returns:
            The return value depends on the asynchronous calls and the executed logic.
        """
        ...

    @abstractmethod
    def get_sub_process_token(self) -> IToken:
        """Retrieve the sub-process token associated with this token."""
        ...

    @abstractmethod
    def log(self, *msg: Any) -> None:
        """
        Logs messages with the execution context.
        """
        ...

    @abstractmethod
    def info(self, *msg: Any) -> None:
        """Log informational messages with the execution context."""
        ...

    @abstractmethod
    def error(self, msg: Any) -> None:
        """Log error messages with the execution context."""
        ...


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
        self.app_delegate = self.configuration.app_delegate

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
    def get_node_by_id(self, id_: str) -> INode:
        """
        Get a node by its ID within the execution definition.
        """
        ...

    @abstractmethod
    def get_token(self, id_: str) -> IToken:
        """
        Retrieve a token by its ID within the execution instance.
        """
        ...

    @abstractmethod
    def get_items_data(self) -> List[ItemData]:
        """
        Retrieves a list of item data from the execution, optionally filtered by a query.

        Returns:
            A list of item data matching the query.
        """
        ...

    @abstractmethod
    async def save(self) -> None:
        """
        Saves the current state of the execution instance to persistent storage.
        """
        ...

    @abstractmethod
    async def end(self) -> None:
        """
        Asynchronously ends the execution instance, handling any necessary cleanup and finalization.
        """
        ...

    @abstractmethod
    def stop(self) -> None:
        """
        Stops the execution instance, terminating any ongoing operations and releasing resources.
        """
        ...

    @abstractmethod
    async def terminate(self) -> None:
        """
        Terminates the execution instance, ensuring all resources are released and cleanup is performed.
        """
        ...

    @abstractmethod
    async def execute(self, start_node_id: Optional[str] = None, input_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Asynchronously executes the workflow defined by the execution instance, starting from the specified node.
        """
        ...

    @abstractmethod
    async def signal_item(
        self,
        execution_id: str,
        input_data: dict[str, Any],
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
        no_wait: bool = False,
    ) -> IExecution:
        """
        Signal an item within the execution with input data, user name, and options.

        Args:
            execution_id: The ID of the item to signal.
            input_data: The input data to be assigned to the item.
            user_name: The name of the user performing the signal operation.
            restart: Flag to indicate if this is a restart operation.
            recover: Flag to indicate if this is a recovery operation.
            no_wait: Flag to indicate if this is a no-wait operation.

        Returns:
            The modified execution object.
        """
        ...

    @abstractmethod
    async def signal_event(
        self,
        execution_id: str,
        input_data: dict[str, Any],
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
    ) -> IExecution:
        """
        Signals an event by invoking a specific node in an execution process.

        This method interacts with a token corresponding to the provided execution ID or handles secondary start
        events within a process. It ensures proper signaling, restarts, or recovery operations depending on the
        provided options.

        This method involves various steps, including obtaining the services provider, initiating execution events,
        processing tokens, handling start nodes for restart scenarios, updating execution status, and saving changes
        to the execution instance.

        Args:
            execution_id: Unique identifier of the execution event to signal.
            input_data: Input data required for performing the operation on the target node or token.
            user_name: Optional string representing the user initiating the signal. Defaults to None.
            restart: Flag indicating whether to restart the process from the beginning. Defaults to False.
            recover: Flag indicating whether to recover from a previous failure. Defaults to False.

        Returns:
            The updated execution instance after signaling the event.
        """
        ...

    @abstractmethod
    async def signal_repeat_timer_event(
        self, execution_id: str, prev_item: Any, input_data: dict[str, Any]
    ) -> IExecution:
        """
        Handles the repeat timer event by signaling the process, creating a new token for the boundary event.

        This is triggered when a repeat timer boundary event occurs in the workflow.

        Args:
            execution_id: The unique identifier of the current execution.
            prev_item: The previous execution item that triggered this timer event.
            input_data: Input data associated with this event.

        Returns:
            The updated execution object after processing the repeat timer event.
        """
        ...

    @abstractmethod
    def get_items(self, query: Optional[Any] = None) -> List[IItem]:
        """
        Retrieves a list of items from the execution, optionally filtered by a query.

        Args:
            query: A query to filter the items. Defaults to None.

        Returns:
            A list of items matching the query.
        """
        ...

    @abstractmethod
    def get_state(self) -> InstanceData:
        """
        Retrieves the current state of the execution, including tokens, loops, and items.

        Returns:
            The current state of the execution.
        """
        ...

    @abstractmethod
    async def restored(self) -> None:
        """
        Asynchronously handles the restoration of an execution instance after a failure or interruption.
        """
        ...

    @abstractmethod
    async def resume(self) -> None:
        """
        Asynchronously resumes the execution of an instance that was previously paused or stopped.
        """
        ...

    @abstractmethod
    def report(self) -> None:
        """
        Generates a report summarizing the execution state and any relevant information.
        """
        ...

    @abstractmethod
    def get_new_sequence(self, scope: str) -> int:
        """
        Generates a new sequence number for a given scope within the execution instance.
        """
        ...

    @abstractmethod
    async def do_execution_event(self, process: Any, event: Any, event_details: Optional[Any] = None) -> Any:
        """
        Handles execution events within the process, such as start, end, or intermediate events.
        """
        ...

    @abstractmethod
    async def do_item_event(self, item: Any, event: Any, event_details: Optional[Any] = None) -> Any:
        """
        Handles item events within the execution, such as signal, completion, or error events.
        """
        ...

    @abstractmethod
    def log(self, *msg: Any) -> None:
        """
        Log a message at the default log level.

        Args:
            *msg: The message(s) to log.
        """
        ...

    @abstractmethod
    def log_s(self, *msg: Any) -> None:
        """
        Log an error message.

        Args:
            *msg: The error message(s) to log.
        """
        ...

    @abstractmethod
    def log_e(self, *msg: Any) -> None:
        """
        Log an error message.

        Args:
            *msg: The error message(s) to log.
        """
        ...

    @abstractmethod
    def info(self, *msg: Any) -> None:
        """
        Log an informational message.

        Args:
            *msg: The message(s) to log.
        """
        ...

    @abstractmethod
    def error(self, msg: Any) -> None:
        """
        Log an error message.

        Args:
            msg: The error message to log.
        """
        ...

    @abstractmethod
    def append_data(self, input_data: Any, item: IItem, data_path: Optional[Any] = None) -> None:
        """
        Append data to the items this transaction belongs to.

        Args:
            input_data: The data to append.
            item: The item to which the data should be appended.
            data_path: Optional path within the item's data structure to append the data. Defaults to None.
        """
        ...

    @abstractmethod
    def get_data(self, data_path: Any) -> Any:
        """
        Retrieves data from the execution instance's data based on the provided data path.

        Args:
            data_path: The path to the data to retrieve.

        Returns:
            The retrieved data.
        """
        ...

    @abstractmethod
    def process_queue(self) -> Any:
        """
        Process the event queue for the execution instance.

        This method should be called periodically to handle any pending events or tasks within the execution.

        Returns:
            The result of processing the event queue.
        """
        ...

    @staticmethod
    @abstractmethod
    async def restore(
        state: InstanceData, configuration: Optional[Settings] = None, item_id: Optional[Any] = None
    ) -> IExecution:
        """
        Restores an execution from a given state, optionally starting from a specific item ID.

        Args:
            state: The execution state to restore from.
            configuration: The configuration to restore from.
            item_id: The ID of the item to start the execution from. Defaults to None.

        Returns:
            The restored execution instance.
        """
        ...

    @abstractmethod
    async def restart(self, item_id: Any, input_data: Any, user_name: Optional[str] = None) -> IExecution:
        """
        Restarts the current execution process associated with an ended instance.

        This method transitions the instance back to a running state and recalibrates its status. It applies a restart
        signal to the specified item with the provided input data and options.

        Args:
            item_id: Identifier of the item to restart from.
            input_data: Data to be processed during the restart.
            user_name: Name of the user initiating the restart, if available.

        Returns:
            The modified instance of the current execution, with an updated state.
        """
        ...

    @abstractmethod
    async def assign(
        self,
        item_id: Any,
        input_data: Any,
        assignment: Optional[Dict[str, Any]] = None,
        user_name: Optional[str] = None,
    ) -> None:
        """
        Assign input data to an item within the execution with an optional assignment.
        """
        ...


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

    @abstractmethod
    def save(self) -> ItemData:
        """Serialize the item data for storage or transmission."""
        ...


class IEngine(ABC):
    """Represents the execution engine handling business process executions."""

    def __init__(self, configuration: Optional[Settings] = None) -> None:
        from pybpmn_server.common.configuration import settings as default_settings

        self.running_counter: int = 0
        self.calls_counter: int = 0
        self.configuration = configuration or default_settings
        self.cache = self.configuration.cache_manager
        self.data_store = self.configuration.data_store
        self.model_data_store = self.configuration.model_data_store

    @abstractmethod
    async def start(
        self,
        name: str,
        source: str,
        data: Optional[dict[str, Any]] = None,
        start_node_id: Optional[str] = None,
        user_name: Optional[str] = None,
        parent_item_id: Optional[str] = None,
        no_wait: bool = False,
    ) -> IExecution:
        """
        Starts the execution of a workflow based on the provided parameters.

        This method initializes and manages the execution of a workflow, applying the
        necessary configurations and handling execution control. It also ensures
        proper resource management such as locking and releasing the execution.

        Args:
            name: The name of the workflow to start.
            source: The definition of the workflow to start.
            data: Input data for the workflow execution. Defaults to an empty dictionary if not provided.
            start_node_id: The ID of the starting node for the workflow execution.
                Defaults to None if not provided.
            user_name: The name of the user initiating the workflow execution. Defaults to None.
            parent_item_id: The ID of the parent node for the workflow execution.
            no_wait: If True, the execution will not wait for the workflow to complete before returning.

        Returns:
            An instance representing the workflow execution, which includes execution context and state.
        """
        ...

    @abstractmethod
    async def get(self, instance_query: Any) -> IExecution:
        """
        Retrieves an execution instance based on the provided query.

        Args:
            instance_query: The query used to find the execution instance.

        Returns:
            The execution instance if found, otherwise None.
        """
        ...

    @abstractmethod
    async def invoke(
        self,
        item_query: Any,
        data: Dict[str, Any],
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
        no_wait: bool = False,
    ) -> IExecution:
        """
        Invokes an execution action within the engine, interacting with an item based on the provided query and data.

        This method manages the execution's lifecycle, including signal processing and state updates.
        It also incorporates error handling and concurrency management.

        Args:
            item_query: Query parameters used to find the specific item in the data store.
            data: Additional data passed to the execution signal. Defaults to an empty dictionary if not provided.
            user_name: Name of the user triggering the action. Could be None if no user context is required.
            restart: Flag indicating whether the execution should be restarted. Default is False.
            recover: Flag indicating whether the execution should attempt recovery. Default is False.
            no_wait: Flag indicating whether the process should avoid waiting for completion before returning.
                Default is False.

        Returns:
            The execution instance that is processed by the action, if successfully invoked.
            Returns None if the invocation fails due to errors or an invalid state.

        Raises:
            Exception: Propagates exceptions encountered during execution lifecycle management,
                if not handled internally.
        """
        ...

    @abstractmethod
    async def assign(
        self,
        item_query: dict[str, Any],
        data: Dict[str, Any],
        assignment: Dict[str, Any],
        user_name: str,
    ) -> IExecution:
        """
        Assigns an item to a user or task while maintaining proper execution and data flow.

        This method processes the assignment of an item by searching the data store for the
        item specified by the query, restoring its execution context, and assigning it to
        a task or user. It performs necessary error handling, logging, and ensures that resources
        are properly released in all scenarios.

        Args:
            item_query: Query used to locate the item in the data store.
            data: Additional data to be passed during assignment.
            assignment: Assignment-specific data used to configure the task or user allocation.
            user_name: Name of the user to whom the item is being assigned, if applicable.

        Returns:
            Execution: The execution instance that processes the assigned item.
        """
        ...

    @abstractmethod
    async def start_repeat_timer_event(
        self,
        instance_id: str,
        prev_item: IItem,
        data: Optional[Dict[str, Any]] = None,
    ) -> IExecution:
        """
        Starts a repeat timer event for a specific execution instance.

        Handles the restoration, signal processing, and release of the execution context.

        Args:
            instance_id: Identifier of the execution instance to start the repeat timer event for.
            prev_item: Previous item associated with the execution instance.
            data: Optional data to be passed during the repeat timer event signal.

        Returns:
            The execution instance that processes the repeat timer event, or None if an error occurs.

        Raises:
            Exception: Propagates exceptions encountered during execution lifecycle management,
                if not handled internally.
        """
        ...

    @abstractmethod
    async def start_event(
        self,
        instance_id: str,
        element_id: str,
        data: Optional[Dict[str, Any]] = None,
        user_name: Optional[str] = None,
        restart: bool = False,
        recover: bool = False,
    ) -> IExecution:
        """
        Starts an event by signaling it within an execution context.

        Handles initialization, signal invocation, and execution state management, ensuring the proper release process
        even in error scenarios.

        Args:
            instance_id: The unique identifier for the instance to be restored before signaling.
            element_id: The unique identifier representing the event element to be signaled.
            data: Optional data payload associated with the event, defaulting to an empty dictionary.
            user_name: Optional user name of the individual triggering the event, default is None.
            restart: Indicates whether the event should trigger a restart, default is False.
            recover: Indicates whether the event should trigger a recovery, default is False.

        Returns:
            Execution: The execution context after the event is processed.
        """
        ...

    @abstractmethod
    async def throw_message(self, message_id: Any, data: Dict[str, Any], matching_query: Dict[str, Any]) -> IExecution:
        """
        Throw a message event to trigger a process instance.
        """
        ...

    @abstractmethod
    async def throw_signal(self, signal_id: Any, data: Dict[str, Any], matching_query: Dict[str, Any]) -> Any:
        """
        Process the given signal by finding and invoking relevant events and items that are waiting for it.

        The method triggers necessary actions and collects the results of the signal propagation.

        Args:
            signal_id: Identifier of the signal to be processed.
            data: Additional data to be passed during the signal processing. Default is an empty dictionary.
            matching_query: Query that specifies additional matching conditions for items.
                Default is an empty dictionary.

        Returns:
            A list containing the IDs of the instances or items that were affected by the signal propagation.
        """
        ...

    @abstractmethod
    async def restart(self, item_query: dict[str, Any], data: dict[str, Any], user_name: Any) -> Optional[IExecution]:
        """
        Restarts an execution based on the provided item query, data, and user information.

        The method retrieves the item and its associated instance from the data store, restores the execution state,
        re-initializes the execution with the provided data, and releases the execution lock after completion.

        Args:
            item_query: A query object or identifier used to locate the item in the data store.
            data: The data required to restart the execution. This may include input parameters or state information.
            user_name: The name of the user initiating the restart operation. Used for auditing or logging purposes.

        Returns:
            An instance of the `Execution` object representing the restarted execution process.
            This includes all relevant state and runtime information.
        """
        ...

    @abstractmethod
    async def upgrade(self, model: str, after_node_ids: List[str]) -> Union[List[str], Dict[str, Any]]:
        """
        Upgrade the source of specified model instances in the data store.

        Returns a list of updated instance IDs or a dictionary containing error information.

        Args:
            model: The name of the model whose instances need to be upgraded.
            after_node_ids: A list of node IDs. Instances related to these nodes will be excluded
                from the upgrade process.

        Returns:
            A list of successfully upgraded instance IDs, or a dictionary with
                error details if an exception occurs during the upgrade process.
        """
        ...
