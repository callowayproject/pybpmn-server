from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.diagram_element import DiagramElement

__NAMESPACE__ = "http://www.omg.org/spec/DMN/20180521/DI/"


@dataclass
class Diagram(DiagramElement):
    """
    Attributes:
        name: the name of the diagram.
        documentation: the documentation of the diagram.
        resolution: the resolution of the diagram expressed in user
            units per inch.
    """

    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    documentation: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    resolution: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
