"""Data store component for managing workflow data and instances."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

from pydantic import ValidationError

from pybpmn_server.common.default_configuration import MongoDBSettings, settings
from pybpmn_server.datastore.aggregate import Aggregate
from pybpmn_server.datastore.data_objects import InstanceDataList
from pybpmn_server.datastore.instance_locker import InstanceLocker
from pybpmn_server.datastore.interfaces import FindParams, FindResult, IDataStore
from pybpmn_server.datastore.mongodb import MongoDB
from pybpmn_server.datastore.query_translator import QueryTranslator
from pybpmn_server.engine import data_handler

if TYPE_CHECKING:
    from pybpmn_server.datastore.data_objects import InstanceData, ItemData

logger = logging.getLogger(__name__)


def _get_items_from_instances(
    instances: List[InstanceData], condition: Any = None, trans: QueryTranslator = None
) -> List[ItemData]:
    items = []
    for instance in instances:
        instance_items = instance.items or []

        # Augments and collects items passing filter condition
        for item in instance_items:
            pass_filter = trans.filter_item(item, condition) if trans else True
            if not pass_filter:
                continue

            data = instance.data or {}
            token_id = item.token_id
            tokens = instance.tokens or []
            token = None
            for t in tokens:
                if t.id == token_id:
                    token = t
                    break

            item_data = data_handler.get_data(data, token.data_path) if token and token.data_path else {}

            item.process_name = instance.name
            item.instance_data = data
            item.data = item_data
            item.instance_id = instance.id
            item.instance_version = instance.version
            items.append(item)

    items.sort(key=lambda x: x.seq or 0)
    return items


class DataStore(IDataStore):
    """Data store component for managing workflow data and instances."""

    def __init__(self, db_configuration: MongoDBSettings = None):
        if not db_configuration and not settings.database:
            raise Exception("Database configuration is not set")
        if not isinstance(settings.database, MongoDBSettings):
            raise Exception("Database configuration is not of type MongoDBSettings")
        self.db_config = db_configuration or settings.database
        self.db = MongoDB(self.db_config)
        self.locker = InstanceLocker(self)

        self.is_modified = False
        self.is_running = False
        self.in_saving = False
        self.enable_save_points = False
        self.save_logs = True
        self.save_source = True

    async def save(self, instance: InstanceData) -> None:
        """Save instance data."""
        await self.save_instance(instance)

    async def load_instance(self, instance_id: str) -> Optional[dict[str, Any]]:
        """Load instance data by id."""
        recs = await self.find_instances({"id": instance_id}, "full")
        if not recs:
            logger.error("Instance is not found for this item")
            return None
        instance_data = recs[0]
        return {"instance": instance_data, "items": _get_items_from_instances([instance_data])}

    async def save_instance(self, instance: InstanceData) -> None:
        """Save instance data."""
        save_object = instance.model_dump()

        if self.save_logs:
            save_object["logs"] = instance.logs
        if self.save_source:
            save_object["source"] = instance.source

        if self.enable_save_points and instance.items:
            last_item = instance.items[-1]
            last_item_id = last_item.id if hasattr(last_item, "id") else last_item.get("id")
            save_point = {
                "id": last_item_id,
                "items": instance.items,
                "loops": instance.loops,
                "tokens": instance.tokens,
                "data": instance.data,
            }
            if not hasattr(instance, "save_points") or not instance.save_points:
                instance.save_points = {}
            instance.save_points[last_item_id] = save_point
            save_object["savePoints"] = instance.save_points

        if not instance.saved:
            instance.saved = datetime.now()
            save_object["saved"] = instance.saved
            save_object["id"] = instance.id
            await self.db.insert(self.db_config.db, self.db_config.instance_collection, [save_object])
        else:
            await self.db.update(
                self.db_config.db,
                self.db_config.instance_collection,
                {"id": instance.id},
                {"$set": save_object},
            )

        logger.info("..DataStore:saving Complete")

    async def find_item(self, query: Any) -> ItemData:
        """Find an item based on the given query."""
        results = await self.find_items(query)
        if not results:
            raise Exception(f"No items found for {query}")
        if len(results) > 1:
            raise Exception(f"More than one record found {len(results)} {query}")
        return results[0]

    async def find_instance(self, query: Any, options: Any) -> InstanceData:
        """Find an instance based on the given query."""
        results = await self.find_instances(query, options)
        if not results:
            raise Exception(f"No instance found for {query}")
        if len(results) > 1:
            raise Exception(f"More than one record found {len(results)} {query}")
        rec = results[0]
        if "logs" not in rec:
            rec["logs"] = []
        return rec

    async def find_instances(self, query: Any, option: Any = "summary") -> List[InstanceData]:
        """Find instances based on the given query."""
        projection = None
        sort = None

        if option == "summary":
            projection = {"source": 0, "logs": 0}
        elif isinstance(option, dict):
            projection = option.get("projection")
            sort = option.get("sort")
        elif option == "full":
            projection = None

        records = await self.db.find(self.db_config.db, self.db_config.instance_collection, query, projection, sort)

        try:
            doc_list = InstanceDataList.validate_python(records)
        except ValidationError as e:
            logger.error(f"Validation error in find instances: {e}")
            raise

        return doc_list

    async def find_items(self, query: Any) -> List[ItemData]:
        """Find items based on the given query."""
        trans = QueryTranslator("items")
        result = trans.translate_criteria(query)
        projection = {"id": 1, "data": 1, "name": 1, "version": 1, "items": 1, "tokens": 1}
        records = await self.db.find(self.db_config.db, self.db_config.instance_collection, result, projection)

        try:
            doc_list = InstanceDataList.validate_python(records)
        except ValidationError as e:
            logger.error(f"Validation error in find instances: {e}")
            raise

        return _get_items_from_instances(doc_list, result, trans)

    async def delete_instances(self, query: Optional[Any] = None) -> None:
        """Delete instances matching the query."""
        await self.db.remove(self.db_config.db, self.db_config.instance_collection, query or {})

    async def install(self) -> None:
        """Install indexes required for the data store."""
        await self.db.create_index(self.db_config.db, self.db_config.instance_collection, [("id", 1)], unique=True)
        await self.db.create_index(self.db_config.db, self.db_config.instance_collection, [("items.id", 1)])
        await self.db.create_index(self.db_config.db, self.db_config.locks_collection, [("id", 1)], unique=True)

    async def archive(self, query: Any) -> None:
        """Archive instances matching the query."""
        docs = await self.db.find(self.db_config.db, self.db_config.instance_collection, query)
        if docs:
            await self.db.insert(self.db_config.db, self.db_config.archive_collection, docs)
            await self.delete_instances(query)
        logger.info(f"total of {len(docs)} archived")

    async def find(self, params: FindParams) -> FindResult:
        """Perform find operation on the database using provided parameters."""
        aggregate = Aggregate(self.db)
        return await aggregate.find(params)
