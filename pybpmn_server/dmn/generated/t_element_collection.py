from dataclasses import dataclass, field

from pybpmn_server.dmn.generated.t_dmnelement_reference import TDmnelementReference
from pybpmn_server.dmn.generated.t_named_element import TNamedElement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TElementCollection(TNamedElement):
    class Meta:
        name = "tElementCollection"

    drg_element: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "drgElement",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
