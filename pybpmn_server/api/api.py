"""API component for interacting with BPMN processes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from pybpmn_server.api.secure_user import SystemUser
from pybpmn_server.server.bpmn_server import get_server

if TYPE_CHECKING:
    from pybpmn_server.api.secure_user import SecureUser
    from pybpmn_server.common.configuration import Settings
    from pybpmn_server.datastore.data_objects import EventData, InstanceData, ItemData
    from pybpmn_server.elements.interfaces import IDefinition
    from pybpmn_server.engine.interfaces import IExecution
    from pybpmn_server.server.bpmn_server import BPMNServer


class BPMNAPI:
    """API component for interacting with BPMN processes."""

    server: BPMNServer
    engine: APIEngine
    data: APIDataStore
    model: APIModelDataStore
    default_user: Optional[SecureUser] = None

    def __init__(self, server: Optional[BPMNServer] = None):
        self.server = server or get_server()
        self.config = self.server.configuration
        self.engine = APIEngine(self.config)
        self.data = APIDataStore(self.config)
        self.model = APIModelDataStore(self.config)


class APIComponent:
    """Base class for API components."""

    def __init__(self, configuration: Optional[Settings] = None):
        self.config = configuration
        self.default_user = SystemUser

    def get_user(self, user: Optional[SecureUser]) -> SecureUser:
        """Return the user instance."""
        if user is None:
            return self.default_user
        return user


class APIEngine(APIComponent):
    """API component for interacting with the engine."""

    def __init__(self, configuration: Optional[Settings] = None):
        super().__init__(configuration)
        self.engine = self.config.engine

    async def start(
        self,
        name: str,
        source: str,
        data: Optional[Dict[str, Any]] = None,
        user: Optional[SecureUser] = None,
        start_node_id: Optional[str] = None,
        parent_item_id: Optional[str] = None,
        no_wait: bool = False,
    ) -> IExecution:
        """Start a process instance."""
        data = data or {}
        user = self.get_user(user)
        return await self.engine.start(name, source, data, start_node_id, user.user_name, parent_item_id, no_wait)

    async def invoke(
        self,
        query: Any,
        data: Optional[Dict[str, Any]] = None,
        user: Optional[SecureUser] = None,
        restart: bool = False,
        recover: bool = False,
        no_wait: bool = False,
    ) -> IExecution:
        """Invokes engine with qualified query and user data."""
        data = data or {}
        user = self.get_user(user)
        query = user.qualify_items(query)
        return await self.engine.invoke(query, data, user.user_name, restart, recover, no_wait)

    async def assign(
        self,
        query: Any,
        data: Optional[Dict[str, Any]] = None,
        assignment: Optional[Dict[str, Any]] = None,
        user: Optional[SecureUser] = None,
    ) -> IExecution:
        """Assigns an activity to a user."""
        data = data or {}
        assignment = assignment or {}
        user = self.get_user(user)
        query = user.qualify_items(query)
        return await self.engine.assign(query, data, assignment, user.user_name)

    async def throw_message(
        self,
        message_id: str,
        data: Optional[Dict[str, Any]] = None,
        message_matching_key: Any = None,
    ) -> IExecution:
        """Throws a message with qualified query and user data."""
        data = data or {}
        return await self.engine.throw_message(message_id, data, message_matching_key)

    async def throw_signal(
        self,
        signal_id: str,
        data: Optional[Dict[str, Any]] = None,
        message_matching_key: Any = None,
    ) -> Any:
        """Throws a signal with qualified query and user data."""
        data = data or {}
        return await self.engine.throw_signal(signal_id, data, message_matching_key)

    async def start_event(
        self,
        query: Any,
        element_id: str,
        data: Optional[Dict[str, Any]] = None,
        user: Optional[SecureUser] = None,
        restart: bool = False,
        recover: bool = False,
    ) -> IExecution:
        """Starts an event with qualified query and user data."""
        data = data or {}
        user = self.get_user(user)
        return await self.engine.start_event(query, element_id, data, user.user_name, restart, recover)

    async def restart(self, item_query: Any, data: Any, user: Optional[SecureUser] = None) -> IExecution:
        """Restarts an item with qualified query and user data."""
        user = self.get_user(user)
        return await self.engine.restart(item_query, data, user.user_name)

    async def upgrade(self, model: str, after_node_ids: List[str]) -> Union[List[str], Dict[str, Any]]:
        """Upgrades a model to the latest version."""
        return await self.engine.upgrade(model, after_node_ids)


class APIDataStore(APIComponent):
    """API component for interacting with data."""

    def __init__(self, configuration: Optional[Settings] = None):
        super().__init__(configuration)
        self.data_store = self.config.data_store

    async def get_pending_user_tasks(self, query: Dict[str, Any], user: Optional[SecureUser] = None) -> List[ItemData]:
        """Retrieves pending user tasks for the given query and user."""
        query["items.status"] = "wait"
        query["items.type"] = "bpmn:UserTask"
        return await self.find_items(query, user)

    async def find_items(self, query: Any, user: Optional[SecureUser] = None) -> List[ItemData]:
        """Finds items based on the given query and user permissions."""
        user = self.get_user(user)
        query = user.qualify_instances(query)
        return await self.data_store.find_items(query)

    async def find_item(self, query: Any, user: Optional[SecureUser] = None) -> Optional[ItemData]:
        """Finds an item based on the given query and user permissions."""
        user = self.get_user(user)
        query = user.qualify_instances(query)
        items = await self.data_store.find_items(query)
        return items[0] if items else None

    async def find_instances(
        self, query: Any, user: Optional[SecureUser] = None, options: Any = None
    ) -> List[InstanceData]:
        """Finds instances based on the given query and user permissions."""
        user = self.get_user(user)
        query = user.qualify_instances(query)
        return await self.data_store.find_instances(query, options)

    async def delete_instances(self, query: Any, user: Optional[SecureUser] = None) -> None:
        """Deletes instances based on the given query and user permissions."""
        user = self.get_user(user)
        query = user.qualify_delete_instances(query)
        return await self.data_store.delete_instances(query)


class APIModelDataStore(APIComponent):
    """API component for interacting with models."""

    def __init__(self, configuration: Optional[Settings] = None):
        super().__init__(configuration)
        self.engine = self.config.engine
        self.model_data_store = self.config.model_data_store

    async def get(self, query: dict[str, Any], user: Optional[SecureUser] = None) -> List[Dict[str, Any]]:
        """Retrieves models based on the given query and user permissions."""
        user = self.get_user(user)
        if user.tenant_id:
            query["owner"] = user.models_owner
        return await self.model_data_store.get(query)

    async def save(self, name: str, source: str, svg: str, user: Optional[SecureUser] = None) -> bool:
        """Saves a model."""
        user = self.get_user(user)
        if user.can_modify_model(name):
            return await self.model_data_store.save(name, source, svg, user.models_owner)
        return False

    async def list(self, query: dict[str, Any], user: Optional[SecureUser] = None) -> List[dict[str, Any]]:
        """Lists models based on the given query and user permissions."""
        user = self.get_user(user)
        if user.tenant_id:
            query["owner"] = user.models_owner
        return await self.model_data_store.get_list(query)

    async def find_events(self, query: dict[str, Any], user: Optional[SecureUser] = None) -> List[EventData]:
        """Finds events based on the given query and user permissions."""
        user = self.get_user(user)
        query = user.qualify_start_events(query)
        return await self.model_data_store.find_events(query)

    async def find_start_events(self, query: dict[str, Any], user: Optional[SecureUser] = None) -> List[EventData]:
        """Finds start events based on the given query and user permissions."""
        user = self.get_user(user)
        query["events.subType"] = None
        query = user.qualify_start_events(query)
        return await self.model_data_store.find_events(query)

    async def delete(self, name: str, user: Optional[SecureUser] = None) -> None:
        """Deletes a model."""
        user = self.get_user(user)
        if user.can_delete_model(name):
            return await self.model_data_store.delete_model(name)
        return None

    async def rename(self, name: str, new_name: str, user: Optional[SecureUser] = None) -> bool:
        """Renames a model."""
        user = self.get_user(user)
        if user.can_modify_model(name):
            return await self.model_data_store.rename_model(name, new_name)
        return False

    async def get_source(self, name: str, user: Optional[SecureUser] = None) -> str:
        """Retrieves the source of a model."""
        user = self.get_user(user)
        return await self.model_data_store.get_source(name)

    async def load(self, name: str, user: Optional[SecureUser] = None) -> IDefinition:
        """Loads a model."""
        user = self.get_user(user)
        return await self.model_data_store.load(name)

    async def export(self, query: Any, folder: str, user: Optional[SecureUser] = None) -> None:
        """Exports models based on the given query and user permissions."""
        pass
