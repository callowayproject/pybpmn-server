from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_artifact import TArtifact

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TGroup(TArtifact):
    class Meta:
        name = "tGroup"

    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
