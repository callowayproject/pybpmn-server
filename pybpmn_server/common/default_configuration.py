"""Default configuration settings."""

import logging
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    database: SQLiteSettings | MongoDBSettings = Field(default_factory=MongoDBSettings)
    timers: TimerSettings = Field(default_factory=TimerSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    domain_name: str = Field(default="localhost")


settings = Settings()
