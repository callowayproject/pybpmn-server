from dataclasses import dataclass, field
from typing import Optional
from xml.etree.ElementTree import QName

from pybpmn_server.dmn.generated.dmndecision_service_divider_line import (
    DmndecisionServiceDividerLine,
)
from pybpmn_server.dmn.generated.dmnlabel import Dmnlabel
from pybpmn_server.dmn.generated.shape import Shape

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20230324/DMNDI/"


@dataclass
class Dmnshape(Shape):
    class Meta:
        name = "DMNShape"
        namespace = "https://www.omg.org/spec/DMN/20230324/DMNDI/"

    dmnlabel: Optional[Dmnlabel] = field(
        default=None,
        metadata={
            "name": "DMNLabel",
            "type": "Element",
        },
    )
    dmndecision_service_divider_line: Optional[DmndecisionServiceDividerLine] = field(
        default=None,
        metadata={
            "name": "DMNDecisionServiceDividerLine",
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
    is_listed_input_data: Optional[bool] = field(
        default=None,
        metadata={
            "name": "isListedInputData",
            "type": "Attribute",
        },
    )
    is_collapsed: bool = field(
        default=False,
        metadata={
            "name": "isCollapsed",
            "type": "Attribute",
        },
    )
