from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "http://www.omg.org/spec/DMN/20180521/DC/"


@dataclass
class Bounds:
    """
    Bounds specifies a rectangular area in some x-y coordinate system that is
    defined by a location (x and y) and a size (width and height).
    """

    class Meta:
        namespace = "http://www.omg.org/spec/DMN/20180521/DC/"

    x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    width: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    height: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
