from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from pybpmn_server.datastore.data_objects import TimerData
from tests.factories.helpers import now_utc


class TimerDataFactory(ModelFactory[TimerData]):
    """Factory for TimerData."""

    __model__ = TimerData

    expression = "PT1M"
    expression_format = "iso"
    reference_date_time = Use(now_utc)
