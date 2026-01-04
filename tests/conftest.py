from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from pybpmn_server.common.configuration import MongoDBSettings, Settings


@pytest.fixture
def fixtures_path() -> Path:
    """Returns the path to the `fixtures` directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def db_config() -> MongoDBSettings:
    """Returns a MongoDBSettings instance with default values."""
    return MongoDBSettings(db_url="mongodb://localhost:27017", enable_profiler=False, db="test_db")


@pytest_asyncio.fixture
async def settings(db_config: MongoDBSettings, fixtures_path: Path) -> AsyncGenerator[Settings, None]:
    """Returns a MongoDBSettings instance with default values."""
    settings = Settings(
        definitions_path=fixtures_path / "definitions",
        templates_path=fixtures_path / "templates",
        database_settings=db_config,
    )
    datastore = settings.data_store
    _ = datastore.db.client["test_db"]

    yield settings

    await datastore.db.client.drop_database("test_db")
