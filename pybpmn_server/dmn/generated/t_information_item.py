from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_named_element import TNamedElement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TInformationItem(TNamedElement):
    class Meta:
        name = "tInformationItem"

    type_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "typeRef",
            "type": "Attribute",
        },
    )
