"""
Protocol interfaces for a BPMN server and its components.

This module defines interfaces for the primary building blocks of a BPMN
server, including the server itself, its engine, components, and auxiliary
services such as caching and scheduling. These interfaces enable modular
and consistent implementation of different server components, ensuring
interoperability and extensibility.

Interfaces include protocols for the server, its components, the execution
engine, a cache manager, and a cron scheduler.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, Union

if TYPE_CHECKING:
    from pybpmn_server.common.configuration import Settings
    from pybpmn_server.datastore.interfaces import IDataStore, IModelsDatastore
    from pybpmn_server.engine.interfaces import IExecution, IItem, ScriptHandler
    from pybpmn_server.interfaces.common import AppDelegateBase


class IBPMNServer(Protocol):
    """Represents the core BPMN server and its dependencies."""

    engine: IEngine
    listener: Any  # EventEmitter
    configuration: Settings
    definitions: IModelsDatastore
    app_delegate: AppDelegateBase
    data_store: IDataStore
    cache: ICacheManager
    cron: ICron
    script_handler: ScriptHandler


class IServerComponent(Protocol):
    """Represents a component of the BPMN server."""

    server: IBPMNServer
    configuration: Settings
    cron: Any
    cache: Any
    app_delegate: AppDelegateBase
    engine: Any
    data_store: IDataStore
    script_handler: ScriptHandler
    definitions: Any


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
        item_query: Any,
        data: Dict[str, Any],
        assignment: Dict[str, Any],
        user_name: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> IExecution: ...
    async def start_repeat_timer_event(
        self, instance_id: Any, prev_item: IItem, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None
    ) -> IExecution: ...
    async def start_event(
        self,
        instance_id: Any,
        element_id: Any,
        data: Optional[Dict[str, Any]] = None,
        user_name: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> IExecution: ...
    async def throw_message(
        self, message_id: Any, data: Dict[str, Any], matching_query: Dict[str, Any]
    ) -> IExecution: ...
    async def throw_signal(self, signal_id: Any, data: Dict[str, Any], matching_query: Dict[str, Any]) -> Any: ...
    async def restart(self, item_query: Any, data: Any, user_name: Any, options: Any) -> IExecution: ...
    async def upgrade(self, model: str, after_node_ids: List[str]) -> Union[List[str], Dict[str, Any]]: ...


class ICron(Protocol):
    """Manages scheduling and timer events for the server."""

    def check_timers(self, duration: Any) -> Any: ...
    def start(self) -> Any: ...
    def start_timers(self) -> Any: ...


class ICacheManager(Protocol):
    """Manages instance-level caching within the BPMN server."""

    def list(self) -> Any: ...
    def add(self, execution: IExecution) -> Any: ...
    def remove(self, instance_id: Any) -> Any: ...
    def shutdown(self) -> Any: ...
