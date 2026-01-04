from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_authority_requirement import TAuthorityRequirement
from pybpmn_server.dmn.generated.t_context import TFunctionDefinition
from pybpmn_server.dmn.generated.t_invocable import TInvocable
from pybpmn_server.dmn.generated.t_knowledge_requirement import TKnowledgeRequirement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TBusinessKnowledgeModel(TInvocable):
    class Meta:
        name = "tBusinessKnowledgeModel"

    encapsulated_logic: Optional[TFunctionDefinition] = field(
        default=None,
        metadata={
            "name": "encapsulatedLogic",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    knowledge_requirement: list[TKnowledgeRequirement] = field(
        default_factory=list,
        metadata={
            "name": "knowledgeRequirement",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    authority_requirement: list[TAuthorityRequirement] = field(
        default_factory=list,
        metadata={
            "name": "authorityRequirement",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
