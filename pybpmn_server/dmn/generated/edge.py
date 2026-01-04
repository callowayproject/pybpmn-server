from dataclasses import dataclass, field

from pybpmn_server.dmn.generated.diagram_element import DiagramElement
from pybpmn_server.dmn.generated.point import Point

__NAMESPACE__ = "http://www.omg.org/spec/DMN/20180521/DI/"


@dataclass
class Edge(DiagramElement):
    """
    Attributes:
        waypoint: an optional list of points relative to the origin of
            the nesting diagram that specifies the connected line
            segments of the edge
    """

    waypoint: list[Point] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.omg.org/spec/DMN/20180521/DI/",
        },
    )
