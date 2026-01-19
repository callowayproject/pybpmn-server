from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from pybpmn_server.datastore.data_objects import ProcessData
from tests.factories.helpers import generate_ulid


class ProcessDataFactory(ModelFactory[ProcessData]):
    """Factory for ProcessData."""

    __model__ = ProcessData

    id = Use(generate_ulid)
    name = "Test Process"
    is_executable = True
