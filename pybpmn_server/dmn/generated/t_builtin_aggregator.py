from enum import Enum

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


class TBuiltinAggregator(Enum):
    SUM = "SUM"
    COUNT = "COUNT"
    MIN = "MIN"
    MAX = "MAX"
