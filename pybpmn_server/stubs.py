from typing import Any, Dict, List, Optional

from pybpmn_server.datastore.interfaces import FindResult, IDataStore, IModelsDatastore
from pybpmn_server.elements.interfaces import INode
from pybpmn_server.engine.interfaces import IExecution, IItem, ScriptHandler
from pybpmn_server.interfaces.common import AppDelegateBase, IServiceProvider
from pybpmn_server.server.interfaces import ICacheManager, ICron


class NodeStub(INode):
    def __init__(self, node_id: str, name: str = "", type_: str = "bpmn:Task"):
        self.id = node_id
        self.name = name
        self.type = type_
        self.process_id = "test_process"
        self.outbounds = []
        self.inbounds = []
        self.lane = None
        self.behaviours = {}
        self.loop_definition = None

    def describe(self) -> List[List[str]]:
        return []

    def restored(self, item: Any) -> None:
        pass

    def resume(self, item: Any) -> None:
        pass

    def has_behaviour(self, name: Any) -> bool:
        return False

    def get_behaviour(self, name: Any) -> Any:
        return None

    def add_behaviour(self, name: Any, behaviour: Any) -> None:
        pass

    async def execute(self, item: Any) -> Any:
        return None

    async def end(self, item: Any, cancel: bool = False) -> None:
        pass

    async def get_outbounds(self, item: Any) -> List[Any]:
        return []


class ModelsDatastoreStub(IModelsDatastore):
    def __init__(self, server: Any):
        self.server = server

    async def get(self, query: Any) -> List[Dict[str, Any]]:
        return []

    async def get_list(self, query: Any) -> List[str]:
        return []

    async def get_source(self, name: Any, owner: Any = None) -> str:
        return ""

    async def get_svg(self, name: Any, owner: Any = None) -> str:
        return ""

    async def save(self, name: Any, bpmn: Any, svg: Optional[Any] = None, owner: Optional[Any] = None) -> bool:
        return True

    async def load(self, name: Any, owner: Any = None) -> Any:
        return None

    async def load_model(self, name: Any, owner: Any = None) -> Any:
        return None

    async def find_events(self, query: Any, owner: Any = None) -> List[Any]:
        return []

    async def rebuild(self, model: Optional[Any] = None) -> None:
        pass

    def install(self) -> None:
        return None

    def import_(self, data: Any) -> None:
        return None

    async def save_model(self, model: Any) -> bool:
        return True

    async def delete_model(self, name: Any, owner: Any = None) -> None:
        pass

    async def rename_model(self, name: Any, new_name: Any, owner: Any = None) -> bool:
        return True


class DataStoreStub(IDataStore):
    def __init__(self, server: Any):
        self.server = server
        self.db_configuration = None
        self.db = None
        self.logger = None
        self.locker = None

    async def save(self, instance: Any, options: Any) -> None:
        pass

    async def load_instance(self, instance_id: Any, options: Any) -> Dict[str, Any]:
        return {"instance": None, "items": []}

    async def find_item(self, query: Any) -> Any:
        return None

    async def find_instance(self, query: Any, options: Any) -> Any:
        return None

    async def find_instances(self, query: Any, option: Any) -> List[Any]:
        return []

    async def find_items(self, query: Any) -> List[Any]:
        return []

    async def delete_instances(self, query: Optional[Any] = None) -> None:
        pass

    def install(self) -> None:
        return None

    def archive(self, query: Any) -> None:
        return None

    async def find(self, params: Any) -> Any:
        return FindResult(data=[], total_count=0)


class DefaultAppDelegateStub(AppDelegateBase):
    def __init__(self, server: Any):
        self.server = server
        self.moddle_options = None

    async def get_services_provider(self, execution: IExecution) -> IServiceProvider:
        return {}  # type: ignore

    def send_email(self, to: Any, msg: Any, body: Any) -> None:
        pass

    def execution_started(self, execution: IExecution) -> None:
        pass

    def start_up(self, options: Any) -> None:
        pass

    def message_thrown(self, message_id: str, data: Any, message_matching_key: Any, item: IItem) -> None:
        pass

    def signal_thrown(self, signal_id: str, data: Any, message_matching_key: Any, item: IItem) -> None:
        pass

    def issue_message(self, message_id: str, data: Any) -> None:
        pass

    def issue_signal(self, message_id: str, data: Any) -> None:
        pass

    def service_called(self, input_data: Dict[str, Any], execution: IExecution, item: IItem) -> Any:
        return None


class NoCacheManagerStub(ICacheManager):
    def __init__(self, server: Any):
        self.server = server

    def list(self) -> List[Any]:
        return []

    def add(self, execution: IExecution) -> None:
        pass

    def remove(self, instance_id: Any) -> None:
        pass

    def shutdown(self) -> None:
        pass


class ScriptHandlerStub(ScriptHandler):
    """Stub for ScriptHandler."""

    def evaluate_expression(self, scope: Any, expression: Any) -> Any:
        """Stub for evaluate_expression method."""
        return None

    def execute_script(self, scope: Any, script: Any) -> Any:
        """Stub for execute_script method."""
        return None


class ExecutionStub(IExecution):
    def __init__(self):
        self.tokens = {}
        self.user_name = "test_user"
        self.options = {}
        self.id = "test_execution_id"
        self._next_id = 1
        self.logs = []

    def get_uuid(self) -> str:
        import uuid

        return str(uuid.uuid4())

    def get_new_sequence(self, scope: str) -> int:
        self._next_id += 1
        return self._next_id

    def log(self, *msg: Any):
        self.logs.append(("LOG", msg))

    def log_s(self, *msg: Any):
        self.logs.append(("LOG_S", msg))

    def log_e(self, *msg: Any):
        self.logs.append(("LOG_E", msg))

    def info(self, msg: Any):
        self.logs.append(("INFO", msg))

    def error(self, msg: Any):
        self.logs.append(("ERROR", msg))

    def get_data(self, data_path: str) -> Any:
        return {}

    def append_data(
        self, input_data: Any, item: IItem, data_path: Optional[Any] = None, assignment: Optional[Any] = None
    ):
        pass

    def get_node_by_id(self, id: Any) -> Any:
        return None

    def get_token(self, id: Any) -> Any:
        return self.tokens.get(id)

    def terminate(self):
        pass


class CronStub(ICron):
    def check_timers(self, duration: Any) -> None:
        pass

    def start(self) -> None:
        pass

    def start_timers(self) -> None:
        pass
