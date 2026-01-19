"""Factory for EventData."""

from polyfactory.factories.pydantic_factory import ModelFactory

from pybpmn_server.datastore.data_objects import EventData


class EventDataFactory(ModelFactory[EventData]):
    """Factory for EventData."""

    __model__ = EventData

    element_id = "event_1"
    process_id = "process_1"

    @classmethod
    def type(cls) -> str:
        """Factory to generate the type attribute."""
        return cls.__random__.choice(
            [
                "bpmn:startEvent",
                "bpmn:endEvent",
                "bpmn:throwEvent",
                "bpmn:catchEvent",
                "bpmn:intermediateThrowEvent",
                "bpmn:intermediateCatchEvent",
                "bpmn:implicitThrowEvent",
                "bpmn:boundaryEvent",
            ]
        )
