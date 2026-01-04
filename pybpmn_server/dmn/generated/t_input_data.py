from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_drgelement import TDrgelement
from pybpmn_server.dmn.generated.t_information_item import TInformationItem

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TInputData(TDrgelement):
    class Meta:
        name = "tInputData"

    variable: Optional[TInformationItem] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
