from dataclasses import dataclass, field
from typing import Optional
from xml.etree.ElementTree import QName

from pybpmn_server.dmn.generated.dmnlabel import Dmnlabel
from pybpmn_server.dmn.generated.edge import Edge

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20230324/DMNDI/"


@dataclass
class Dmnedge(Edge):
    class Meta:
        name = "DMNEdge"
        namespace = "https://www.omg.org/spec/DMN/20230324/DMNDI/"

    dmnlabel: Optional[Dmnlabel] = field(
        default=None,
        metadata={
            "name": "DMNLabel",
            "type": "Element",
        },
    )
    dmn_element_ref: Optional[QName] = field(
        default=None,
        metadata={
            "name": "dmnElementRef",
            "type": "Attribute",
            "required": True,
        },
    )
    source_element: Optional[QName] = field(
        default=None,
        metadata={
            "name": "sourceElement",
            "type": "Attribute",
        },
    )
    target_element: Optional[QName] = field(
        default=None,
        metadata={
            "name": "targetElement",
            "type": "Attribute",
        },
    )
