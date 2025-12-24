"""Default configuration settings."""

import logging
from pathlib import Path

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


class Settings(BaseSettings):
    """Configuration settings for the BPMN server."""

    model_config = SettingsConfigDict(env_prefix="pybpmn_server_", env_file=".env", env_file_encoding="utf-8")

    definitions_path: Path = Field(default_factory=lambda: Path.cwd() / "definitions")
    templates_path: Path = Field(default_factory=lambda: Path.cwd() / "templates")
    database: SQLiteSettings | MongoDBSettings = Field(default_factory=MongoDBSettings)
    timers: TimerSettings = Field(default_factory=TimerSettings)


settings = Settings()
