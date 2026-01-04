from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.bounds import Bounds
from pybpmn_server.dmn.generated.diagram_element import DiagramElement

__NAMESPACE__ = "http://www.omg.org/spec/DMN/20180521/DI/"


@dataclass
class Shape(DiagramElement):
    """
    Attributes:
        bounds: the optional bounds of the shape relative to the origin
            of its nesting plane.
    """

    bounds: Optional[Bounds] = field(
        default=None,
        metadata={
            "name": "Bounds",
            "type": "Element",
            "namespace": "http://www.omg.org/spec/DMN/20180521/DC/",
        },
    )
