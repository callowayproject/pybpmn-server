"""Aggregate class for performing find operations on the database."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from pybpmn_server.interfaces.datastore import FindResult

if TYPE_CHECKING:
    from pybpmn_server.datastore.mongodb import MongoDB
    from pybpmn_server.interfaces.datastore import FindParams


class Aggregate:
    """
    Aggregate class for performing find operations on the database.

    MongoDB Pagination class for finding instances in a collection.
    This module provides a function to retrieve paginated results from a MongoDB collection.
    It allows filtering, sorting, and projecting fields in the results.
    The results can be paginated using a cursor for efficient data retrieval.
    All the parameters are optional and are passed to the findInstances method.
    `sort` fields can be specified as an object with field names as keys and 1 (ascending) or -1 (descending) as values
       Sort by `_id` in descending order by default.
       Sort field can be a nested field, e.g., `data.caseId`
        *  Sort field can be a numeric or date field.
    `filter` is an object that specifies the criteria for filtering the results.
    `after` is a string that specifies the cursor for pagination, allowing results retrieval after a specific document.
    `limit` is a number that specifies the maximum number of documents to return in the result set.
    `projection` is an object that specifies which fields to include or exclude in the returned documents.
    """

    def __init__(self, mongo_db: MongoDB):
        self.mongo_db = mongo_db
        self.db_configuration = mongo_db.db_config
        client = self.mongo_db.client
        db = client[self.db_configuration.db]
        self.collection = db[self.db_configuration.instance_collection]

    async def find(self, params: FindParams) -> FindResult:
        """Perform find operation on the database using provided parameters."""
        filters = params.filter or {}
        match_items = {k: v for k, v in filters.items() if k.startswith("items.")}
        include_items = bool(match_items)
        match_instances = {k: v for k, v in filters.items() if not k.startswith("items.")}

        # 1. Add filter
        pipeline: List[Dict[str, Any]] = [{"$match": match_instances}]

        # 2. Add last_item if needed (legacy support)
        if params.last_item and len(params.last_item) > 0:
            pipeline.append({"$addFields": {"last_item": {"$arrayElemAt": ["$items", -1]}}})
            pipeline.append({"$match": params.last_item})

        # latest_item is more complex in TS, skipped there as well

        # 3. Handle Pagination Cursor (After)
        if params.after:
            cursor_doc = await self.collection.find_one({"_id": params.after})

            if cursor_doc:
                sort_field = next(iter(params.sort.keys())) if params.sort else "_id"
                sort_order = params.sort[sort_field] if params.sort else -1
                operator = "$gt" if sort_order == 1 else "$lt"
                pipeline.append(
                    {
                        "$match": {
                            "$or": [
                                {sort_field: {operator: cursor_doc[sort_field]}},
                                {sort_field: cursor_doc[sort_field], "_id": {operator: cursor_doc["_id"]}},
                            ]
                        }
                    }
                )

        # 4. Add Sort
        if params.sort:
            sort_config = params.sort.copy()
            sort_config["_id"] = params.sort[next(iter(params.sort.keys()))]
            pipeline.append({"$sort": sort_config})
        else:
            pipeline.append({"$sort": {"_id": -1}})

        # 5. Add Limit
        pipeline.append({"$limit": params.limit or 10})

        # 6. Add Projection
        if params.projection:
            pipeline.append({"$project": params.projection})

        if include_items:
            pipeline.extend([{"$unwind": "$items"}, {"$match": match_items}])

        data = await self.collection.aggregate(pipeline)
        data_list = await data.to_list(length=params.limit or 10)

        total_count = None
        if params.get_total_count:
            total_count = await self.collection.count_documents(params.filter or {})

        next_cursor = str(data_list[-1]["_id"]) if data_list else None

        return FindResult(data=data_list, next_cursor=next_cursor, total_count=total_count)

    # def find2(self, params: FindParams) -> FindResult:
    #     """My alternate version of find."""
    #     match_items = {k: v for k, v in params.filter.items() if k.startswith("items.")}
    #     include_items = bool(match_items)
    #     match_instances = {k: v for k, v in params.filter.items() if not k.startswith("items.")}
    #
    #     sort_field = next(iter(params.sort.keys())) if params.sort else "_id"
    #     sort_value = params.sort[sort_field]
    #     sort_direction = params.sort[sort_field] if params.sort else -1
    #
    #     sort_field_is_date = False


# def do_after(
#     after: str,
#     sort_field: str,
#     sort_direction: int,
#     match_instances: Optional[dict[str, Any]] = None,
#     match_items: Optional[dict[str, Any]] = None,
# ) -> tuple[dict[str, Any], dict[str, Any]]:
#     match_instances = match_instances or {}
#     match_items = match_items or {}
#
#     if not after:
#         return match_instances, match_items
#
#     if sort_field == "_id" or "|" not in after:
#         sort_val_raw = after
#         id_part = None
#     else:
#         sort_val_raw, id_part = after.split("|")
#
#     sort_field_is_date = False
#
#     if sort_val_raw.startswith("d:"):
#         sort_field_is_date = True
#         sort_val = datetime.datetime.fromtimestamp(int(sort_val_raw[2:]), tz=datetime.timezone.utc)
#     elif sort_val_raw.isdigit():
#         sort_val = int(sort_val_raw)
#     else:
#         sort_val = sort_val_raw
#
#     comparator = "$lt" if sort_direction == -1 else "$gt"
#
#     if sort_field == "_id":
#         match_instances["_id"] = {comparator: ObjectId(sort_val_raw)}
#     else:
#         match_items["$and"] = match_items.get("$and", [])
#         if sort_field.startswith("items."):
#             sort_field_2 = sort_field[6:]
#             match_items["$and"].append(
#                 {
#                     "$or": [
#                         {sort_field_2: {comparator: sort_val}, "_id": {"$ne": ObjectId(id_part)}},
#                         {sort_field_2: sort_val, "_id": {comparator: ObjectId(id_part)}},
#                     ]
#                 }
#             )
#         else:
#             match_instances["$and"].append(
#                 {
#                     "$or": [
#                         {sort_field: {comparator: sort_val}, "_id": {"$ne": ObjectId(id_part)}},
#                         {sort_field: sort_val, "_id": {comparator: ObjectId(id_part)}},
#                     ]
#                 }
#             )
#     return match_instances, match_items
