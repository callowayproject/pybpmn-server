"""Default configuration settings."""

import logging
from pathlib import Path
from typing import Any, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymitter import EventEmitter

from pybpmn_server.common.utils import import_string
from pybpmn_server.datastore.interfaces import IDataStore, IModelsDatastore
from pybpmn_server.engine.interfaces import ScriptHandler
from pybpmn_server.server.interfaces import ICacheManager

logger = logging.getLogger(__name__)


class TimerSettings(BaseSettings):
    """Configuration settings for the BPMN server timers."""

    force_timers_delay: int = 1000
    precision: int = 3000


class MongoDBSettings(BaseSettings):
    """Configuration settings for a MongoDB database."""

    db_url: str = "mongodb://localhost:27017?retryWrites=true&w=majority"
    db: str = "bpmn"
    locks_collection: str = "wf_locks"
    instance_collection: str = "wf_instances"
    archive_collection: str = "wf_archives"
    definition_collection: str = "wf_definitions"
    events_collection: str = "wf_events"
    enable_profiler: bool = False


class SQLiteSettings(BaseSettings):
    """Configuration settings for a SQLite database."""

    db_url: str = "sqlite:///bpmn.db"


class EmailSettings(BaseSettings):
    """Configuration settings for an email server."""

    model_config = SettingsConfigDict(env_prefix="email_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    backend: str = Field(
        default="pybpmn_server.mail.backends.console.EmailBackend",
        description="The backend to use for sending emails.",
    )
    host: str = Field(default="localhost", description="The hostname or IP address of the email server.")
    port: int = Field(default=25, description="The port number to use for the email server connection.")
    username: str = Field(default="", description="The username for authenticating with the email server.")
    password: str = Field(default="", description="The password for authenticating with the email server.")
    subject_prefix: str = Field(
        default="",
        description="Subject-line prefix for email messages sent. You'll probably want to include a trailing space.",
    )
    use_localtime: bool = Field(
        default=False, description="Whether to use local time zone (True) or in UTC (False) for sending emails."
    )
    use_tls: bool = Field(default=False, description="Whether to use TLS encryption for the email server connection.")
    use_ssl: bool = Field(default=False, description="Whether to use SSL encryption for the email server connection.")
    timeout: Optional[int] = Field(
        default=None, description="The timeout in seconds for blocking operations like the connection attempt."
    )
    ssl_keyfile: Optional[str] = Field(
        default=None, description="The path to the SSL key file for the email server connection."
    )
    ssl_certfile: Optional[str] = Field(
        default=None, description="The path to the SSL certificate file for the email server connection."
    )
    file_path: Optional[Path] = Field(
        default=None, description="The directory used by the file email backend to store output files."
    )
    default_from_email: Optional[str] = Field(
        default="noreply@example.com", description="The default email address to use for sending emails."
    )


class Settings(BaseSettings):
    """Configuration settings for the BPMN server."""

    model_config = SettingsConfigDict(env_prefix="pybpmn_server_", env_file=".env", env_file_encoding="utf-8")

    definitions_path: Path = Field(default_factory=lambda: Path.cwd() / "definitions")
    templates_path: Path = Field(default_factory=lambda: Path.cwd() / "templates")

    database_settings: SQLiteSettings | MongoDBSettings = Field(default_factory=MongoDBSettings)
    _data_store: Optional[IDataStore] = None
    _model_data_store: Optional[IModelsDatastore] = None

    timers: TimerSettings = Field(default_factory=TimerSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    domain_name: str = Field(default="localhost")

    script_backend: str = Field(default="pybpmn_server.engine.script_handler.DefaultScriptHandler")
    _script_handler: Optional[ScriptHandler] = None

    cache_backend: str = Field(default="pybpmn_server.server.cache_manager.CacheManager")
    _cache_manager: Optional[ICacheManager] = None

    service_config: dict[str, str] = Field(default_factory=dict)
    _service_providers: Optional[dict[str, Any]] = None

    _listener: Optional[EventEmitter] = None

    @property
    def listener(self) -> EventEmitter:
        """Get the listener."""
        if self._listener is None:
            self._listener = EventEmitter()
        return self._listener

    @property
    def script_handler(self) -> ScriptHandler:
        """Get the script handler."""
        if self._script_handler is None:
            self._script_handler = import_string(self.script_backend)()
        return self._script_handler

    @property
    def cache_manager(self) -> ICacheManager:
        """Get the cache manager."""
        if self._cache_manager is None:
            self._cache_manager = import_string(self.cache_backend)()
        return self._cache_manager

    @property
    def data_store(self) -> IDataStore:
        """Get the data store."""
        from pybpmn_server.datastore.data_store import DataStore

        if self._data_store is None:
            self._data_store = DataStore(self.database_settings)
        return self._data_store

    @property
    def model_data_store(self) -> IModelsDatastore:
        """Get the model data store."""
        from pybpmn_server.datastore.model_data_store import ModelsDatastore

        if self._model_data_store is None:
            self._model_data_store = ModelsDatastore(self.definitions_path, self.database_settings)
        return self._model_data_store

    @property
    def service_providers(self) -> dict[str, Any]:
        """Get the service providers."""
        if self._service_providers is None:
            self._service_providers = {k: import_string(v) for k, v in self.service_config}
        return self._service_providers


settings = Settings()
