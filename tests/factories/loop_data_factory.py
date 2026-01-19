from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from pybpmn_server.datastore.data_objects import LoopData
from tests.factories.helpers import sequence_int


class LoopDataFactory(ModelFactory[LoopData]):
    """Factory for LoopData."""

    __model__ = LoopData

    id = Use(lambda: 0)
    node_id = "loop_1"
    owner_token_id = "token_1"
