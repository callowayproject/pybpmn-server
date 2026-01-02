"""Tests for the mongodb module."""

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from bson.objectid import ObjectId

from pybpmn_server.common.configuration import MongoDBSettings
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
        return MongoDBSettings(db_url="mongodb://localhost:27017", enable_profiler=False, db="test_db")

    @pytest_asyncio.fixture
    async def mongo_db(self, db_config) -> AsyncGenerator[MongoDB, None]:
        """Returns a MongoDBSettings instance with default values."""
        mongo_db = MongoDB(db_config)
        db = mongo_db.client["test_db"]
        await db.create_collection("test_coll")

        yield mongo_db

        await mongo_db.client.drop_database("test_db")

    @pytest.mark.asyncio
    async def test_find_returns_documents(self, mongo_db):
        """
        Tests that the find method correctly queries the database and returns a list of documents matching the query.

        It should apply projections and sorting as expected.
        """
        # Arrange
        db = mongo_db.client["test_db"]
        collection = db["test_coll"]
        await collection.insert_many([{"_id": "1", "name": "test"}])

        query = {"name": "test"}
        projection = {"name": 1}
        sort = [("name", 1)]

        # Act
        result = await mongo_db.find("test_db", "test_coll", query, projection=projection, sort=sort)

        # Assert
        assert result == [{"_id": "1", "name": "test"}]

    @pytest.mark.asyncio
    async def test_create_index_returns_index_name(self, mongo_db):
        """
        Tests that the create_index method correctly calls the PyMongo create_index method and returns the name.
        """
        # Arrange

        # Act
        result = await mongo_db.create_index("test_db", "test_coll", "field", unique=True)

        # Assert
        assert result == "field_1"

    @pytest.mark.asyncio
    async def test_insert_returns_inserted_count(self, mongo_db):
        """
        Tests that the insert method correctly calls the PyMongo insert_many method and returns the number inserted.
        """
        # Arrange
        docs = [{"a": 1}, {"b": 2}]

        # Act
        result = await mongo_db.insert("test_db", "test_coll", docs)

        # Assert
        assert result == 2

    @pytest.mark.asyncio
    async def test_update_returns_modified_count(self, mongo_db):
        """
        Tests that the update method correctly calls the PyMongo update_one method and returns the number of modified.
        """
        # Arrange
        db = mongo_db.client["test_db"]
        collection = db["test_coll"]
        await collection.insert_one({"_id": "1", "name": "old"})

        query = {"_id": "1"}
        update_obj = {"$set": {"name": "new"}}

        # Act
        result = await mongo_db.update("test_db", "test_coll", query, update_obj, upsert=True)

        # Assert
        assert result == 1
        assert await collection.find_one(query) == {"_id": "1", "name": "new"}

    @pytest.mark.asyncio
    async def test_update2_returns_modified_count(self, mongo_db):
        """
        Tests that the update2 method correctly calls update_many method and returns the number of documents modified.
        """
        # Arrange
        db = mongo_db.client["test_db"]
        mock_coll = db["test_coll"]
        await mock_coll.insert_many([{"index": i, "status": "old"} for i in range(5)])

        query = {"status": "old"}
        update_obj = {"$set": {"status": "new"}}

        # Act
        result = await mongo_db.update2("test_db", "test_coll", query, update_obj, upsert=False)

        # Assert
        assert result == 5
        assert len(await mock_coll.find({"status": "new"}).to_list()) == 5

    @pytest.mark.asyncio
    async def test_remove_returns_deleted_count(self, mongo_db):
        """
        Tests that the remove method correctly calls delete_many and returns the number of documents removed.
        """
        # Arrange
        db = mongo_db.client["test_db"]
        mock_coll = db["test_coll"]
        await mock_coll.insert_many([{"index": i, "type": "temp"} for i in range(3)])

        query = {"type": "temp"}

        # Act
        result = await mongo_db.remove("test_db", "test_coll", query)

        # Assert
        assert result == 3
        assert len(await mock_coll.find(query).to_list()) == 0

    @pytest.mark.asyncio
    async def test_remove_by_id_returns_deleted_count(self, mongo_db):
        """
        Tests that the remove_by_id method correctly calls delete_one with a specific ObjectId.
        """
        # Arrange
        db = mongo_db.client["test_db"]
        mock_coll = db["test_coll"]
        result = await mock_coll.insert_one({"index": 1, "type": "temp"})

        obj_id_str = result.inserted_id

        # Act
        result = await mongo_db.remove_by_id("test_db", "test_coll", obj_id_str)

        # Assert
        assert result == 1
        assert len(await mock_coll.find({"_id": ObjectId(obj_id_str)}).to_list()) == 0
