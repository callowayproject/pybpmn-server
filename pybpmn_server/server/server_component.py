"""Server component."""

from typing import Any

from pybpmn_server.common.configuration import Settings
from pybpmn_server.datastore.interfaces import IDataStore, IModelsDatastore
from pybpmn_server.engine.interfaces import IEngine, ScriptHandler
from pybpmn_server.interfaces.common import AppDelegateBase
from pybpmn_server.server.bpmn_server import BPMNServer
from pybpmn_server.server.interfaces import ICacheManager, ICron


class ServerComponent:
    """
    Super class for various objects that are part of the server.
    """

    def __init__(self, server: BPMNServer):
        self.server = server

    @property
    def configuration(self) -> Settings:
        """Return the server configuration."""
        return self.server.configuration

    @property
    def cron(self) -> ICron:
        """Return the server cron manager."""
        return self.server.cron

    @property
    def cache(self) -> ICacheManager:
        """Return the server cache manager."""
        return self.server.cache

    @property
    def app_delegate(self) -> AppDelegateBase:
        """Return the server app delegate."""
        return self.server.app_delegate

    @property
    def engine(self) -> IEngine:
        """Return the server engine."""
        return self.server.engine

    @property
    def data_store(self) -> IDataStore:
        """Return the server data store."""
        return self.server.data_store

    @property
    def definitions(self) -> IModelsDatastore:
        """Return the server definitions datastore."""
        return self.server.model_data_store

    @property
    def listener(self) -> Any:
        """Return the server listener."""
        return self.server.listener

    @property
    def script_handler(self) -> ScriptHandler:
        """Return the server script handler."""
        return self.server.script_handler
