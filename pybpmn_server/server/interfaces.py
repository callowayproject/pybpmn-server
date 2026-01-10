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

from typing import TYPE_CHECKING, Any, Optional, Protocol

if TYPE_CHECKING:
    from pybpmn_server.common.configuration import Settings
    from pybpmn_server.datastore.interfaces import IDataStore, IModelsDatastore
    from pybpmn_server.engine.interfaces import IEngine, IExecution, ScriptHandler
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


class ICron(Protocol):
    """Manages scheduling and timer events for the server."""

    def check_timers(self, duration: Any) -> Any: ...
    def start(self) -> Any: ...
    def start_timers(self) -> Any: ...


class ICacheManager(Protocol):
    """Manages instance-level caching within the BPMN server."""

    def list(self) -> list[IExecution]: ...
    def add(self, execution: IExecution) -> None: ...
    def remove(self, instance_id: Any) -> None: ...
    def shutdown(self) -> None: ...
    def get_instance(self, instance_id: str) -> Optional[IExecution]: ...
