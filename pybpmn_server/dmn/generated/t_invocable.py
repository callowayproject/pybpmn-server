from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_drgelement import TDrgelement
from pybpmn_server.dmn.generated.t_information_item import TInformationItem

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TInvocable(TDrgelement):
    class Meta:
        name = "tInvocable"

    variable: Optional[TInformationItem] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
