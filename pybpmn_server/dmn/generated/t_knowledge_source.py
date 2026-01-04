from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_authority_requirement import TAuthorityRequirement
from pybpmn_server.dmn.generated.t_dmnelement_reference import TDmnelementReference
from pybpmn_server.dmn.generated.t_drgelement import TDrgelement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TKnowledgeSource(TDrgelement):
    class Meta:
        name = "tKnowledgeSource"

    authority_requirement: list[TAuthorityRequirement] = field(
        default_factory=list,
        metadata={
            "name": "authorityRequirement",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    type_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    owner: Optional[TDmnelementReference] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    location_uri: Optional[str] = field(
        default=None,
        metadata={
            "name": "locationURI",
            "type": "Attribute",
        },
    )
