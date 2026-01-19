"""Test factories for data objects."""

from pybpmn_server.datastore.data_objects import (
    BpmnModelData,
    EventData,
    InstanceData,
    ItemData,
    LoopData,
    ProcessData,
    TimerData,
    TokenData,
)
from tests.factories import (
    BpmnModelDataFactory,
    EventDataFactory,
    InstanceDataFactory,
    ItemFactory,
    LoopDataFactory,
    ProcessDataFactory,
    TimerDataFactory,
    TokenDataFactory,
)


def test_loop_data_factory():
    loop = LoopDataFactory.build()
    assert isinstance(loop, LoopData)
    assert isinstance(loop.id, int)
    assert loop.node_id == "loop_1"


def test_token_data_factory():
    token = TokenDataFactory.build()
    assert isinstance(token, TokenData)
    assert len(token.id) > 0
    assert token.start_node_id == "start_node_1"


def test_item_factory():
    item = ItemFactory.build()
    assert isinstance(item, ItemData)
    assert len(item.id) > 0
    assert item.element_id == "task_1"


def test_instance_data_factory():
    instance = InstanceDataFactory.build()
    assert isinstance(instance, InstanceData)
    assert len(instance.id) > 0
    assert instance.items == []
    assert instance.tokens == []
    assert instance.loops == []


def test_timer_data_factory():
    timer = TimerDataFactory.build()
    assert isinstance(timer, TimerData)
    assert timer.expression == "PT1M"


def test_event_data_factory():
    event = EventDataFactory.build()
    assert isinstance(event, EventData)
    assert event.element_id == "event_1"


def test_process_data_factory():
    process = ProcessDataFactory.build()
    assert isinstance(process, ProcessData)
    assert len(process.id) > 0
    assert process.name == "Test Process"


def test_bpmn_model_data_factory():
    model = BpmnModelDataFactory.build()
    assert isinstance(model, BpmnModelData)
    assert model.name == "test_model"
