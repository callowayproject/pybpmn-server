from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from pybpmn_server.datastore.data_objects import ItemData
from pybpmn_server.interfaces.enums import ItemStatus
from tests.factories.helpers import generate_ulid


class ItemFactory(ModelFactory[ItemData]):
    """Factory for creating ItemData objects."""

    __model__ = ItemData

    id = Use(generate_ulid)
    token_id = Use(generate_ulid)
    element_id = "task_1"
    element_name = ""
    element_type = "bpmn:ServiceTask"
    instance_id = Use(generate_ulid)
    status = ItemStatus.enter
    seq = Use(lambda: 0)
