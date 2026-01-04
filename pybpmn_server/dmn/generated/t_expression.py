from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_dmnelement import TDMNElement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TExpression(TDMNElement):
    class Meta:
        name = "tExpression"

    type_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "typeRef",
            "type": "Attribute",
        },
    )
