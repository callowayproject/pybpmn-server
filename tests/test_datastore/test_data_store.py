"""Tests for the datastore.data_store module."""

from datetime import datetime
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from ulid import ULID

from pybpmn_server.common.configuration import MongoDBSettings
from pybpmn_server.datastore.data_objects import InstanceData, InstanceDataAdapter
from pybpmn_server.datastore.data_store import DataStore, _get_items_from_instances
from pybpmn_server.datastore.interfaces import FindParams, FindResult
from pybpmn_server.interfaces.enums import TokenType


class TestGetItemsFromInstances:
    def test_get_items_from_instances_basic(self):
        """Verify that items are correctly extracted from instances and augmented with instance information."""
        item1_id = ULID()
        item2_id = ULID()
        token1_id = ULID()
        token2_id = ULID()
        instance_id = ULID()
        instance = InstanceDataAdapter.validate_python(
            {
                "id": instance_id,
                "name": "Process 1",
                "version": 1,
                "data": {"key": "value"},
                "tokens": [
                    {
                        "id": token1_id,
                        "data_path": "path.to.data",
                        "type": TokenType.Instance,
                        "status": "running",
                        "start_node_id": "node-1",
                        "current_node_id": "node-1",
                        "parent_token_id": None,
                    },
                    {
                        "id": token2_id,
                        "data_path": "",
                        "type": TokenType.Instance,
                        "start_node_id": "node-1",
                        "current_node_id": "node-1",
                        "status": "running",
                        "parent_token_id": None,
                    },
                ],
                "items": [
                    {
                        "id": item1_id,
                        "token_id": token1_id,
                        "seq": 1,
                        "element_id": "element-1",
                        "element_type": "Task",
                        "element_name": "Task 1",
                    },
                    {
                        "id": item2_id,
                        "token_id": token2_id,
                        "seq": 2,
                        "element_id": "element-2",
                        "element_type": "Task",
                        "element_name": "Task 2",
                    },
                ],
            }
        )

        # Mock data_handler.get_data
        with patch("pybpmn_server.engine.data_handler.get_data") as mock_get_data:
            mock_get_data.return_value = {"scoped": "data"}

            items = _get_items_from_instances([instance])

            # Should be sorted by seq
            assert len(items) == 2
            assert items[0].id == item1_id
            assert items[1].id == item2_id

            # Check augmentation
            mock_get_data.assert_called_with({"key": "value"}, "path.to.data")
            assert items[0].instance_id == instance_id
            assert items[0].process_name == "Process 1"
            assert items[0].data == {"scoped": "data"}


