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
    from pymitter import EventEmitter

    from pybpmn_server.common.configuration import Settings
    from pybpmn_server.datastore.interfaces import IDataStore, IModelsDatastore
    from pybpmn_server.engine.interfaces import IEngine, IExecution, ScriptHandler
    from pybpmn_server.interfaces.common import AppDelegateBase


class IBPMNServer(Protocol):
    """Represents the core BPMN server and its dependencies."""

    engine: IEngine
    listener: EventEmitter
    configuration: Settings
    definitions: IModelsDatastore
    app_delegate: AppDelegateBase
    data_store: IDataStore
    cache: ICacheManager
    cron: ICron
    script_handler: ScriptHandler


class ICron(Protocol):
    """Manages scheduling and timer events for the server."""

    def start(self) -> Any:
        """
        Start the timer management process.
        """
        ...

    def start_timers(self) -> Any:
        """
        Start the timer management process, ensuring only one instance runs at a time.
        """
        ...


class ICacheManager(Protocol):
    """Manages instance-level caching within the BPMN server."""

    def list(self) -> list[IExecution]:
        """
        Returns a list of all live instances in the cache.
        """
        ...

    def add(self, execution: IExecution) -> None:
        """
        Adds a live instance to the cache.
        """
        ...

    def remove(self, instance_id: Any) -> None:
        """
        Removes a live instance from the cache by its ID.
        """
        ...

    def shutdown(self) -> None:
        """
        Shuts down all live instances in the cache.
        """
        ...

    def get_instance(self, instance_id: str) -> Optional[IExecution]:
        """
        Retrieves a live instance from the cache by its ID.
        """
        ...
