"""Data store interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, Union

if TYPE_CHECKING:
    from datetime import datetime

    from .data_objects import IBpmnModelData, IInstanceData, IItemData
    from .elements import IDefinition


@dataclass
class FindParams:
    filter: Optional[Dict[str, Any]] = None
    after: Optional[str] = None
    limit: Optional[int] = None
    sort: Optional[Dict[str, Union[int, Any]]] = None
    projection: Optional[Dict[str, Any]] = None
    last_item: Optional[Dict[str, Any]] = None
    latest_item: Optional[Dict[str, Any]] = None
    get_total_count: Optional[bool] = None


@dataclass
class FindResult:
    data: Optional[List[Any]] = None
    next_cursor: Optional[Union[str, None]] = None
    total_count: Optional[int] = None
    error: Optional[str] = None


class IDataStore(Protocol):
    db_configuration: Any
    db: Any
    logger: Any
    locker: Any

    async def save(self, instance: Any, options: Any) -> None: ...
    async def load_instance(self, instance_id: Any, options: Any) -> Dict[str, Any]: ...
    async def find_item(self, query: Any) -> IItemData: ...
    async def find_instance(self, query: Any, options: Any) -> IInstanceData: ...
    async def find_instances(self, query: Any, option: Any) -> List[IInstanceData]: ...
    async def find_items(self, query: Any) -> List[IItemData]: ...
    async def delete_instances(self, query: Optional[Any] = None) -> None: ...
    def install(self) -> Any: ...
    def archive(self, query: Any) -> Any: ...
    async def find(self, params: FindParams) -> FindResult: ...


class IModelsDatastore(Protocol):
    async def get(self, query: Any) -> List[Dict[str, Any]]: ...
    async def get_list(self, query: Any) -> List[str]: ...
    async def get_source(self, name: Any, owner: Any = None) -> str: ...
    async def get_svg(self, name: Any, owner: Any = None) -> str: ...
    async def save(self, name: Any, bpmn: Any, svg: Optional[Any] = None, owner: Optional[Any] = None) -> bool: ...
    async def load(self, name: Any, owner: Any = None) -> IDefinition: ...
    async def load_model(self, name: Any, owner: Any = None) -> IBpmnModelData: ...
    async def find_events(self, query: Any, owner: Any = None) -> List[Any]: ...
    async def rebuild(self, model: Optional[Any] = None) -> None: ...
    def install(self) -> Any: ...
    def import_(self, data: Any) -> Any: ...  # 'import' is keyword
    async def save_model(self, model: IBpmnModelData) -> bool: ...
    async def delete_model(self, name: Any, owner: Any = None) -> None: ...
    async def rename_model(self, name: Any, new_name: Any, owner: Any = None) -> bool: ...


@dataclass
class EventData:  # Implementing IEventData but as dataclass
    element_id: str
    process_id: str
    type: Any
    sub_type: Any
    name: Any
    signal_id: Optional[str] = None
    message_id: Optional[str] = None
    expression: Optional[Any] = None
    expression_format: Optional[Any] = None
    reference_date_time: Optional[Any] = None
    max_repeat: Optional[Any] = None
    repeat_count: Optional[Any] = None
    time_due: Optional[datetime] = None
