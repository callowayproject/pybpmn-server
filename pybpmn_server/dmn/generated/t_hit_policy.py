from enum import Enum

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


class THitPolicy(Enum):
    UNIQUE = "UNIQUE"
    FIRST = "FIRST"
    PRIORITY = "PRIORITY"
    ANY = "ANY"
    COLLECT = "COLLECT"
    RULE_ORDER = "RULE ORDER"
    OUTPUT_ORDER = "OUTPUT ORDER"
