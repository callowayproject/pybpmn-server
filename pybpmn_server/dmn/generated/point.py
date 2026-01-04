from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "http://www.omg.org/spec/DMN/20180521/DC/"


@dataclass
class Point:
    """
    A Point specifies an location in some x-y coordinate system.
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
