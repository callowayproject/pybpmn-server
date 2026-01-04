from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_dmnelement import TDMNElement
from pybpmn_server.dmn.generated.t_dmnelement_reference import TDmnelementReference

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TAuthorityRequirement(TDMNElement):
    class Meta:
        name = "tAuthorityRequirement"

    required_decision: Optional[TDmnelementReference] = field(
        default=None,
        metadata={
            "name": "requiredDecision",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    required_input: Optional[TDmnelementReference] = field(
        default=None,
        metadata={
            "name": "requiredInput",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    required_authority: Optional[TDmnelementReference] = field(
        default=None,
        metadata={
            "name": "requiredAuthority",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
