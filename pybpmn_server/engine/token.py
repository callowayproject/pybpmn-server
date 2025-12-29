"""
Defines and implements the Token class, representing the unit of execution in a process.

Tokens:

| Start                      | End                 | Data             |
|----------------------------|---------------------|------------------|
| 1 start of execution       | end of execution    | execution        |
| 2 start of subexecution    | end of subexecution | own (new object) |
| 3 start of multi-instances | end of instance     | own (new object) |
| 4 diverging                | at converge         | parent           |

Rules:

- INode acts synchronously
- Parent token goes on 'HOLD' waiting for children to finish

Example:
Event1 -> Task1   -> Gateway1       -> Task2                -> Gateway2       -> task 3
                                    -> Task3                --^

token 1   token 1    token 1 (wait for tokens 2 & 3 finish)    token 1 resume    token 1
                                       token 2                 token 2 end
                                       token 3                 token 3 end

- when token 1 arrives at Gateway1 - it waits and increments its count by 2.
- when token 2 arrives at Gateway2 - it ends and token 1 decrements its count by 1.
- when token 3 arrives at Gateway2 - it ends and token 1 decrements its count by 1.
- At Gateway 2 token 1 will proceed since its count is 0.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, List, Optional

from pybpmn_server.datastore.data_objects import TokenData
from pybpmn_server.engine.interfaces import IToken
from pybpmn_server.interfaces.enums import ItemStatus, NodeAction, TokenStatus, TokenType

if TYPE_CHECKING:
    from pybpmn_server.engine.execution import Execution
    from pybpmn_server.engine.interfaces import IExecution, IItem
    from pybpmn_server.engine.loop import Loop
    from pybpmn_server.interfaces.elements import INode


class Token(IToken):
    """
    Defines and implements the Token class, representing the unit of execution in a process.

    The Token class is responsible for managing the lifecycle of an execution token, its
    relationships with nodes, parent tokens, and subprocesses, as well as executing its workflow
    logic. It provides methods for saving and loading token state, managing node transitions,
    interacting with data paths, and executing tasks defined by nodes.
    """

    @property
    def current_node(self) -> INode:
        """The node currently associated with the Token."""
        return self._current_node

    @property
    def data(self) -> Any:
        """Data accessible by the Token based on its data path."""
        return self.execution.get_data(self.data_path)

    @property
    def current_item(self) -> Optional[IItem]:
        """The current execution item in the Token's path."""
        return self.path[-1] if self.path else None

    @property
    def first_item(self) -> Optional[IItem]:
        """The first execution item in the Token's path."""
        return self.path[0] if self.path else None

    @property
    def last_item(self) -> Optional[IItem]:
        """The second-to-last executed node in the Token's path, if not sequence flow."""
        nodes = [item for item in self.path if item.element.type != "bpmn:SequenceFlow"]
        if len(nodes) > 1:
            return nodes[-2]
        return None

    @property
    def children_tokens(self) -> List[IToken]:
        """List of child Tokens spawned by this Token."""
        return self.get_children_tokens()

    def has_node(self, node_id: str) -> bool:
        """
        Checks if a node with the specified ID exists in the path.

        This method iterates through the list of path items to determine if any item contains a node with the given ID.

        Args:
            node_id: The ID of the node to search for.

        Returns:
            True if a node with the specified ID exists in the path, False otherwise.
        """
        return any(item.node.id == node_id for item in self.path)

    def get_full_path(self, path: Optional[List[IItem]] = None) -> List[IItem]:
        """
        Retrieve the full execution path of the Token, including parent tokens' paths.

        Args:
            path: Existing path to extend, defaults to an empty list.

        Returns:
            Full execution path of the Token.
        """
        path = path or []
        if self.parent_token:
            path.extend(self.parent_token.get_full_path(path))
        path.extend(self.path)
        return path

    @staticmethod
    async def start_new_token(
        type_: TokenType,
        execution: IExecution,
        start_node: INode,
        data_path: Optional[str],
        parent_token: Optional[IToken],
        origin_item: Optional[IItem],
        loop: Optional[Loop],
        data: Any = None,
        no_execute: bool = False,
        items_key: Any = None,
    ) -> Token:
        """
        Starts a new token within the execution process and initializes or updates its attributes.

        The method also handles data appending, execution control, and managing loops if applicable.

        Args:
            type_: The type of the token to be created.
            execution: The execution instance associated with the token.
            start_node: The node where the token execution starts.
            data_path: Path to the data associated with the token (if any).
            parent_token: The token's parent token, used to inherit attributes like loops or `items_key`.
            origin_item: Item that triggered or is related to this token.
            loop: Loop context for the token if it operates within a looping construct.
            data: Data to be appended to the token during initialization. Defaults to None.
            no_execute: If True, the token will not execute upon creation. Defaults to False.
            items_key: Key to be assigned to the token used for identifying items. Inherited from `parent_token`
                if available. Defaults to None.

        Returns:
            A newly created token initialized with the provided parameters or
                inherited attributes from the parent token.
        """
        token = Token(type_, execution, start_node, data_path, parent_token, origin_item)

        if items_key is not None:
            if token.items_key is not None:
                token.items_key += "."
            else:
                token.items_key = ""
            token.items_key += str(items_key)
        elif parent_token and parent_token.items_key:
            token.items_key = parent_token.items_key

        if loop:
            token.loop = loop
        elif parent_token:
            token.loop = parent_token.loop

        token.log(
            f"Token({token.id}).start_new_token: starting new Token with id={token.id} start node={start_node.id}"
        )

        execution.tokens[token.id] = token
        token.append_data(data, origin_item)

        if not no_execute:
            await token.execute(data)
        return token

    def save(self) -> TokenData:
        """Serialize the current execution token."""
        parent_token_id = self.parent_token.id if self.parent_token else None
        origin_item_id = self.origin_item.id if self.origin_item else None
        loop_id = self.loop.id if self.loop else None

        return TokenData(
            **{
                "id": self.id,
                "type": self.type.value if isinstance(self.type, TokenType) else self.type,
                "status": self.status,
                "dataPath": self.data_path,
                "loopId": loop_id,
                "parentToken": parent_token_id,
                "originItem": origin_item_id,
                "startNodeId": self.start_node_id,
                "currentNode": self.current_node.id,
                "itemsKey": self.items_key,
            }
        )

    @staticmethod
    def load(execution: Execution, data: TokenData) -> Token:
        """
        Creates and initializes a Token instance based on provided execution context and data.

        This method constructs a Token object by retrieving referenced execution nodes and parent tokens, setting
        relevant attributes, and establishing connections to the associated execution environment.

        Args:
            execution: The execution environment containing nodes and tokens used to initialize the Token instance.
            data: A data object containing token-specific information such as type, identifiers, status,
                and additional metadata.

        Returns:
            The newly initialized Token instance.
        """
        start_node = execution.get_node_by_id(data.start_node_id_id)
        parent_token = execution.get_token(data.parent_token)
        current_node = execution.get_node_by_id(data.current_node)

        token = Token(data.type, execution, start_node, data.data_path, parent_token, None)
        token.id = data.id
        token.start_node_id = data.start_node_id
        token._current_node = current_node
        token.status = data.status
        token.items_key = data.items_key
        token.path = []
        return token

    def stop(self) -> None:
        """Stop the execution token."""
        pass

    async def resume(self) -> None:
        """Resume the execution token."""
        if self.current_item:
            await self.current_node.resume(self.current_item)

    async def restored(self) -> None:
        """Restore the execution token."""
        for item in self.path:
            await item.element.restored(item)

    def get_sub_process_token(self) -> Optional[IToken]:
        """
        Retrieves the subprocess token associated with the current token.

        If the token type is SubProcess or AdHoc, it directly returns the token. Otherwise, it recursively
        checks the parent token for an associated subprocess token.

        Returns:
            The subprocess token if found, or None if no such token exists.
        """
        if self.type in [TokenType.SubProcess, TokenType.AdHoc]:
            return self
        elif self.parent_token is None:
            return None
        else:
            return self.parent_token.get_sub_process_token()

    def get_children_tokens(self) -> List[IToken]:
        """
        Retrieves the child tokens associated with the current token.

        Returns:
            A list of child tokens.
        """
        return [t for t in self.execution.tokens.values() if t.parent_token and t.parent_token.id == self.id]

    async def pre_execute(self) -> bool:
        """
        Pre-execution hook for the token.

        Returns:
            True if pre-execution is successful, False otherwise.
        """
        from .loop import Loop

        return await Loop.check_start(self)

    async def pre_next(self) -> bool:
        """
        Checks if the next item is available in the loop.

        This asynchronous method interacts with the `Loop` class to determine whether the next item is available
        for processing. It leverages the `check_next` method provided by the `Loop` class to perform this check.

        Returns:
            True if the next item is available; otherwise, False.
        """
        from .loop import Loop

        return await Loop.check_next(self)

    async def execute(self, input_data: Optional[dict[str, Any]] = None) -> Any:
        """
        Executes the process for the current token, managing its lifecycle and providing input to the current node.

        The execution process may branch or terminate based on the current status of the token and the result of
        the node execution.

        Args:
            input_data: Input data to be passed to the current node during execution.

        Returns:
            The result of the execution if the token successfully proceeds further in the process;
                otherwise, returns `None`.
        """
        from pybpmn_server.engine.item import Item

        input_data = input_data if input_data else {}
        self.log_s(f"Token({self.id}).execute:start input {input_data}")
        if self.status == TokenStatus.end:
            self.log_e(f"Token({self.id}).execute:end token status is end: return from execute!!")
            return None

        self.status = TokenStatus.running

        if not await self.pre_execute():
            return None

        item = Item(self.current_node, self)
        if input_data:
            item.input = input_data

        self.add_item_to_path(item)
        self.log(f"Token({self.id}).execute: new IItem created itemId={item.id}")

        if input_data and hasattr(self.current_node, "set_input"):
            await self.current_node.set_input(item, input_data)

        self.log(f"Token({self.id}).execute: executing currentNodeId={self.current_node.id}")

        ret = await self.current_node.execute(item)

        if ret == NodeAction.WAIT:
            self.status = TokenStatus.wait
            self.log_e(
                f"Token({self.id}).execute:end executing currentNodeId={self.current_node.id} "
                f"item.seq={item.seq} is done!"
            )
            return None
        elif ret == NodeAction.ABORT:
            await self.execution.terminate()
            self.log_e(
                f"Token({self.id}).execute:end executing currentNodeId={self.current_node.id} "
                f"item.seq={item.seq} is done!"
            )
            return None
        elif ret == NodeAction.END:
            self.status = TokenStatus.end
            self.log_e(
                f"Token({self.id}).execute:end executing currentNodeId={self.current_node.id} "
                f"item.seq={item.seq} is done!"
            )
            return None

        result = await self.go_next()
        self.log_e(
            f"Token({self.id}).execute:end executing currentNodeId={self.current_node.id} item.seq={item.seq} is done!"
        )
        return result

    def add_item_to_path(self, item: IItem) -> None:
        """
        Adds the given item to the token's execution path and updates the current node.

        Args:
            item: The item to be added to the execution path.
        """
        self.path.append(item)
        self._current_node = item.node

    async def process_error(self, error_code: Any, calling_event: Any) -> None:
        """
        Processes an error by directing the flow to an error handler token if available.

        Args:
            error_code: Error code to be handled.
            calling_event: The event that triggered the error.
        """
        error_handler_token = self.get_scope_catch_event("error", error_code)
        if error_handler_token:
            if self.current_item:
                self.current_item.status_details = {
                    "bpmnError": error_code,
                    "errorHandler": error_handler_token.current_item.id if error_handler_token.current_item else None,
                    "callingEvent": calling_event.id,
                }
            self.log(
                f"bpmnError raised by: {calling_event.element_id} directing flow to: "
                f"{error_handler_token.current_node.id} bpmnError:{error_code}"
            )
            await error_handler_token.signal({"errorCode": error_code})
            if self.current_item:
                self.current_item.status = ItemStatus.end
            await self.end(True)
        else:
            if self.current_item:
                self.current_item.status_details = {"bpmnError": error_code, "calling_event": calling_event.id}
            self.log(f"Aborting due to bpmnError {error_code}")
            await self.execution.terminate()

    def get_scope_catch_event(self, type_: str, code: Any) -> Optional[Token]:
        """
        Retrieves the scope-catch event token based on the provided type and code.

        The method determines if a token matches the specified type and code within a given scope.
        If such a token exists, it is returned; otherwise, None is returned.

        Args:
            type_: The type of the event to catch.
            code: The code associated with the event.

        Returns:
            The matching token if found; otherwise, None.
        """
        return None

    async def process_cancel(self, calling_event: Any) -> None:
        """
        Processes a cancel event by triggering the appropriate error handler token.

        Args:
            calling_event: The event that triggered the cancel action.

        Returns:
            None
        """
        error_handler_token = self.get_scope_catch_event("cancel", None)
        if error_handler_token:
            await error_handler_token.signal(None)

    async def process_escalation(self, escalation_code: Any, calling_event: Any) -> None:
        """
        Processes an escalation event by attempting to locate and handle an error handler token.

        If a relevant error handler token is found, its signal method is invoked to process the escalation.
        If no handler is found, a log entry is recorded to indicate the absence of an escalation process.

        Args:
            escalation_code: A code that identifies the specific escalation scenario. It is used to
                retrieve the corresponding error handler token.
            calling_event: The event that triggered the escalation. It is used primarily for logging
                purposes to track the source event related to the escalation.
        """
        error_handler_token = self.get_scope_catch_event("escalation", escalation_code)
        if error_handler_token:
            self.log(
                "Action: Escalation, "
                f"Item: {error_handler_token.current_item.seq if error_handler_token.current_item else None}, "
                f"Code:{escalation_code},By:{calling_event.seq}"
            )
            await error_handler_token.signal(None)
        else:
            self.log(f"Escalation not found By: {calling_event.seq}")

    def append_data(self, input_data: Any, item: IItem) -> None:
        """
        Appends data to the execution context of the token.

        Parameters:
            input_data: The data to be appended.
            item: The item to which the data is appended.
        """
        self.execution.append_data(input_data, item, self.data_path)

    async def terminate(self) -> None:
        """
        Terminates the token and its associated resources.

        This method ensures that the token and its children are properly terminated,
        and any ongoing processes are canceled.
        """
        from .loop import Loop

        if self.status == TokenStatus.terminated:
            return

        self.log(f"Token({self.id}).terminate: terminating ....")
        await self.end(True)
        self.status = TokenStatus.terminated

        if self.current_item:
            await Loop.cancel(self.current_item)

        for ct in self.get_children_tokens():
            self.log(f"Token({self.id}).terminate: terminating child: {ct.id}...")
            await ct.terminate()

        if self.current_item:
            self.log(
                f"Token({self.id}).terminate: terminating is done! {self.current_node.id} "
                f"status={self.current_item.status}"
            )

    async def continue_(self) -> Any:
        """
        Performs continuation of the current process by finalizing the current item and advancing to the next one.

        The method first checks if there is an active current item and finalizes it using the
        current node's `end` method. Following this, it proceeds to advance to the next item or
        state by invoking the `go_next` method.

        Returns:
            The outcome of advancing to the next state or operation following the completion of the
                current item's processing.
        """
        if self.current_item:
            await self.current_node.end(self.current_item)
        await self.go_next()

    async def signal(
        self,
        data: Optional[dict[str, Any]] = None,
        restart: bool = False,
        recover: bool = False,
        no_wait: bool = False,
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
        data = data or {}
        item = self.current_item
        if not item:
            return

        self.log_s(
            f"Token({self.id}).signal: invoking {self.current_node.id} {self.current_node.type} with data={data}"
        )

        if hasattr(self.current_node, "set_input"):
            await self.current_node.set_input(item, data)

        if restart:
            if item.status == ItemStatus.wait:
                return
            await self.current_node.run(item)
            await asyncio.sleep(0.01)
            self.current_node.continue_(item)
            await self.go_next()
        elif item.status == ItemStatus.wait or recover:
            if hasattr(self.current_node, "validate"):
                await self.current_node.validate(item)
            await self.current_node.run(item)
            self.current_node.continue_(item)
            if no_wait:
                return
            await self.go_next()
        else:
            self.log(
                f"ERROR: invoking item {item.node.id} {item.id} type of {self.current_node.type} "
                f"with status of {item.status}"
            )

        self.log_e(f"Token({self.id}).signal: invoke {self.current_node.id} {self.current_node.type} finished!")

    async def end(self, cancel: bool = False) -> None:
        """
        Asynchronously ends the token's execution, handling cancellation and finalizing the current node.

        Args:
            cancel: Indicates whether the token execution is being canceled.
        """
        self.log_s(f"Token({self.id}).end: currentNode={self.current_node.id} status={self.status}")
        if self.status in [TokenStatus.end, TokenStatus.terminated]:
            return

        self.status = TokenStatus.end
        if self.current_item:
            await self.current_node.end(self.current_item)

        children = self.get_children_tokens()
        for child in children:
            if self.type in [
                TokenType.SubProcess,
                TokenType.AdHoc,
                TokenType.EventSubProcess,
                TokenType.Instance,
            ] or child.type in [TokenType.Instance, TokenType.AdHoc]:
                await child.terminate()

        if self.type == TokenType.SubProcess:
            if self.current_item:
                self.current_item.status = ItemStatus.end
            self.log("..subprocess token has ended")
            if not cancel and self.parent_token:
                await self.parent_token.signal(None)

        self.log_e(f"Token({self.id}).end(): finished!")

    async def go_next(self) -> Any:
        """
        Processes the transition of the token to the next node within the workflow.

        This coroutine facilitates the movement of the token within a processing chain. It handles various
        conditions, such as whether the token path is defined, the current item status, the token's own
        status, and the availability of outbound connections. The method also manages diverging paths
        when multiple outbound connections exist, creating new tokens for parallel processing as necessary.

        Returns:
            The return value depends on the asynchronous calls and the executed logic.
        """
        await asyncio.sleep(0.01)

        if not self.path:
            tokens = self.get_children_tokens()
            if tokens:
                first_token = tokens[0]
                if first_token.path:
                    self.add_item_to_path(first_token.path[0])

        if not self.current_item:
            return

        self.log_s(
            f"Token({self.id}).goNext(): currentNodeId={self.current_node.id} type={self.current_node.type} "
            f"currentItem.status={self.current_item.status}"
        )

        if self.current_item.status == ItemStatus.wait:
            self.log_e(
                f"Token({self.id}).goNext(): currentNodeId={self.current_node.id} type={self.current_node.type} "
                f"currentItem.status={self.current_item.status}"
            )
            return

        if self.status == TokenStatus.terminated:
            self.log_e(
                f"Token({self.id}).goNext(): currentNodeId={self.current_node.id} type={self.current_node.type} "
                f"status={self.status} not going next"
            )
            await self.end(True)
            return

        if not await self.pre_next():
            self.log_e(f"Token({self.id}).goNext(): no more outbounds - ending this token {self.id}")
            return

        outbounds = await self.current_node.get_outbounds(self.current_item)
        if not outbounds:
            await self.end()
            self.log_e(f"Token({self.id}).goNext(): no more outbounds - ending this token {self.id}")
            return

        diverging = len(outbounds) > 1 or len(self.current_node.outbounds) > 1
        this_item = self.current_item
        promises = []

        if diverging:
            self.log(f"Token({self.id}).goNext(): verify outbonds....")
            for flow_item in outbounds:
                self.log(f"Token({self.id}).goNext(): ... outbonds flowItemId={flow_item.id}")
                flow_item.status = ItemStatus.end
                self.add_item_to_path(flow_item)
                next_node = getattr(flow_item.element, "to", None)
                if next_node:
                    promises.append(
                        Token.start_new_token(
                            TokenType.Diverge, self.execution, next_node, None, self, this_item, None
                        )
                    )
            if self.type != TokenType.SubProcess:
                await self.end()
        else:
            self.log(f"Token({self.id}).goNext(): verify outbonds....")
            for flow_item in outbounds:
                self.log(f"Token({self.id}).goNext(): ... outbonds flowItemId={flow_item.id}")
                flow_item.status = ItemStatus.end
                self.add_item_to_path(flow_item)
                next_node = getattr(flow_item.element, "to", None)
                if next_node:
                    self._current_node = next_node
                    promises.append(self.execute(None))

        self.log(f"Token({self.id}).goNext(): waiting for num promises {len(promises)}")
        if promises:
            await asyncio.gather(*promises)
        self.log_e(f"Token({self.id}).goNext(): is done currentNodeId={self.current_node.id}")

    def log(self, *msg: Any) -> None:
        """
        Logs messages with the execution context.
        """
        self.execution.log(*msg)

    def log_s(self, *msg: Any) -> None:
        """
        Logs messages with the execution context at the start of a function.
        """
        self.execution.log_s(*msg)

    def log_e(self, *msg: Any) -> None:
        """
        Logs messages with the execution context at the end of a function.
        """
        self.execution.log_e(*msg)

    def info(self, msg: Any) -> None:
        """
        Logs informational messages with the execution context.
        """
        self.execution.info(msg)

    def error(self, msg: Any) -> None:
        """
        Logs error messages with the execution context.
        """
        self.execution.error(msg)
