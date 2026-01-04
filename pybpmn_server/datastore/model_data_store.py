"""ModelsDatastore for BPMN."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from pybpmn_server.common.configuration import MongoDBSettings, settings
from pybpmn_server.datastore.data_objects import BpmnModelData, EventData
from pybpmn_server.datastore.interfaces import IModelsDatastore
from pybpmn_server.datastore.mongodb import MongoDB
from pybpmn_server.datastore.query_translator import QueryTranslator
from pybpmn_server.elements.interfaces import IDefinition


class ModelsDatastore(IModelsDatastore):
    """ModelsDatastore for BPMN."""

    def __init__(self, definitions_path: Optional[Path] = None, db_configuration: MongoDBSettings = None):
        if not db_configuration and not settings.database_settings:
            raise Exception("Database configuration is not set")
        if not isinstance(settings.database_settings, MongoDBSettings):
            raise Exception("Database configuration is not of type MongoDBSettings")
        self.db_config = db_configuration or settings.database_settings
        self.db = MongoDB(self.db_config)
        self.definitions_path = definitions_path or settings.definitions_path

    async def import_model(self, data: BpmnModelData) -> int:
        """Import an BPMN model."""
        return await self.db.insert(self.db_config.db, self.db_config.definition_collection, [data.model_dump()])

    async def get(self, query: dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve models from the database based on the provided query."""
        return await self.db.find(self.db_config.db, self.db_config.definition_collection, query)

    async def load_model(self, name: str) -> Optional[BpmnModelData]:
        """Load a BPMN model from the database."""
        results = await self.db.find(self.db_config.db, self.db_config.definition_collection, {"name": name})
        if results:
            return BpmnModelData(**results[0])
        return None

    async def find_events(self, query: dict[str, Any]) -> List[EventData]:
        """Find events in the database based on the provided query."""
        translation = QueryTranslator("events")
        new_query = translation.translate_criteria(query)
        results = await self.db.find(self.db_config.db, self.db_config.definition_collection, new_query)
        events: List[EventData] = []

        for record in results:
            for event in record.get("events", []):
                is_valid = translation.filter_item(event, new_query)
                if not is_valid:
                    continue
                events.append(EventData(**record))

        return events

    async def install(self) -> None:
        """The first time installation of the DB creates a new collection and adds an index."""
        await self.db.create_index(self.db_config.db, self.db_config.definition_collection, {"name": 1}, unique=True)

    # async def update_timer(self, name: str) -> bool:
    #     """Update a BPMN timer from the database."""
    #     from pybpmn_server.elements.definition import Definition
    #
    #     source = await self.get_source(name)
    #     model = BpmnModelData(name=name, source=source, svg="")
    #     definition = Definition(name, source)
    #     await definition.load()
    #     query = {"name": name}
    #     update_obj = {"$set": {"events": model.events}}
    #     await self.db.update(self.db_config.db, self.db_config.definition_collection, query, update_obj, upsert=False)

    async def save_model(self, model: BpmnModelData) -> bool:
        """Save a BPMN model to the database."""
        model.saved = datetime.now(tz=timezone.utc)
        data = model.model_dump()
        update_obj = {"$set": data}
        await self.db.update(
            self.db_config.db, self.db_config.definition_collection, {"name": model.name}, update_obj, upsert=True
        )
        return True

    async def delete_model(self, name: str) -> None:
        """Delete a BPMN model from the database."""
        num_deleted = await self.db.remove(self.db_config.db, self.db_config.definition_collection, {"name": name})

        if num_deleted != 1:
            return None

        for ext in [".bpmn", ".svg"]:
            file_path = self.definitions_path / f"{name}{ext}"
            try:
                if file_path.exists():
                    file_path.unlink()
            except OSError as e:
                print(f"ERROR: {e}")
                return None

    async def rename_model(self, name: Any, new_name: Any) -> bool:
        """Rename a BPMN model from the database."""
        num_updated = await self.db.update(
            self.db_config.db,
            self.db_config.definition_collection,
            {"name": name},
            {"$set": {"name": new_name}},
            upsert=False,
        )

        if num_updated != 1:
            return False

        for ext in [".bpmn", ".svg"]:
            old_path = self.definitions_path / f"{name}{ext}"
            new_path = self.definitions_path / f"{new_name}{ext}"
            try:
                if old_path.exists():
                    old_path.rename(new_path)
            except OSError as e:
                print(f"ERROR: {e}")
                return False
        return True

    async def get_list(self, query: Optional[dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve models from the filesystem based on the provided query."""
        files = []
        path = self.definitions_path

        if path.exists():
            for file in path.glob("*.bpmn"):
                # name without .bpmn extension
                name = file.stem
                files.append({"name": name, "saved": None})

        return files

    async def load(self, name: str, owner: Optional[str] = None) -> IDefinition:
        """Load a BPMN model from the database."""
        from pybpmn_server.elements.definition import Definition

        source = await self.get_source(name)
        # TODO (pybpmn-server-bwr): Re-Implement
        # rules = self.get_file(name, 'rules')

        definition = Definition(name, source)
        await definition.load()
        return definition

    def _get_file(self, name: str, file_type: str) -> str:
        """Retrieve a BPMN model file from the filesystem."""
        file_path = self.definitions_path / f"{name}.{file_type}"
        return file_path.read_text(encoding="utf-8")

    def _save_file(self, name: str, file_type: str, data: str) -> None:
        """Save a BPMN model file from the filesystem."""
        file_path = self.definitions_path / f"{name}.{file_type}"
        file_path.write_text(data, encoding="utf-8")

    async def get_source(self, name: str, owner: Optional[str] = None) -> str:
        """Retrieve a BPMN source from the filesystem."""
        return self._get_file(name, "bpmn")

    async def get_svg(self, name: str, owner: Optional[str] = None) -> str:
        """Retrieve a BPMN svg from the filesystem."""
        return self._get_file(name, "svg")

    async def save(self, name: str, bpmn: str, svg: Optional[str] = None, owner: Optional[str] = None) -> bool:
        """Save a BPMN model to the database."""
        model = BpmnModelData(name=name, source=bpmn, svg=svg or "")
        return await self.save_model(model)

    async def rebuild(self, model: Optional[str] = None) -> Any:
        """Rebuild the model database from the filesystem."""
        try:
            if model:
                return await self._rebuild_model(model)

            files_list = await self.get_list()
            models_on_disk: Dict[str, float] = {}

            for f in files_list:
                name = f["name"]
                path = self.definitions_path / f"{name}.bpmn"
                if path.exists():
                    mtime = path.stat().st_mtime
                    models_on_disk[name] = mtime

            db_list = await self.get({})
            for model_entry in db_list:
                name = model_entry["name"]
                # Assuming 'saved' is a timestamp or isoformat string
                saved_val = model_entry["saved"]
                saved_time = datetime.fromisoformat(saved_val).timestamp() if isinstance(saved_val, str) else saved_val

                entry_mtime = models_on_disk.get(name)
                if entry_mtime:
                    if saved_time > entry_mtime:
                        del models_on_disk[name]
                else:
                    await self.delete_model(name)

            for name in models_on_disk:
                await self._rebuild_model(name)

        except Exception as exc:
            print("rebuild error")
            raise exc

    async def _rebuild_model(self, name: str) -> None:
        print(f"rebuilding {name}")
        source = await self.get_source(name)
        svg = None
        import contextlib

        with contextlib.suppress(FileNotFoundError):
            svg = await self.get_svg(name)

        await self.save(name, source, svg)
