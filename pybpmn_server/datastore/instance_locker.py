"""Instance locking component for managing concurrent access to workflow instances."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from pymongo.errors import PyMongoError

if TYPE_CHECKING:
    from pybpmn_server.datastore.data_store import DataStore

logger = logging.getLogger(__name__)


class InstanceLocker:
    """Instance locking component for managing concurrent access to workflow instances."""

    def __init__(self, datastore: DataStore):
        self.datastore = datastore
        self.db_config = datastore.db_configuration
        self.client = datastore.db
        self.db_name = self.db_config.db
        self.collection = self.db_config.locks_collection

    async def lock(self, id_: str) -> bool:
        """Lock the instance with the given id."""
        query = {"id": id_}
        update = {"$set": {"id": id_, "time": datetime.now()}}

        try:
            await self.client.update(self.db_name, self.collection, query, update, upsert=True)
            logger.info(f"Locked instance {id_}")
            return True
        except PyMongoError as err:
            logger.error(f"Failed to lock instance {id_}: {err}", exc_info=True)
            return False

    async def release(self, id_: str) -> bool:
        """Release the lock for the instance with the given id."""
        query = {"id": id_}

        try:
            await self.client.remove(self.db_name, self.collection, query)
            logger.info(f"Released lock for instance {id_}")
            return True
        except PyMongoError as err:
            logger.error(f"Failed to release lock for instance {id_}: {err}", exc_info=True)
            return False

    async def is_locked(self, id_: str) -> bool:
        """Check if the instance with the given id is locked."""
        query = {"id": id_}

        try:
            records = await self.client.find(self.db_name, self.collection, query)
            return len(records) > 0
        except PyMongoError as err:
            logger.error(f"Failed to check lock for instance {id_}: {err}", exc_info=True)
            return False
