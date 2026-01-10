"""MongoDB datastore implementation using PyMongo."""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional

from bson.objectid import ObjectId
from pymongo import AsyncMongoClient

if TYPE_CHECKING:
    from pymongo.results import DeleteResult, InsertManyResult, UpdateResult

    from pybpmn_server.common.configuration import MongoDBSettings

logger = logging.getLogger(__name__)


@contextmanager
def profile(mongo_db: MongoDB, operation: str) -> Generator[None, None, None]:
    """Context manager for profiling."""
    can_profile = mongo_db.db_config.enable_profiler
    start_time = time.time() if can_profile else None

    yield

    if can_profile and start_time:
        duration = (time.time() - start_time) * 1000
        logger.debug(f"{operation}: {duration:.3f}ms")


class MongoDB:
    """MongoDB datastore implementation using PyMongo."""

    def __init__(self, db_config: MongoDBSettings):
        self.db_config = db_config
        self.client = AsyncMongoClient(self.db_config.db_url)

    async def find(
        self,
        db_name: str,
        coll_name: str,
        qry: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """Finds documents matching query; applies projection/sort; returns results."""
        db = self.client[db_name]
        collection = db[coll_name]

        with profile(self, f">mongo.find:{coll_name}"):
            async with collection.find(qry, projection=projection, sort=sort) as cursor:
                docs = await cursor.to_list()

        return docs

    async def create_index(self, db_name: str, coll_name: str, index: Any, unique: bool = False) -> Optional[str]:
        """Creates an index on a collection."""
        db = self.client[db_name]
        collection = db[coll_name]

        with profile(self, f">mongo.create_index:{coll_name}"):
            result = await collection.create_index(index, unique=unique)
            logger.info(f'index named "{result}" was created for collection "{coll_name}"')
            return result

    async def insert(self, db_name: str, coll_name: str, docs: List[Dict[str, Any]]) -> int:
        """Insert documents into collection."""
        db = self.client[db_name]
        collection = db[coll_name]

        with profile(self, f">mongo.insert:{coll_name}"):
            result: InsertManyResult = await collection.insert_many(docs)

        return len(result.inserted_ids)

    async def update(
        self,
        db_name: str,
        coll_name: str,
        query: Dict[str, Any],
        update_object: Dict[str, Any],
        upsert: bool = False,
    ) -> int:
        """Updates documents in collection."""
        db = self.client[db_name]
        collection = db[coll_name]

        with profile(self, f">mongo.update:{coll_name}"):
            result: UpdateResult = await collection.update_one(query, update_object, upsert=upsert)

        logger.info(f" updated {result.modified_count}")
        return result.modified_count

    async def update2(
        self,
        db_name: str,
        coll_name: str,
        query: Dict[str, Any],
        update_object: Dict[str, Any],
        upsert: bool = False,
    ) -> int:
        """Updates documents in collection."""
        # In TS, update2 uses collection.update which might be updateMany or just update with different defaults
        # For parity, I'll use update_many here if it was meant to be that, but TS code shows collection.update
        # which is deprecated. I'll use update_one or update_many.
        # Given the name update2, it might be updateMany.
        db = self.client[db_name]
        collection = db[coll_name]

        with profile(self, f">mongo.update:{coll_name}"):
            result: UpdateResult = await collection.update_many(query, update_object, upsert=upsert)

        logger.info(f" updated {result.modified_count}")
        return result.modified_count

    async def remove(self, db_name: str, coll_name: str, query: Dict[str, Any]) -> int:
        """Remove documents matching query."""
        db = self.client[db_name]
        collection = db[coll_name]

        with profile(self, f">mongo.remove:{coll_name}"):
            result: DeleteResult = await collection.delete_many(query)

        logger.info(f"remove done for {result.deleted_count} docs in {coll_name}")
        return result.deleted_count

    async def remove_by_id(self, db_name: str, coll_name: str, id_: str) -> int:
        """Remove a document by its id."""
        db = self.client[db_name]
        collection = db[coll_name]

        with profile(self, f">mongo.remove_by_id:{coll_name}"):
            result: DeleteResult = await collection.delete_one({"_id": ObjectId(id_)})
            logger.info(f"remove done for {id_} > {result.deleted_count}")
            return result.deleted_count
