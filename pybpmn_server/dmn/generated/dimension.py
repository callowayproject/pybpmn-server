from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "http://www.omg.org/spec/DMN/20180521/DC/"


@dataclass
class Dimension:
    """
    Dimension specifies two lengths (width and height) along the x and y axes in
    some x-y coordinate system.
    """

    class Meta:
        namespace = "http://www.omg.org/spec/DMN/20180521/DC/"

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
