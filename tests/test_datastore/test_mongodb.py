"""Tests for the mongodb module."""

from unittest.mock import MagicMock

import pytest
from bson.objectid import ObjectId

from pybpmn_server.common.default_configuration import MongoDBSettings
from pybpmn_server.datastore.mongodb import MongoDB, profile


class TestProfile:
    """Tests for the profile context manager."""

    def test_profile_prints_duration_when_enabled(self, mocker, capsys):
        """
        The profile context manager prints the duration of the operation when 'enable_profiler' is set to True.
        """
        # Arrange
        db_config = MongoDBSettings(enable_profiler=True)
        mongo_db = mocker.MagicMock(spec=MongoDB)
        mongo_db.db_config = db_config

        # Act
        with profile(mongo_db, "test_op"):
            pass

        # Assert
        captured = capsys.readouterr()
        assert "test_op:" in captured.out
        assert "ms" in captured.out

    def test_profile_does_not_print_when_disabled(self, mocker, capsys):
        """
        The profile context manager does not print anything when 'enable_profiler' is set to False.
        """
        # Arrange
        db_config = MongoDBSettings(enable_profiler=False)
        mongo_db = mocker.MagicMock(spec=MongoDB)
        mongo_db.db_config = db_config

        # Act
        with profile(mongo_db, "test_op"):
            pass

        # Assert
        captured = capsys.readouterr()
        assert not captured.out


class TestMongoDB:
    """Tests for the MongoDB class."""

    @pytest.fixture
    def db_config(self) -> MongoDBSettings:
        """Returns a MongoDBSettings instance with default values."""
        return MongoDBSettings(db_url="mongodb://localhost:27017", enable_profiler=False)

    @pytest.fixture
    def mock_client(self, mocker) -> MagicMock:
        """Returns a mock for the MongoClient class."""
        return mocker.patch("pybpmn_server.datastore.mongodb.MongoClient")

    def test_init_sets_config_and_client(self, db_config, mock_client):
        """
        The MongoDB class correctly initializes with the provided database configuration and creates a MongoClient.
        """
        # Act
        mongo_db = MongoDB(db_config)

        # Assert
        assert db_config == mongo_db.db_config
        mock_client.assert_called_once_with(db_config.db_url)

    @pytest.mark.asyncio
    async def test_find_returns_documents(self, db_config, mock_client):
        """
        Tests that the find method correctly queries the database and returns a list
        of documents matching the query, applying projections and sorting as expected.
        """
        # Arrange
        mongo_db = MongoDB(db_config)
        mock_db = mock_client.return_value["test_db"]
        mock_coll = mock_db["test_coll"]
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [{"_id": "1", "name": "test"}]
        mock_coll.find.return_value = mock_cursor

        query = {"name": "test"}
        projection = {"name": 1}
        sort = [("name", 1)]

        # Act
        result = await mongo_db.find("test_db", "test_coll", query, projection=projection, sort=sort)

        # Assert
        assert result == [{"_id": "1", "name": "test"}]
        mock_coll.find.assert_called_once_with(query, projection=projection, sort=sort)

    @pytest.mark.asyncio
    async def test_create_index_returns_index_name(self, db_config, mock_client):
        """
        Tests that the create_index method correctly calls the PyMongo create_index
        method and returns the name of the created index.
        """
        # Arrange
        mongo_db = MongoDB(db_config)
        mock_coll = mock_client.return_value["test_db"]["test_coll"]
        mock_coll.create_index.return_value = "idx_name"

        # Act
        result = await mongo_db.create_index("test_db", "test_coll", "field", unique=True)

        # Assert
        assert result == "idx_name"
        mock_coll.create_index.assert_called_once_with("field", unique=True)

    @pytest.mark.asyncio
    async def test_insert_returns_inserted_count(self, db_config, mock_client):
        """
        Tests that the insert method correctly calls the PyMongo insert_many
        method and returns the number of successfully inserted documents.
        """
        # Arrange
        mongo_db = MongoDB(db_config)
        mock_coll = mock_client.return_value["test_db"]["test_coll"]
        mock_result = MagicMock()
        mock_result.inserted_ids = [ObjectId(), ObjectId()]
        mock_coll.insert_many.return_value = mock_result

        docs = [{"a": 1}, {"b": 2}]

        # Act
        result = await mongo_db.insert("test_db", "test_coll", docs)

        # Assert
        assert result == 2
        mock_coll.insert_many.assert_called_once_with(docs)

    @pytest.mark.asyncio
    async def test_update_returns_modified_count(self, db_config, mock_client):
        """
        Tests that the update method correctly calls the PyMongo update_one
        method and returns the number of documents modified by the operation.
        """
        # Arrange
        mongo_db = MongoDB(db_config)
        mock_coll = mock_client.return_value["test_db"]["test_coll"]
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_coll.update_one.return_value = mock_result

        query = {"_id": "1"}
        update_obj = {"$set": {"name": "new"}}

        # Act
        result = await mongo_db.update("test_db", "test_coll", query, update_obj, upsert=True)

        # Assert
        assert result == 1
        mock_coll.update_one.assert_called_once_with(query, update_obj, upsert=True)

    @pytest.mark.asyncio
    async def test_update2_returns_modified_count(self, db_config, mock_client):
        """
        Tests that the update2 method correctly calls the PyMongo update_many
        method and returns the number of documents modified by the operation.
        """
        # Arrange
        mongo_db = MongoDB(db_config)
        mock_coll = mock_client.return_value["test_db"]["test_coll"]
        mock_result = MagicMock()
        mock_result.modified_count = 5
        mock_coll.update_many.return_value = mock_result

        query = {"status": "old"}
        update_obj = {"$set": {"status": "new"}}

        # Act
        result = await mongo_db.update2("test_db", "test_coll", query, update_obj, upsert=False)

        # Assert
        assert result == 5
        mock_coll.update_many.assert_called_once_with(query, update_obj, upsert=False)

    @pytest.mark.asyncio
    async def test_remove_returns_deleted_count(self, db_config, mock_client):
        """
        Tests that the remove method correctly calls the PyMongo delete_many
        method and returns the number of documents removed from the collection.
        """
        # Arrange
        mongo_db = MongoDB(db_config)
        mock_coll = mock_client.return_value["test_db"]["test_coll"]
        mock_result = MagicMock()
        mock_result.deleted_count = 3
        mock_coll.delete_many.return_value = mock_result

        query = {"type": "temp"}

        # Act
        result = await mongo_db.remove("test_db", "test_coll", query)

        # Assert
        assert result == 3
        mock_coll.delete_many.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_remove_by_id_returns_deleted_count(self, db_config, mock_client):
        """
        Tests that the remove_by_id method correctly calls the PyMongo delete_one
        method with a specific ObjectId and returns the number of documents deleted.
        """
        # Arrange
        mongo_db = MongoDB(db_config)
        mock_coll = mock_client.return_value["test_db"]["test_coll"]
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        mock_coll.delete_one.return_value = mock_result

        obj_id_str = "6587dab5f1593c6f0a40d6c1"

        # Act
        result = await mongo_db.remove_by_id("test_db", "test_coll", obj_id_str)

        # Assert
        assert result == 1
        mock_coll.delete_one.assert_called_once_with({"_id": ObjectId(obj_id_str)})
