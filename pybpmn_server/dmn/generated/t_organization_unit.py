from dataclasses import dataclass, field

from pybpmn_server.dmn.generated.t_business_context_element import TBusinessContextElement
from pybpmn_server.dmn.generated.t_dmnelement_reference import TDmnelementReference

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TOrganizationUnit(TBusinessContextElement):
    class Meta:
        name = "tOrganizationUnit"

    decision_made: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "decisionMade",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    decision_owned: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "decisionOwned",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
