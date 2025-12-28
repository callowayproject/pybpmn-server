"""The definitions of the data objects persisted in the datastore."""

from __future__ import annotations

from datetime import datetime  # NOQA: TC003
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, TypeAdapter

from pybpmn_server.interfaces.enums import ExecutionStatus, ItemStatus, TokenStatus, TokenType


class LoopData(BaseModel):
    """Data object for a loop."""

    id: str
    node_id: str
    owner_token_id: str
    data_path: str = Field(default="")
    items: List[Any] = Field(default_factory=list)
    end_flag: bool = Field(default=False)
    completed: int = Field(default=1)
    sequence: int = Field(default=0)


class TokenData(BaseModel):
    """Data object for a token."""

    id: str
    type: TokenType
    start_node_id: str
    current_node_id: str
    status: TokenStatus
    data_path: str = Field(default="")
    parent_token_id: Optional[str] = Field(default=None)
    origin_item_id: Optional[str] = Field(default=None, description="Item ID in the instance that created this token.")
    loop_id: Optional[str] = Field(default=None)
    items_key: Optional[str] = Field(default=None)


class ItemData(BaseModel):
    """Data object for an execution item."""

    id: str = Field(description="System generated unique Id")
    token_id: str = Field(description="Token Id this item belongs to")
    element_id: str = Field(description="BPMN element Id")
    element_name: str = Field(description="BPMN element name")
    element_type: str = Field(description="BPMN element type")
    instance_id: Optional[str] = Field(default=None, description="Instance Id this item belongs to")
    instance_data: Optional[dict[str, Any]] = Field(default_factory=dict, description="Instance data")
    instance_version: Optional[int] = Field(default=None, description="Instance version")
    data: Optional[dict[str, Any]] = Field(default_factory=dict, description="Item data")
    user_name: Optional[str] = Field(default=None, description="User who started the item")
    item_key: Optional[str] = Field(default=None, description="Assigned key used in multi-instance loops.")
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)
    seq: int = Field(default=0, description="Sequence number of the item in the instance")
    time_due: Optional[datetime] = Field(default=None)
    message_id: Optional[str] = Field(default=None)
    signal_id: Optional[str] = Field(default=None)
    vars: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    assignee_id: Optional[str] = Field(default=None, description="ID of the User assigned to the item")
    candidate_groups: List[str] = Field(default_factory=list)
    candidate_users: List[str] = Field(
        default_factory=list, description="List of user IDs allowed to complete the item."
    )
    due_date: Optional[datetime] = Field(default=None)
    follow_up_date: Optional[datetime] = Field(default=None)
    priority: Optional[str] = Field(default=None)
    process_name: Optional[str] = Field(default=None)
    status: ItemStatus = Field(default=ItemStatus.enter)
    status_details: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Error details if status is error"
    )


class InstanceData(BaseModel):
    """Data object for an execution instance."""

    id: str
    name: Optional[str] = Field(default=None)
    status: ExecutionStatus = Field(default=ExecutionStatus.running)
    version: int = Field(default=0)
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)
    saved: Optional[datetime] = Field(default=None)
    data: dict[str, Any] = Field(default_factory=dict, description="Data available to the instance.")
    items: list[ItemData] = Field(default_factory=list)
    tokens: list[TokenData] = Field(default_factory=list)
    loops: list[LoopData] = Field(default_factory=list)
    parent_item_id: Optional[str] = Field(default=None, description="used for subProcess Calls")


InstanceDataList = TypeAdapter(list[InstanceData])
InstanceDataAdapter = TypeAdapter(InstanceData)


class TimerData(BaseModel):
    """Data object for a timer attached to an event."""

    expression: Any
    expression_format: Literal["cron"] | Literal["iso"] = Field(default="iso")
    reference_date_time: datetime  # start time of event or last time timer ran
    time_due: Optional[datetime] = None


class EventData(BaseModel):
    """Data object for an event in a BPMN model."""

    element_id: str
    process_id: str
    type: str
    name: Optional[str] = Field(default=None)
    sub_type: Optional[str] = Field(default=None, description="Event type (timer/message/signal)")
    lane: Optional[str] = Field(default=None)
    candidate_groups: list[str] = Field(default_factory=list)
    candidate_users: list[str] = Field(default_factory=list)
    timer: Optional[TimerData] = None
    signal_id: Optional[str] = None
    message_id: Optional[str] = None


class ProcessData(BaseModel):
    """Process data object in a BPMN model."""

    id: str
    name: Optional[str] = Field(default=None)
    is_executable: bool = Field(default=False)
    candidate_starter_groups: List[str] = Field(default_factory=list)
    candidate_starter_users: List[str] = Field(default_factory=list)
    history_time_to_live: Optional[str] = Field(default=None)
    is_startable_in_tasklist: bool = Field(default=True)


class BpmnModelData(BaseModel):
    """Data object for a BPMN model."""

    name: str
    source: str = Field(description="BPMN model source XML")
    svg: str = Field(description="BPMN model SVG")
    processes: List[ProcessData] = Field(default_factory=list)
    events: List[EventData] = Field(default_factory=list)
    saved: Optional[datetime] = Field(default=None)
