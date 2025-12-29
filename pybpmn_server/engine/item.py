"""Item class representing an execution item in the engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional

from ulid import ULID

from pybpmn_server.datastore.data_objects import ItemData
from pybpmn_server.elements.node import Node
from pybpmn_server.engine.interfaces import IExecution, IItem, IToken
from pybpmn_server.interfaces.enums import ItemStatus

if TYPE_CHECKING:
    from pybpmn_server.interfaces.elements import Element, INode


class Item(IItem):
    """
    Item class representing an execution item in the engine.
    """

    def __init__(self, element: Element, token: IToken, status: ItemStatus = ItemStatus.start):
        super().__init__(element, token, status)

        self.id: Optional[ULID] = ULID()
        self.seq: int = token.execution.get_new_sequence("item")

        self.message_id: Optional[str] = getattr(element, "message_id", None)
        self.signal_id: Optional[str] = getattr(element, "signal_id", None)

        self.user_name: Any = token.execution.user_name
        self.item_key: str = token.items_key if token.items_key else ""

        self.started_at: datetime = datetime.now(tz=timezone.utc)
        self.ended_at: Any = None
        self.instance_id: Any = None
        self.input: Dict[str, Any] = {}
        self.output: Dict[str, Any] = {}
        self.vars: Dict[str, Any] = {}
        self.assignee: Optional[str] = None
        self.candidate_groups: list[str] = []
        self.candidate_users: list[str] = []
        self.due_date: Any = None
        self.follow_up_date: Any = None
        self.priority: Any = None
        self.status_details: Optional[Dict[str, Any]] = None
        self.time_due: Optional[Any] = None
        self.timer_count: Any = None
        self.data: Any = None

    def log(self, *msg: Any) -> Any:
        return self.token.log(*msg)

    @property
    def data_from_token(self) -> Any:  # Renamed to avoid collision with self.data if needed, but TS used a getter
        return self.token.data

    @data_from_token.setter
    def data_from_token(self, val: Any) -> None:
        self.token.append_data(val, self)

    def set_data(self, val: Any) -> None:
        self.token.append_data(val, self)

    @property
    def options(self) -> Any:
        return self.token.execution.options

    @property
    def context(self) -> IExecution:
        return self.token.execution

    @property
    def element_id(self) -> str:
        return self.element.id

    @property
    def name(self) -> str:
        return self.element.name

    @property
    def token_id(self) -> Any:
        return self.token.id

    @property
    def type(self) -> str:
        return self.element.type

    @property
    def node(self) -> INode:
        return Node.from_element(self.element)

    def save(self) -> ItemData:
        """Serialize the item data for storage or transmission."""
        return ItemData(
            id=self.id,
            seq=self.seq,
            item_key=self.item_key,
            token_id=self.token.id,
            element_id=self.element_id,
            element_name=self.name,
            element_type=self.type,
            status=self.status,
            status_details=self.status_details,
            user_name=self.user_name,
            started_at=self.started_at,
            ended_at=self.ended_at,
            time_due=self.time_due,
            vars=self.vars,
            output=self.output,
            instance_id=self.instance_id,
            message_id=self.message_id,
            signal_id=self.signal_id,
            assignee_id=self.assignee,
            candidate_groups=self.candidate_groups,
            candidate_users=self.candidate_users,
            due_date=self.due_date,
            follow_up_date=self.follow_up_date,
            priority=self.priority,
            data=self.data,
        )

    @staticmethod
    def load(execution: IExecution, data_object: ItemData, token: IToken) -> Item:
        """Load item data from storage or transmission."""
        el = execution.get_node_by_id(data_object.element_id)
        item = Item(el, token, data_object.status)
        item.id = data_object.id
        item.item_key = data_object.item_key
        item.seq = data_object.seq
        item.user_name = data_object.user_name
        item.started_at = data_object.started_at
        item.ended_at = data_object.ended_at
        item.time_due = data_object.time_due
        item.status_details = data_object.status_details
        item.message_id = data_object.message_id
        item.signal_id = data_object.signal_id
        item.assignee = data_object.assignee
        item.candidate_groups = data_object.candidate_groups
        item.candidate_users = data_object.candidate_users
        item.due_date = data_object.due_date
        item.follow_up_date = data_object.follow_up_date
        item.priority = data_object.priority
        item.vars = data_object.vars
        item.output = data_object.output
        item.data = data_object.data
        return item
