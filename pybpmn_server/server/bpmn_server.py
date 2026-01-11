"""The BPMN Server class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from pybpmn_server.common.configuration import settings as default_settings
from pybpmn_server.engine.default_app_delegate import DefaultAppDelegate

if TYPE_CHECKING:
    from pybpmn_server.common.configuration import Settings
    from pybpmn_server.engine.interfaces import IEngine


class BPMNServer:
    """Represents the BPMN server."""

    def __init__(self, configuration: Optional[Settings] = None):
        self.error: Any = None
        self.configuration = configuration or default_settings
        self.listener = self.configuration.listener
        self.cron = self.configuration.cron
        self.engine = self.configuration.engine

        self.cache = self.configuration.cache
        self.data_store = self.configuration.data_store
        self.model_data_store = self.configuration.model_data_store
        self.app_delegate = DefaultAppDelegate(self.listener, self.data_store)
        self.script_handler = self.configuration.script_handler

    def status(self) -> Dict[str, Any]:
        """Get the status of the server."""
        return {
            "cache": self.cache.list(),
            "engine_running": self.engine.running_counter,
            "engine_calls": self.engine.calls_counter,
        }

    @property
    def engine_instance(self) -> IEngine:
        """Get the engine instance."""
        return self.engine


SERVER = None


def get_server(config: Optional[Settings] = None, options: Optional[Dict[str, Any]] = None) -> BPMNServer:
    """Get the BPMN Server instance, initializing it if necessary."""
    global SERVER  # noqa: PLW0603

    config = config or default_settings

    if SERVER is None:
        SERVER = BPMNServer(config)

    return SERVER
