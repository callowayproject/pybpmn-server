"""Interface for Data Objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List, Optional, Protocol

if TYPE_CHECKING:
    from datetime import datetime

    from .enums import ItemStatus


class IItemData(Protocol):
    id: str  # System generated unique Id
    item_key: str  # application assigned key to call the item by
    instance_id: str  # Instance Id of the item
    user_name: Any
    started_at: Any
    ended_at: Any
    seq: Any
    time_due: datetime
    status: ItemStatus
    data: Any
    message_id: Any
    signal_id: Any
    vars: Any
    output: Any
    assignee: Any
    candidate_groups: Any
    candidate_users: Any
    due_date: Any
    follow_up_date: Any
    priority: Any
    process_name: Optional[str] = None
    status_details: Optional[dict] = field(default_factory=dict)

    @property
    def element_id(self) -> str:
        """BPMN element id."""
        ...

    @property
    def name(self) -> str:
        """Name of bpmn element."""
        ...

    @property
    def type(self) -> str:
        """BPMN element type."""
        ...

    @property
    def token_id(self) -> Any:
        """Execution Token."""
        ...


@dataclass
class IInstanceData:
    id: Any
    name: Any
    status: Any
    version: Any
    started_at: Any
    ended_at: Any
    saved: Any
    data: Any
    items: Any
    source: Any
    logs: Any
    tokens: Any
    loops: Any
    parent_item_id: Any  # used for subProcess Calls


@dataclass
class IDefinitionData:
    name: Any
    processes: dict[Any, Any]
    root_elements: Any
    nodes: dict[Any, Any]
    flows: List[Any]
    source: Any
    logger: Any
    access_rules: List[Any]


@dataclass
class IElementData:
    id: Any
    type: Any
    name: Any
    behaviours: dict[Any, Any]


@dataclass
class IEventData:
    element_id: str
    process_id: str
    type: Any
    name: Any
    sub_type: Any
    expression: Any
    expression_format: Any  # cron/iso
    reference_date_time: Any  # start time of event or last time timer ran
    max_repeat: Any
    repeat_count: Any
    time_due: Optional[datetime] = None
    lane: Optional[str] = None
    candidate_groups: Optional[Any] = None
    candidate_users: Optional[Any] = None
    signal_id: Optional[str] = None
    message_id: Optional[str] = None


@dataclass
class IBpmnModelData:
    name: Any
    source: Any
    svg: Any
    processes: List[IProcessData]
    events: List[IEventData]
    saved: Any


@dataclass
class IProcessData:
    id: Any
    name: Any
    is_executable: Any
    candidate_starter_groups: Any
    candidate_starter_users: Any
    history_time_to_live: Any
    is_startable_in_tasklist: Any
