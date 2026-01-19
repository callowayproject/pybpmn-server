from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from pybpmn_server.datastore.data_objects import TokenData
from pybpmn_server.interfaces.enums import TokenStatus, TokenType
from tests.factories.helpers import generate_ulid


class TokenDataFactory(ModelFactory[TokenData]):
    """Factory for TokenData."""

    __model__ = TokenData

    id = Use(generate_ulid)
    type = TokenType.Primary
    start_node_id = "start_node_1"
    current_node_id = "current_node_1"
    status = TokenStatus.running
