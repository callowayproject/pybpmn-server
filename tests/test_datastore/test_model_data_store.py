"""Tests for the ModelsDatastore class."""

from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from pybpmn_server.common.configuration import MongoDBSettings
from pybpmn_server.datastore.data_objects import BpmnModelData
from pybpmn_server.datastore.model_data_store import ModelsDatastore


@pytest.fixture
def db_config() -> MongoDBSettings:
    """Return a mock settings object."""
    return MongoDBSettings(db_url="mongodb://localhost:27017", enable_profiler=False, db="test_db")


@pytest_asyncio.fixture
async def datastore(db_config: MongoDBSettings, tmp_path: Path) -> AsyncGenerator[ModelsDatastore, None]:
    """Initializes ModelsDatastore with mocked settings and MongoDB."""
    from pybpmn_server.datastore.mongodb import MongoDB

    mongo_db = MongoDB(db_config)
    _db = mongo_db.client["test_db"]

    yield ModelsDatastore(tmp_path, db_config)

    await mongo_db.client.drop_database("test_db")


class TestImportModel:
    """Tests for the ModelsDatastore.import_model method."""

    @pytest.mark.asyncio
    async def test_serializes_and_inserts_model(self, datastore: ModelsDatastore):
        """
        Verify that importing a model correctly serializes the data and inserts into MongoDB.
        """
        # Arrange
        db = datastore.db.client["test_db"]
        collection = db[datastore.db_config.definition_collection]
        model_data = BpmnModelData(name="test_process", source="<xml/>", svg="<svg/>")

        # Act
        result = await datastore.import_model(model_data)

        # Assert
        assert result == 1
        async with collection.find({"name": "test_process"}) as cursor:
            docs = await cursor.to_list()
        assert len(docs) == 1
        assert docs[0]["name"] == "test_process"


class TestLoadModel:
    """Tests for the ModelsDatastore.load_model method."""

    @pytest.mark.asyncio
    async def test_returns_data_if_found(self, datastore: ModelsDatastore):
        """
        Ensure that when a model exists in the database, it is retrieved and parsed into a BpmnModelData object.
        """
        # Arrange
        db = datastore.db.client["test_db"]
        collection = db[datastore.db_config.definition_collection]
        model_data = BpmnModelData(name="my_model", source="<xml/>", svg="<svg/>")
        await collection.insert_one(model_data.model_dump())

        # Act
        result = await datastore.load_model("my_model")

        # Assert
        assert isinstance(result, BpmnModelData)
        assert result.name == "my_model"

    @pytest.mark.asyncio
    async def test_returns_none_if_not_found(self, datastore: ModelsDatastore):
        """
        Verify that the method returns None gracefully when the requested model name does not exist in the database.
        """
        # Act
        result = await datastore.load_model("unknown")

        # Assert
        assert result is None


class TestSaveModel:
    """Tests for the ModelsDatastore.save_model method."""

    @pytest.mark.asyncio
    async def test_save_model_updates_timestamp_and_calls_upsert(self, datastore: ModelsDatastore):
        """
        Confirm that saving a model updates its 'saved' timestamp and triggers an upsert operation in the database.
        """
        # Arrange
        db = datastore.db.client["test_db"]
        collection = db[datastore.db_config.definition_collection]
        model_data = BpmnModelData(name="update_me", source="<xml/>", svg="<svg/>")
        updated_data = BpmnModelData(name="update_me", source="<xml></xml>", svg="<svg/>")

        # Act
        success_1 = await datastore.save_model(model_data)
        success = await datastore.save_model(updated_data)

        # Assert
        assert success_1
        assert success
        async with collection.find({"name": "update_me"}) as cursor:
            docs = await cursor.to_list()
            assert len(docs) == 1
            assert docs[0]["source"] == "<xml></xml>"
            assert docs[0]["saved"] is not None


