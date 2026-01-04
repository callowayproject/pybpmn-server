from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.diagram import Diagram
from pybpmn_server.dmn.generated.dimension import Dimension
from pybpmn_server.dmn.generated.dmndiagram_element import DmndiagramElement
from pybpmn_server.dmn.generated.dmnedge import Dmnedge
from pybpmn_server.dmn.generated.dmnshape import Dmnshape

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20230324/DMNDI/"


@dataclass
class Dmndiagram(Diagram):
    class Meta:
        name = "DMNDiagram"
        namespace = "https://www.omg.org/spec/DMN/20230324/DMNDI/"

    size: Optional[Dimension] = field(
        default=None,
        metadata={
            "name": "Size",
            "type": "Element",
        },
    )
    dmnedge: list[Dmnedge] = field(
        default_factory=list,
        metadata={
            "name": "DMNEdge",
            "type": "Element",
        },
    )
    dmnshape: list[Dmnshape] = field(
        default_factory=list,
        metadata={
            "name": "DMNShape",
            "type": "Element",
        },
    )
    dmndiagram_element: list[DmndiagramElement] = field(
        default_factory=list,
        metadata={
            "name": "DMNDiagramElement",
            "type": "Element",
        },
    )
    use_alternative_input_data_shape: bool = field(
        default=False,
        metadata={
            "name": "useAlternativeInputDataShape",
            "type": "Attribute",
        },
    )
