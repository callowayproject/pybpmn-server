from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_dmnelement import TDMNElement
from pybpmn_server.dmn.generated.t_information_item import TInformationItem

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TFunctionItem(TDMNElement):
    class Meta:
        name = "tFunctionItem"

    parameters: list[TInformationItem] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    output_type_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "outputTypeRef",
            "type": "Attribute",
        },
    )