class TestDeleteModel:
    """Tests for the ModelsDatastore.delete_model method."""

    @pytest.mark.asyncio
    async def test_removes_db_record_and_files(self, datastore: ModelsDatastore):
        """
        Validate that deleting a model removes the database record and attempts to clean up associated files.
        """
        # Arrange
        db = datastore.db.client["test_db"]
        collection = db[datastore.db_config.definition_collection]
        model_data = BpmnModelData(name="delete_me", source="<xml/>", svg="<svg/>")
        bpmn_path = datastore.definitions_path.joinpath("delete_me.bpmn")
        svg_path = datastore.definitions_path.joinpath("delete_me.svg")
        bpmn_path.touch()
        svg_path.touch()
        await datastore.save_model(model_data)

        # Act
        await datastore.delete_model("delete_me")

        # Assert
        assert not bpmn_path.exists()
        assert not svg_path.exists()
        async with collection.find({"name": "delete_me"}) as cursor:
            docs = await cursor.to_list()
            assert len(docs) == 0

    @pytest.mark.asyncio
    async def test_succeeds_if_missing_svg(self, datastore: ModelsDatastore):
        """
        Validate that deleting a model works if the SVG file is missing.
        """
        # Arrange
        db = datastore.db.client["test_db"]
        collection = db[datastore.db_config.definition_collection]
        model_data = BpmnModelData(name="delete_me", source="<xml/>", svg="<svg/>")
        bpmn_path = datastore.definitions_path.joinpath("delete_me.bpmn")
        bpmn_path.touch()
        await datastore.save_model(model_data)

        # Act
        await datastore.delete_model("delete_me")

        # Assert
        assert not bpmn_path.exists()
        async with collection.find({"name": "delete_me"}) as cursor:
            docs = await cursor.to_list()
            assert len(docs) == 0


class TestRenameModel:
    """Tests for the ModelsDatastore.rename_model method."""

    @pytest.mark.asyncio
    async def test_updates_db_and_renames_files(self, datastore: ModelsDatastore):
        """
        Ensure that renaming a model updates the name field in the database and renames the corresponding files.
        """
        # Arrange
        db = datastore.db.client["test_db"]
        collection = db[datastore.db_config.definition_collection]
        model_data = BpmnModelData(name="old", source="<xml/>", svg="<svg/>")
        bpmn_path = datastore.definitions_path.joinpath("old.bpmn")
        new_bpmn_path = datastore.definitions_path.joinpath("new.bpmn")
        svg_path = datastore.definitions_path.joinpath("old.svg")
        new_svg_path = datastore.definitions_path.joinpath("new.svg")
        bpmn_path.touch()
        svg_path.touch()
        await datastore.save_model(model_data)

        # Act
        success = await datastore.rename_model("old", "new")

        # Assert
        assert success
        assert new_bpmn_path.exists()
        assert new_svg_path.exists()
        assert not bpmn_path.exists()
        assert not svg_path.exists()

        async with collection.find({"name": "new"}) as cursor:
            docs = await cursor.to_list()
            assert len(docs) == 1

    @pytest.mark.asyncio
    async def test_suceeds_if_missing_svg(self, datastore: ModelsDatastore):
        """
        Ensure that renaming a model works if the SVG file is missing.
        """
        # Arrange
        db = datastore.db.client["test_db"]
        collection = db[datastore.db_config.definition_collection]
        model_data = BpmnModelData(name="old", source="<xml/>", svg="<svg/>")
        bpmn_path = datastore.definitions_path.joinpath("old.bpmn")
        new_bpmn_path = datastore.definitions_path.joinpath("new.bpmn")
        bpmn_path.touch()
        await datastore.save_model(model_data)

        # Act
        success = await datastore.rename_model("old", "new")

        # Assert
        assert success
        assert new_bpmn_path.exists()
        assert not bpmn_path.exists()

        async with collection.find({"name": "new"}) as cursor:
            docs = await cursor.to_list()
            assert len(docs) == 1


class TestGetList:
    """Tests for the ModelsDatastore.get_list method."""

    @pytest.mark.asyncio
    async def test_get_list_finds_files_on_disk(self, datastore: ModelsDatastore):
        """
        It correctly scans the definitions directory and returns a list of model names found on the filesystem.
        """
        # Arrange
        mock_file = MagicMock(spec=Path)
        mock_file.stem = "process_a"

        with patch("pathlib.Path.exists", return_value=True), patch("pathlib.Path.glob", return_value=[mock_file]):
            # Act
            results = await datastore.get_list()

            # Assert
            assert len(results) == 1
            assert results[0]["name"] == "process_a"
