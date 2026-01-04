from enum import Enum

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


class TDecisionTableOrientation(Enum):
    RULE_AS_ROW = "Rule-as-Row"
    RULE_AS_COLUMN = "Rule-as-Column"
    CROSS_TABLE = "CrossTable"
