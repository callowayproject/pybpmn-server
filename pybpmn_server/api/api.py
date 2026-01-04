"""API component for interacting with BPMN processes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from pybpmn_server.api.secure_user import SecureUser
    from pybpmn_server.datastore.data_objects import InstanceData, ItemData
    from pybpmn_server.elements.interfaces import IDefinition
    from pybpmn_server.engine.interfaces import IExecution
    from pybpmn_server.server.bpmn_server import BPMNServer


class BPMNAPI:
    """API component for interacting with BPMN processes."""

    server: BPMNServer
    engine: APIEngine
    data: APIData
    model: APIModel
    default_user: Optional[SecureUser] = None

    def __init__(self, server: BPMNServer):
        self.server = server
        self.engine = APIEngine(self)
        self.data = APIData(self)
        self.model = APIModel(self)


class APIComponent:
    """Base class for API components."""

    api: BPMNAPI

    def __init__(self, api: BPMNAPI):
        self.api = api

    @property
    def server(self) -> BPMNServer:
        """Return the server instance."""
        return self.api.server

    def get_user(self, user: Optional[SecureUser]) -> SecureUser:
        """Return the user instance."""
        if user is None:
            return self.api.default_user
        return user


class APIEngine(APIComponent):
    """API component for interacting with the engine."""

    async def start(
        self,
        name: str,
        data: Optional[Dict[str, Any]] = None,
        user: Optional[SecureUser] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> IExecution:
        """Start a process instance."""
        if data is None:
            data = {}
        if options is None:
            options = {}
        user = self.get_user(user)
        return await self.server.engine.start(name, data, options.get("startNodeId"), user.user_name, options)

    async def invoke(
        self,
        query: Any,
        data: Optional[Dict[str, Any]] = None,
        user: Optional[SecureUser] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> IExecution:
        """Invokes engine with qualified query and user data."""
        if data is None:
            data = {}
        if options is None:
            options = {}
        user = self.get_user(user)
        query = user.qualify_items(query)
        return await self.server.engine.invoke(query, data, user.user_name, options)

    async def assign(
        self,
        query: Any,
        data: Optional[Dict[str, Any]] = None,
        assignment: Optional[Dict[str, Any]] = None,
        user: Optional[SecureUser] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> IExecution:
        """Assigns an activity to a user."""
        if data is None:
            data = {}
        if assignment is None:
            assignment = {}
        if options is None:
            options = {}
        user = self.get_user(user)
        query = user.qualify_items(query)
        return await self.server.engine.assign(query, data, assignment, user.user_name, options)

    async def throw_message(
        self,
        message_id: str,
        data: Optional[Dict[str, Any]] = None,
        message_matching_key: Any = None,
        # user: Optional[ISecureUser] = None,
        # options: Dict[str, Any] = None,
    ) -> IExecution:
        """Throws a message with qualified query and user data."""
        data = data or {}
        return await self.server.engine.throw_message(message_id, data, message_matching_key)

    async def throw_signal(
        self,
        signal_id: str,
        data: Optional[Dict[str, Any]] = None,
        message_matching_key: Any = None,
        # user: Optional[ISecureUser] = None,
        # options: Dict[str, Any] = None,
    ) -> Any:
        """Throws a signal with qualified query and user data."""
        data = data or {}
        return await self.server.engine.throw_signal(signal_id, data, message_matching_key)

    async def start_event(
        self,
        query: Any,
        element_id: str,
        data: Optional[Dict[str, Any]] = None,
        user: Optional[SecureUser] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> IExecution:
        """Starts an event with qualified query and user data."""
        data = data or {}
        options = options or {}
        user = self.get_user(user)
        return await self.server.engine.start_event(query, element_id, data, user.user_name, options)

    async def restart(
        self, item_query: Any, data: Any, user: Optional[SecureUser] = None, options: Optional[Dict[str, Any]] = None
    ) -> IExecution:
        """Restarts an item with qualified query and user data."""
        options = options or {}
        user = self.get_user(user)
        return await self.server.engine.restart(item_query, data, user.user_name, options)

    async def upgrade(self, model: str, after_node_ids: List[str]) -> Union[List[str], Dict[str, Any]]:
        """Upgrades a model to the latest version."""
        return await self.server.engine.upgrade(model, after_node_ids)


class APIData(APIComponent):
    """API component for interacting with data."""

    async def get_pending_user_tasks(self, query: Dict[str, Any], user: Optional[SecureUser] = None) -> List[ItemData]:
        """Retrieves pending user tasks for the given query and user."""
        query["items.status"] = "wait"
        query["items.type"] = "bpmn:UserTask"
        return await self.find_items(query, user)

    async def find_items(self, query: Any, user: Optional[SecureUser] = None) -> List[ItemData]:
        """Finds items based on the given query and user permissions."""
        user = self.get_user(user)
        query = user.qualify_instances(query)
        return await self.server.data_store.find_items(query)

    async def find_item(self, query: Any, user: Optional[SecureUser] = None) -> Optional[ItemData]:
        """Finds an item based on the given query and user permissions."""
        user = self.get_user(user)
        query = user.qualify_instances(query)
        items = await self.server.data_store.find_items(query)
        return items[0] if items else None

    async def find_instances(
        self, query: Any, user: Optional[SecureUser] = None, options: Any = None
    ) -> List[InstanceData]:
        """Finds instances based on the given query and user permissions."""
        user = self.get_user(user)
        query = user.qualify_instances(query)
        return await self.server.data_store.find_instances(query, options)

    async def delete_instances(self, query: Any, user: Optional[SecureUser] = None) -> None:
        """Deletes instances based on the given query and user permissions."""
        user = self.get_user(user)
        query = user.qualify_delete_instances(query)
        return await self.server.data_store.delete_instances(query)


class APIModel(APIComponent):
    """API component for interacting with models."""

    async def get(self, query: Any, user: Optional[SecureUser] = None) -> List[Dict[str, Any]]:
        """Retrieves models based on the given query and user permissions."""
        user = self.get_user(user)
        if user.tenant_id:
            query["owner"] = user.models_owner
        return await self.server.definitions.get(query)

    async def save(self, name: str, source: str, svg: str, user: Optional[SecureUser] = None) -> bool:
        """Saves a model."""
        user = self.get_user(user)
        if user.can_modify_model(name):
            return await self.server.definitions.save(name, source, svg, user.models_owner)
        return False

    async def list(self, query: Any, user: Optional[SecureUser] = None) -> List[str]:
        """Lists models based on the given query and user permissions."""
        user = self.get_user(user)
        if user.tenant_id:
            query["owner"] = user.models_owner
        return await self.server.definitions.get_list(query)

    async def find_events(self, query: Any, user: Optional[SecureUser] = None) -> List[Any]:
        """Finds events based on the given query and user permissions."""
        user = self.get_user(user)
        return await self.server.definitions.find_events(query, user.models_owner)

    async def find_start_events(self, query: Any, user: Optional[SecureUser] = None) -> List[Any]:
        """Finds start events based on the given query and user permissions."""
        user = self.get_user(user)
        query["events.subType"] = None
        query = user.qualify_start_events(query)
        return await self.server.definitions.find_events(query, user.models_owner)

    async def delete(self, name: str, user: Optional[SecureUser] = None) -> None:
        """Deletes a model."""
        user = self.get_user(user)
        if user.can_delete_model(name):
            return await self.server.definitions.delete_model(name, user.models_owner)
        return None

    async def rename(self, name: str, new_name: str, user: Optional[SecureUser] = None) -> bool:
        """Renames a model."""
        user = self.get_user(user)
        if user.can_modify_model(name):
            return await self.server.definitions.rename_model(name, new_name, user.models_owner)
        return False

    async def get_source(self, name: str, user: Optional[SecureUser] = None) -> str:
        """Retrieves the source of a model."""
        user = self.get_user(user)
        return await self.server.definitions.get_source(name, user.models_owner)

    async def load(self, name: str, user: Optional[SecureUser] = None) -> IDefinition:
        """Loads a model."""
        user = self.get_user(user)
        return await self.server.definitions.load(name, user.models_owner)

    async def export(self, query: Any, folder: str, user: Optional[SecureUser] = None) -> None:
        """Exports models based on the given query and user permissions."""
        pass
