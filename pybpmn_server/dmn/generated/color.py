from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "http://www.omg.org/spec/DMN/20180521/DC/"


@dataclass
class Color:
    """
    Color is a data type that represents a color value in the RGB format.
    """

    class Meta:
        namespace = "http://www.omg.org/spec/DMN/20180521/DC/"

    red: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 255,
        },
    )
    green: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 255,
        },
    )
    blue: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 255,
        },
    )
