from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_dmnelement import TDMNElement
from pybpmn_server.dmn.generated.t_dmnelement_reference import TDmnelementReference

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TKnowledgeRequirement(TDMNElement):
    class Meta:
        name = "tKnowledgeRequirement"

    required_knowledge: Optional[TDmnelementReference] = field(
        default=None,
        metadata={
            "name": "requiredKnowledge",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )
