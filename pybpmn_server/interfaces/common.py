"""Common interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Protocol, TypeAlias, Mapping

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IExecution, IItem


class IMongoDBDatabaseConfiguration(Protocol):
    MongoDB: Dict[str, str]


class ISQLiteDatabaseConfiguration(Protocol):
    SQLite: Dict[str, str]


# In Python, we can't easily express string indexer for different types in one Protocol
# without using __getitem__ or similar, but for migration we use Any for indexer.
IServiceProvider: TypeAlias = Mapping[str, Callable[..., Any] | "IServiceProvider"]  # noqa: TC010


class AppDelegateBase(ABC):
    """
    Application Delegate Object to respond to various events and services.

    1.  Receive all events from the workflow
    2.  Receive service calls
    3.  Receive message and signal calls
    4.  Execute scripts
    """

    def __init__(self, server: Any, moddle_options: Optional[Dict[str, Any]] = None):
        self.server = server
        self.moddle_options = moddle_options

    @abstractmethod
    async def get_services_provider(self, execution: IExecution) -> IServiceProvider:
        pass  # Simplified Promise

    @abstractmethod
    def send_email(self, to: Any, msg: Any, body: Any) -> Any:
        pass

    @abstractmethod
    def execution_started(self, execution: IExecution) -> Any:
        pass

    @abstractmethod
    def start_up(self, options: Any) -> Any:
        pass

    @abstractmethod
    def message_thrown(self, message_id: str, data: Any, message_matching_key: Any, item: IItem) -> Any:
        pass

    @abstractmethod
    def signal_thrown(self, signal_id: str, data: Any, message_matching_key: Any, item: IItem) -> Any:
        pass

    @abstractmethod
    def issue_message(self, message_id: str, data: Any) -> Any:
        pass

    @abstractmethod
    def issue_signal(self, message_id: str, data: Any) -> Any:
        pass

    @abstractmethod
    def service_called(self, kwargs: Dict[str, Any], execution: IExecution, item: IItem) -> Any:
        pass
