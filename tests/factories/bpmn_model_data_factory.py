from polyfactory.factories.pydantic_factory import ModelFactory

from pybpmn_server.datastore.data_objects import BpmnModelData


class BpmnModelDataFactory(ModelFactory[BpmnModelData]):
    """Factory for BpmnModelData."""

    __model__ = BpmnModelData

    name = "test_model"
    source = "<xml/>"
    svg = "<svg/>"
