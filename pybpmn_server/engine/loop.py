"""
An implementation of a loop structure in a process execution engine.

This module defines the Loop class which is used to manage sequential,
standard, and parallel loops in process nodes. The class supports actions
like checking loop types, managing loop items, saving and loading loop states,
and handling loop execution flows in relation to tokens.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pybpmn_server.datastore.data_objects import LoopData
from pybpmn_server.interfaces.enums import TokenStatus, TokenType

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IExecution, IToken
    from pybpmn_server.elements.interfaces import INode


class Loop:
    """Encapsulates the behavior and state management of a loop in a process execution."""

    def __init__(self, node: INode, token: IToken, data_object: Optional[LoopData] = None):
        self.node = node
        self.ownerToken = token
        self.completed = 1
        self.sequence = 0
        self.data_path: str = ""
        self._items: Optional[List[Any]] = None
        self.end_flag = False

        self.id = token.execution.get_new_sequence("loop")

        if data_object:
            self.id = data_object.id
            self._items = data_object.items
            self.completed = data_object.completed
            self.sequence = data_object.sequence
            self.definition = node.loop_definition
            self.end_flag = data_object.end_flag
            self.data_path = data_object.data_path
        else:
            self.definition = node.loop_definition
            self.completed = 1
            self.sequence = 0
            if token.data_path:
                self.data_path = token.data_path + "." + self.node.id
            else:
                self.data_path = self.node.id

    def is_sequential(self) -> bool:
        """
        Check if the loop is sequential based on its definition.
        """
        assert self.definition is not None
        return self.definition.is_sequential()

    def is_standard(self) -> bool:
        """
        Check if the loop is standard based on its definition.
        """
        assert self.definition is not None
        return self.definition.is_standard()

    def save(self) -> LoopData:
        """
        Serializes the current state of the object as a LoopData instance.

        This method constructs a LoopData object that encapsulates the current state of the object, including its
        identifiers, associated node, owner token, data path, items, end flag, completion status, and sequence. It
        is typically used when persisting the state or sharing it across different components.

        Returns:
            An object that represents the state of the instance, including its attributes and their current values.
        """
        return LoopData(
            id=self.id,
            node_id=self.node.id,
            owner_token_id=self.ownerToken.id,
            data_path=self.data_path,
            items=self._items,
            end_flag=self.end_flag,
            completed=self.completed,
            sequence=self.sequence,
        )

    def end(self) -> None:
        """
        Mark the loop as ended.
        """
        self.end_flag = True

    @staticmethod
    def load(execution: IExecution, data_object: LoopData) -> Loop:
        """
        Loads a Loop instance from a LoopData object.
        """
        node = execution.get_node_by_id(data_object.node_id)
        owner_token = execution.get_token(data_object.owner_token_id)
        return Loop(node, owner_token, data_object)

    async def get_items(self) -> List[Any]:
        """
        Asynchronously retrieves items from the specified collection or range.

        If the `_items` attribute is not yet initialized, this method evaluates the
        expression defined in the `definition` attribute's collection. Based on the
        result, it either assigns a list generated from a range (if the result is an
        integer) or the evaluated collection to `_items`. The fetched items are then
        returned.

        Returns:
            A list of items retrieved or generated based on the evaluated collection or range.
        """
        if self._items is None:
            assert self.definition is not None
            self._items = self.ownerToken.execution.script_handler.evaluate_expression(
                self.ownerToken, self.definition.collection
            )
            if isinstance(self._items, int):
                self._items = list(range(self._items))
        return self._items

    async def is_done(self) -> bool:
        """
        Is the loop done or not?

        Checks if the current sequence exceeds the number of available items.

        This method asynchronously retrieves the list of items and determines whether the current sequence value
        is beyond the index of the last item in the list.

        Returns:
            True if the sequence exceeds the number of items, False otherwise.
        """
        items = await self.get_items()
        return self.sequence > len(items) - 1

    async def get_next(self) -> Any:
        """
        Retrieves the next item in the sequence from the available items.

        This asynchronous method fetches a list of items and returns the next item based on the current sequence.
        If the sequence exceeds the available items, it returns None.
        The sequence is incremented after accessing an item.

        Returns:
            Any: The next item in the sequence if available, otherwise None.
        """
        items = await self.get_items()
        if len(items) > self.sequence:
            val = items[self.sequence]
            self.sequence += 1
            return val
        else:
            return None

    @staticmethod
    async def check_start(token: IToken) -> bool:
        """
        Determines whether a token can proceed or if additional tokens are required based on the current loop config.

        Handles
        sequential, standard, and parallel loop execution types. If a loop definition
        exists within the token's current node, it evaluates the type of loop and
        manages the creation or execution of new tokens accordingly.

        Args:
            token: The token instance representing an execution flow in the system. It contains the current node,
                execution, and loop details that influence the decision-making process.

        Returns:
            Returns True if the token's current execution step can begin without
            the need for further token creation. Returns False if new tokens are
            created or other operations defer the current token's execution.
        """
        from .token import Token

        loop_definition = token.current_node.loop_definition

        if not loop_definition:
            return True

        if token.loop and token.loop.node.id == token.current_node.id:
            return True

        loop = Loop(token.current_node, token)
        data: Dict[str, Any] = {}

        if loop.is_sequential():
            seq = await loop.get_next()
            await Token.start_new_token(
                TokenType.Instance,
                token.execution,
                token.current_node,
                loop.data_path + "." + str(seq),
                token,
                token.current_item,
                loop,
                data,
                False,
                seq,
            )
            return False
        elif loop.is_standard():
            token.log("standard loop")
            seq = loop.sequence
            loop.sequence += 1
            await Token.start_new_token(
                TokenType.Instance,
                token.execution,
                token.current_node,
                loop.data_path + "." + str(seq),
                token,
                token.current_item,
                loop,
                data,
                False,
                seq,
            )
            return False
        else:  # parallel
            seq_idx = 0
            items = await loop.get_items()
            if items:
                tokens = []
                for seq in items:
                    data = {}
                    new_token = await Token.start_new_token(
                        TokenType.Instance,
                        token.execution,
                        token.current_node,
                        loop.data_path + "." + str(seq),
                        token,
                        token.current_item,
                        loop,
                        data,
                        True,
                        seq,
                    )
                    tokens.append(new_token)
                    token.log(f"created token {new_token.id} for {seq}")
                    seq_idx += 1

                for t in tokens:
                    await t.execute(None)
            else:
                token.error("loop has no items")

            token.log(f"..loop: fired all tokens {seq_idx}")
            return False

    @staticmethod
    async def cancel(from_item: Any) -> None:
        """
        Handles the cancellation of operations associated with a specific loop context.

        The method ensures that tokens within the same loop context, excluding the initiating token,
        are terminated. If a parent token is associated with the first token in the loop, the method
        additionally attempts to invoke its termination sequence. Logs are generated throughout to
        trace the cancellation process.

        Args:
            from_item: The item associated with the token initiating the loop cancellation.
                It must contain a valid token with an associated loop context.
        """
        if not from_item or not from_item.token.loop:
            return

        token = from_item.token
        current_loop_id = from_item.token.loop.id

        if token.parent_token and token.parent_token.loop and token.parent_token.loop.id == current_loop_id:
            return

        loop_first_token = None
        tokens_to_terminate = []

        token.log(f"..loop.cancel {current_loop_id}")

        for t in token.execution.tokens.values():
            if t.loop and t.loop.id == current_loop_id and t.id != token.id:
                if loop_first_token is None:
                    loop_first_token = t
                tokens_to_terminate.append(t)

        if loop_first_token:
            token.log(f"..loop.cancel {current_loop_id} - first token {loop_first_token.id}")
            for t in tokens_to_terminate:
                if t.status != TokenStatus.terminated:
                    token.log(f"..loop.cancel {current_loop_id} - terminating token {t.id}")
                    await t.terminate()

            if loop_first_token.parent_token and loop_first_token.parent_token.current_node:
                await loop_first_token.parent_token.current_node.end(loop_first_token.parent_token.current_item)

    @staticmethod
    async def check_next(token: IToken) -> bool:
        """
        Checks if the current token can proceed to the next node in its loop.

        If the token is part of a loop and its current node is the loop's node,
        it evaluates the loop's condition and proceeds accordingly.

        Args:
            token: The token to check.

        Returns:
            True if the token can proceed, False otherwise.
        """
        from .token import Token, TokenType

        if token.loop and token.current_node.id == token.loop.node.id:
            data: Dict[str, Any] = {}

            if token.loop.is_sequential():
                if await token.loop.is_done():
                    await token.end()
                    if token.parent_token:
                        await token.parent_token.go_next()
                    return False
                else:
                    await token.current_node.end(token.current_item)
                    await token.end()
                    seq = await token.loop.get_next()
                    await Token.start_new_token(
                        TokenType.Instance,
                        token.execution,
                        token.current_node,
                        token.loop.data_path + "." + str(seq),
                        token.parent_token,
                        token.parent_token.current_item if token.parent_token else None,
                        token.loop,
                        data,
                        False,
                        seq,
                    )
                    return False
            elif token.loop.is_standard():
                await token.end()
                if token.loop.end_flag:
                    if token.parent_token:
                        await token.parent_token.go_next()
                    return True
                else:
                    token.loop.completed += 1
                    seq = token.loop.sequence
                    token.loop.sequence += 1
                    await Token.start_new_token(
                        TokenType.Instance,
                        token.execution,
                        token.current_node,
                        token.loop.data_path + "." + str(seq),
                        token.parent_token,
                        token.current_item,
                        token.loop,
                        data,
                        False,
                        seq,
                    )
                    return False
            else:  # parallel
                await token.end()
                token.loop.completed += 1
                items = await token.loop.get_items()
                if token.loop.completed == len(items) + 1:
                    if token.parent_token:
                        await token.parent_token.go_next()
                    return False
                return False
        return True
