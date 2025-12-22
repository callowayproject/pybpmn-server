import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional

from pybpmn_server.interfaces.common import IAppDelegate, IConfiguration
from pybpmn_server.interfaces.datastore import IDataStore, IModelsDatastore
from pybpmn_server.interfaces.engine import IScriptHandler
from pybpmn_server.interfaces.server import ICacheManager
from pybpmn_server.stubs import (
    DataStoreStub,
    DefaultAppDelegateStub,
    ModelsDatastoreStub,
    NoCacheManagerStub,
    ScriptHandlerStub,
)

logger = logging.getLogger(__name__)


class Configuration(IConfiguration):
    """
    Default configuration for the BPMN server.
    """

    def __init__(
        self,
        definitions_path: Optional[Path] = None,
        templates_path: Optional[Path] = None,
        timers: Optional[Dict[str, int]] = None,
        database: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
        definitions: Optional[Callable[[Any], IModelsDatastore]] = None,
        app_delegate: Optional[Callable[[Any], IAppDelegate]] = None,
        data_store: Optional[Callable[[Any], IDataStore]] = None,
        cache_manager: Optional[Callable[[Any], ICacheManager]] = None,
        script_handler: Optional[Callable[[Any], IScriptHandler]] = None,
    ):
        self.definitions_path = definitions_path
        self.templates_path = templates_path
        self.timers: Mapping[str, int | float] = (
            timers if timers is not None else {"forceTimersDelay": 1000, "precision": 3000}
        )
        self.database = database or {
            "MongoDB": {
                "db_url": "mongodb://localhost:27017?retryWrites=true&w=majority",
                "db": "bpmn",
                "Locks_collection": "wf_locks",
                "Instance_collection": "wf_instances",
                "Archive_collection": "wf_archives",
            }
        }
        self.api_key = api_key or "1234"
        self.definitions_factory = definitions
        self.app_delegate_factory = app_delegate
        self.data_store_factory = data_store
        self.cache_manager_factory = cache_manager
        self.script_handler_factory = script_handler

    def definitions(self, server: Any) -> IModelsDatastore:
        if self.definitions_factory:
            return self.definitions_factory(server)
        return ModelsDatastoreStub(server)

    def app_delegate(self, server: Any) -> IAppDelegate:
        if self.app_delegate_factory:
            return self.app_delegate_factory(server)
        return DefaultAppDelegateStub(server)

    def data_store(self, server: Any) -> IDataStore:
        if self.data_store_factory:
            return self.data_store_factory(server)
        return DataStoreStub(server)

    def cache_manager(self, server: Any) -> ICacheManager:
        if self.cache_manager_factory:
            return self.cache_manager_factory(server)
        return NoCacheManagerStub(server)

    def script_handler(self, server: Any) -> IScriptHandler:
        if self.script_handler_factory:
            return self.script_handler_factory(server)
        return ScriptHandlerStub()


_current_dir = Path(os.getcwd())

default_configuration = Configuration(
    definitions_path=_current_dir.joinpath("processes/"),
    templates_path=_current_dir.joinpath("emailTemplates/"),
    timers={
        "forceTimersDelay": 1000,
        "precision": 3000,
    },
    database={"MongoDB": {"db_url": "mongodb://localhost:27017?retryWrites=true&w=majority", "db": "bpmn"}},
    api_key="1234",
    definitions=lambda server: ModelsDatastoreStub(server),
    app_delegate=lambda server: DefaultAppDelegateStub(server),
    data_store=lambda server: DataStoreStub(server),
    cache_manager=lambda server: NoCacheManagerStub(server),
    script_handler=lambda server: ScriptHandlerStub(),
)
