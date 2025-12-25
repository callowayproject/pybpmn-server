"""Tests for the `Aggregate` class."""

from typing import AsyncGenerator

import pytest
import pytest_asyncio

from pybpmn_server.common.default_configuration import MongoDBSettings
from pybpmn_server.datastore.aggregate import Aggregate
from pybpmn_server.datastore.mongodb import MongoDB
from pybpmn_server.interfaces.datastore import FindParams, FindResult


class TestAggregateFind:
    """Test cases for the `Aggregate.find` method."""

    @pytest.fixture
    def db_config(self) -> MongoDBSettings:
        """Returns a MongoDBSettings instance with default values."""
        return MongoDBSettings(db_url="mongodb://localhost:27017", enable_profiler=False, db="test_db")

    @pytest_asyncio.fixture
    async def mongo_db(self, db_config) -> AsyncGenerator[MongoDB, None]:
        """Returns a MongoDBSettings instance with default values."""
        mongo_db = MongoDB(db_config)
        db = mongo_db.client["test_db"]

        yield mongo_db

        await mongo_db.client.drop_database("test_db")

    @pytest.mark.asyncio
    async def test_find_success(self, mongo_db):
        """
        Test that `find` method retrieves results from the database as expected.
        """
        db = mongo_db.client["test_db"]
        collection = db[mongo_db.db_config.instance_collection]
        await collection.insert_many([{"_id": "doc1", "field1": "value1"}, {"_id": "doc2", "field1": "value1"}])

        aggregate = Aggregate(mongo_db)

        params = FindParams(
            filter={"field1": "value1"},
            limit=2,
            sort={"field1": 1},
            projection={"field1": 1},
            after=None,
            get_total_count=True,
        )

        result = await aggregate.find(params)

        assert isinstance(result, FindResult)
        assert result.data == [{"_id": "doc1", "field1": "value1"}, {"_id": "doc2", "field1": "value1"}]
        assert result.next_cursor == "doc2"
        assert result.total_count == 2

    @pytest.mark.asyncio
    async def test_find_empty_results(self, mongo_db):
        """
        Test that `find` method handles an empty database result correctly.
        """
        aggregate = Aggregate(mongo_db)

        params = FindParams(filter={}, limit=10, sort={"_id": 1}, projection=None)

        result = await aggregate.find(params)

        assert isinstance(result, FindResult)
        assert result.data == []
        assert result.next_cursor is None
        assert result.total_count is None

    @pytest.mark.asyncio
    async def test_find_with_pagination(self, mongo_db):
        """
        Test that `find` method correctly applies cursor-based pagination.
        """
        db = mongo_db.client["test_db"]
        collection = db[mongo_db.db_config.instance_collection]
        await collection.insert_many(
            [
                {"_id": "doc1", "field1": "value10"},
                {"_id": "doc2", "field1": "value11"},
                {"_id": "doc3", "field1": "value12"},
            ]
        )

        aggregate = Aggregate(mongo_db)

        params = FindParams(
            # filter={"field1": "value1"},
            after="doc1",
            limit=2,
            sort={"field1": 1},
            get_total_count=True,
        )

        result = await aggregate.find(params)

        assert isinstance(result, FindResult)
        assert result.data == [
            {"_id": "doc2", "field1": "value11"},
            {"_id": "doc3", "field1": "value12"},
        ]
        assert result.next_cursor == "doc3"
        assert result.total_count == 3

    @pytest.mark.asyncio
    async def test_find_with_projection_and_sort(self, mongo_db):
        """
        Test that `find` method applies projection and sorting correctly.
        """
        db = mongo_db.client["test_db"]
        collection = db[mongo_db.db_config.instance_collection]
        await collection.insert_many(
            [
                {"_id": "doc3", "field1": "value3", "field2": "value3"},
                {"_id": "doc4", "field1": "value4", "field2": "value4"},
            ]
        )

        aggregate = Aggregate(mongo_db)

        params = FindParams(
            filter={"field2": {"$gte": "value2"}},
            limit=2,
            projection={"field1": 1, "field2": 1},
            sort={"field2": -1},
        )

        result = await aggregate.find(params)

        assert isinstance(result, FindResult)
        assert result.data == [
            {"_id": "doc4", "field1": "value4", "field2": "value4"},
            {"_id": "doc3", "field1": "value3", "field2": "value3"},
        ]
        assert result.next_cursor == "doc3"
