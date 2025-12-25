from typing import AsyncGenerator

import pytest
from unittest.mock import AsyncMock, MagicMock

import pytest_asyncio
from pymongo.errors import PyMongoError

from pybpmn_server.common.default_configuration import MongoDBSettings
from pybpmn_server.datastore.instance_locker import InstanceLocker
from pybpmn_server.datastore.data_store import DataStore


class TestLock:
    """Tests for the lock method of InstanceLocker."""

    @pytest.fixture
    def db_config(self) -> MongoDBSettings:
        """Returns a MongoDBSettings instance with default values."""
        return MongoDBSettings(db_url="mongodb://localhost:27017", enable_profiler=False, db="test_db")

    @pytest_asyncio.fixture
    async def docstore(self, db_config) -> AsyncGenerator[DataStore, None]:
        """Returns a MongoDBSettings instance with default values."""
        datastore = DataStore(db_config)
        db = datastore.db.client["test_db"]
        await db.create_collection("wf_locks")

        yield datastore

        await datastore.db.client.drop_database("test_db")

    @pytest.mark.asyncio
    async def test_lock_returns_true_on_success(self, docstore):
        """
        The lock method should return True when the database update operation succeeds.

        This ensures that the instance is correctly marked as locked in the datastore.
        """
        locker = InstanceLocker(docstore)
        result = await locker.lock("instance_123")

        assert result is True
        assert len(await docstore.db.find("test_db", "wf_locks", {})) == 1

    @pytest.mark.asyncio
    async def test_lock_returns_false_on_pymongo_error(self, mocker):
        """
        The lock method should return False when a PyMongoError occurs during the update.

        This ensures the application can gracefully handle database failures during locking.
        """
        mock_datastore = MagicMock()
        mock_datastore.db.update = AsyncMock(side_effect=PyMongoError("Database error"))

        locker = InstanceLocker(mock_datastore)
        result = await locker.lock("instance_123")

        assert result is False


class TestRelease:
    """Tests for the release method of InstanceLocker."""

    @pytest.mark.asyncio
    async def test_release_returns_true_on_success(self, mocker):
        """
        The release method should return True when the database remove operation succeeds.
        This confirms that the lock has been successfully removed from the datastore.
        """
        mock_datastore = MagicMock()
        mock_datastore.db_configuration.db = "test_db"
        mock_datastore.db_configuration.locks_collection = "test_locks"
        mock_datastore.db.remove = AsyncMock(return_value=1)

        locker = InstanceLocker(mock_datastore)
        result = await locker.release("instance_123")

        assert result is True
        mock_datastore.db.remove.assert_called_once_with("test_db", "test_locks", {"id": "instance_123"})

    @pytest.mark.asyncio
    async def test_release_returns_false_on_pymongo_error(self, mocker):
        """
        The release method should return False when a PyMongoError occurs during removal.
        This ensures failures during lock release are caught and reported correctly.
        """
        mock_datastore = MagicMock()
        mock_datastore.db.remove = AsyncMock(side_effect=PyMongoError("Database error"))

        locker = InstanceLocker(mock_datastore)
        result = await locker.release("instance_123")

        assert result is False


class TestIsLocked:
    """Tests for the is_locked method of InstanceLocker."""

    @pytest.mark.asyncio
    async def test_is_locked_returns_true_if_record_exists(self, mocker):
        """
        The is_locked method should return True if at least one record is found in the locks collection.
        This correctly identifies that an instance is currently locked.
        """
        mock_datastore = MagicMock()
        mock_datastore.db_configuration.db = "test_db"
        mock_datastore.db_configuration.locks_collection = "test_locks"
        mock_datastore.db.find = AsyncMock(return_value=[{"id": "instance_123"}])

        locker = InstanceLocker(mock_datastore)
        result = await locker.is_locked("instance_123")

        assert result is True
        mock_datastore.db.find.assert_called_once_with("test_db", "test_locks", {"id": "instance_123"})

    @pytest.mark.asyncio
    async def test_is_locked_returns_false_if_no_record_exists(self, mocker):
        """
        The is_locked method should return False if no record is found in the locks collection.
        This confirms that the instance is not currently locked.
        """
        mock_datastore = MagicMock()
        mock_datastore.db.find = AsyncMock(return_value=[])

        locker = InstanceLocker(mock_datastore)
        result = await locker.is_locked("instance_123")

        assert result is False

    @pytest.mark.asyncio
    async def test_is_locked_returns_false_on_pymongo_error(self, mocker):
        """
        The is_locked method should return False when a PyMongoError occurs during the query.
        This provides a safe default (not locked or failure to check) when database errors occur.
        """
        mock_datastore = MagicMock()
        mock_datastore.db.find = AsyncMock(side_effect=PyMongoError("Database error"))

        locker = InstanceLocker(mock_datastore)
        result = await locker.is_locked("instance_123")

        assert result is False