class TestDataStore:
    @pytest.fixture
    def mock_settings(self) -> Generator[MongoDBSettings, None, None]:
        """Return a mock settings object."""
        with patch("pybpmn_server.datastore.data_store.settings") as mock:
            mock.database = MongoDBSettings(
                db_url="mongodb://localhost:27017",
                db="test_db",
                instance_collection="instances",
                locks_collection="locks",
                archive_collection="archive",
            )
            yield mock

    @pytest.fixture
    def data_store(self, mock_settings) -> DataStore:
        """Return a DataStore instance."""
        return DataStore()

    def test_init_raises_if_no_database_settings(self):
        """Ensure DataStore initialization fails if database settings are missing."""
        with patch("pybpmn_server.datastore.data_store.settings") as mock_settings:
            mock_settings.database = None
            with pytest.raises(Exception, match="Database configuration is not set"):
                DataStore()

    @pytest.mark.asyncio
    async def test_save_calls_save_instance(self, data_store):
        """Verify that save method is an alias for save_instance."""
        instance = MagicMock(spec=InstanceData)
        with patch.object(DataStore, "save_instance", new_callable=AsyncMock) as mock_save_instance:
            await data_store.save(instance)
            mock_save_instance.assert_called_once_with(instance)

    @pytest.mark.asyncio
    async def test_load_instance_returns_none_if_not_found(self, data_store):
        """Verify that load_instance returns None when the instance does not exist."""
        with patch.object(DataStore, "find_instances", new_callable=AsyncMock) as mock_find_instances:
            mock_find_instances.return_value = []
            result = await data_store.load_instance("non-existent")
            assert result is None

    @pytest.mark.asyncio
    async def test_load_instance_returns_data_if_found(self, data_store):
        """Verify that load_instance returns instance and its items when found."""
        instance_data = MagicMock()
        instance_data.get.side_effect = lambda k, d=None: {
            "id": "inst-1",
            "name": "Process 1",
            "data": {},
            "tokens": [],
        }.get(k, d)
        instance_data.items = []

        with patch.object(DataStore, "find_instances", new_callable=AsyncMock) as mock_find_instances:
            mock_find_instances.return_value = [instance_data]
            result = await data_store.load_instance("inst-1")

            assert result["instance"] == instance_data
            assert isinstance(result["items"], list)

    @pytest.mark.asyncio
    async def test_save_instance_new(self, data_store):
        """Verify that save_instance uses insert for new instances."""
        instance = MagicMock(spec=InstanceData)
        instance.model_dump.return_value = {"id": "inst-1"}
        instance.saved = None
        instance.id = "inst-1"
        instance.items = []
        instance.logs = []
        instance.source = ""

        data_store.db.insert = AsyncMock()

        await data_store.save_instance(instance)

        assert instance.saved is not None
        data_store.db.insert.assert_called_once()
        args = data_store.db.insert.call_args[0]
        assert args[2][0]["id"] == "inst-1"

    @pytest.mark.asyncio
    async def test_save_instance_existing(self, data_store):
        """Verify that save_instance uses update for already saved instances."""
        instance = MagicMock(spec=InstanceData)
        instance.model_dump.return_value = {"id": "inst-1"}
        instance.saved = datetime.now()
        instance.id = "inst-1"
        instance.items = []
        instance.logs = []
        instance.source = ""

        data_store.db.update = AsyncMock()

        await data_store.save_instance(instance)

        data_store.db.update.assert_called_once()
        args = data_store.db.update.call_args[0]
        assert args[2] == {"id": "inst-1"}

    @pytest.mark.asyncio
    async def test_find_item_raises_if_not_found(self, data_store):
        """Verify that find_item raises an exception if no items match the query."""
        with patch.object(DataStore, "find_items", new_callable=AsyncMock) as mock_find_items:
            mock_find_items.return_value = []
            with pytest.raises(Exception, match="No items found"):
                await data_store.find_item({"id": "none"})

    @pytest.mark.asyncio
    async def test_find_item_raises_if_multiple_found(self, data_store):
        """Verify that find_item raises an exception if multiple items match the query."""
        with patch.object(DataStore, "find_items", new_callable=AsyncMock) as mock_find_items:
            mock_find_items.return_value = [{"id": "1"}, {"id": "2"}]
            with pytest.raises(Exception, match="More than one record found"):
                await data_store.find_item({"id": "many"})

    @pytest.mark.asyncio
    async def test_find_instances_summary(self, data_store):
        """Verify that find_instances uses correct projection for 'summary' option."""
        data_store.db.find = AsyncMock(return_value=[])

        with patch("pybpmn_server.datastore.data_store.InstanceDataList.validate_python") as mock_validate:
            mock_validate.return_value = []
            await data_store.find_instances({"status": "running"}, option="summary")

            data_store.db.find.assert_called_once()
            args, _ = data_store.db.find.call_args
            assert args[3] == {"source": 0, "logs": 0}

    @pytest.mark.asyncio
    async def test_delete_instances(self, data_store):
        """Verify that delete_instances calls the database remove method."""
        data_store.db.remove = AsyncMock()
        await data_store.delete_instances({"id": "inst-1"})
        data_store.db.remove.assert_called_once_with(
            data_store.db_config.db, data_store.db_config.instance_collection, {"id": "inst-1"}
        )

    @pytest.mark.asyncio
    async def test_install_creates_indexes(self, data_store):
        """Verify that `install` creates the expected indexes."""
        data_store.db.create_index = AsyncMock()
        await data_store.install()
        assert data_store.db.create_index.call_count == 3

    @pytest.mark.asyncio
    async def test_archive_moves_and_deletes(self, data_store):
        """
        Verify that archive inserts records into the archive collection, then deletes them from the main collection.
        """
        data_store.db.find = AsyncMock(return_value=[{"id": "1"}])
        data_store.db.insert = AsyncMock()
        with patch.object(DataStore, "delete_instances", new_callable=AsyncMock) as mock_delete:
            await data_store.archive({"id": "1"})
            data_store.db.insert.assert_called_once_with(
                data_store.db_config.db, data_store.db_config.archive_collection, [{"id": "1"}]
            )
            mock_delete.assert_called_once_with({"id": "1"})

    @pytest.mark.asyncio
    async def test_find_uses_aggregate(self, data_store):
        """Verify that find method delegates to the Aggregate class."""
        params = FindParams(filter={})
        with patch("pybpmn_server.datastore.data_store.Aggregate") as mock_aggregate_cls:
            mock_aggregate = mock_aggregate_cls.return_value
            mock_aggregate.find = AsyncMock(return_value=FindResult(total_count=0, data=[]))

            await data_store.find(params)
            mock_aggregate.find.assert_called_once_with(params)
