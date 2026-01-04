from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_artifact import TArtifact
from pybpmn_server.dmn.generated.t_association_direction import TAssociationDirection
from pybpmn_server.dmn.generated.t_dmnelement_reference import TDmnelementReference

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TAssociation(TArtifact):
    class Meta:
        name = "tAssociation"

    source_ref: Optional[TDmnelementReference] = field(
        default=None,
        metadata={
            "name": "sourceRef",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )
    target_ref: Optional[TDmnelementReference] = field(
        default=None,
        metadata={
            "name": "targetRef",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )
    association_direction: TAssociationDirection = field(
        default=TAssociationDirection.NONE,
        metadata={
            "name": "associationDirection",
            "type": "Attribute",
        },
    )
