from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from pybpmn_server.datastore.data_objects import InstanceData
from pybpmn_server.interfaces.enums import ExecutionStatus
from tests.factories.helpers import generate_ulid


class InstanceDataFactory(ModelFactory[InstanceData]):
    """Factory for InstanceData."""

    __model__ = InstanceData

    id = Use(generate_ulid)
    status = ExecutionStatus.running
    version = Use(lambda: 0)
    items = Use(list)
    tokens = Use(list)
    loops = Use(list)
