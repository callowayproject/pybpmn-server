from dataclasses import dataclass, field

from pybpmn_server.dmn.generated.t_dmnelement_reference import TDmnelementReference
from pybpmn_server.dmn.generated.t_invocable import TInvocable

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TDecisionService(TInvocable):
    class Meta:
        name = "tDecisionService"

    output_decision: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "outputDecision",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    encapsulated_decision: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "encapsulatedDecision",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    input_decision: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "inputDecision",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    input_data: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "inputData",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
