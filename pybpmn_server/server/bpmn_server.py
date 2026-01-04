"""The BPMN Server class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from pymitter import EventEmitter

from pybpmn_server.common.configuration import settings as default_settings
from pybpmn_server.datastore.data_store import DataStore
from pybpmn_server.datastore.model_data_store import ModelsDatastore
from pybpmn_server.engine.default_app_delegate import DefaultAppDelegate
from pybpmn_server.engine.engine import Engine
from pybpmn_server.engine.script_handler import DefaultScriptHandler
from pybpmn_server.server.cache_manager import CacheManager
from pybpmn_server.server.cron import Cron

if TYPE_CHECKING:
    from pybpmn_server.common.configuration import Settings
    from pybpmn_server.server.interfaces import IEngine


class BPMNServer:
    """Represents the BPMN server."""

    def __init__(self, configuration: Optional[Settings] = None):
        self.error: Any = None
        self.listener = EventEmitter()
        self.configuration = configuration or default_settings
        self.cron = Cron(self)
        self.engine = Engine()

        self.cache = CacheManager(self)
        self.data_store = DataStore(self.configuration.database_settings)
        self.definitions = ModelsDatastore(self.configuration.definitions_path, self.configuration.database_settings)
        self.app_delegate = DefaultAppDelegate(self.listener, self.data_store)
        self.script_handler = DefaultScriptHandler()
        # TODO (pybpmn-server-h00): Refactor app delegate startup calling
        # self.app_delegate.start_up(self.configuration)

    def status(self) -> Dict[str, Any]:
        """Get the status of the server."""
        return {
            "cache": self.cache.list(),
            "engine_running": self.engine.running_counter,
            "engine_calls": self.engine.calls_counter,
        }

    @property
    def engine_instance(self) -> IEngine:
        return self.engine


SERVER = None


def get_server(config: Optional[Settings] = None, options: Optional[Dict[str, Any]] = None) -> BPMNServer:
    """Get the BPMN Server instance, initializing it if necessary."""
    global SERVER  # noqa: PLW0603

    config = config or default_settings

    if SERVER is None:
        SERVER = BPMNServer(config)

    return SERVER
