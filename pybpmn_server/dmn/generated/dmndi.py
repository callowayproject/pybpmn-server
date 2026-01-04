from dataclasses import dataclass, field

from pybpmn_server.dmn.generated.dmndiagram import Dmndiagram
from pybpmn_server.dmn.generated.dmnstyle import Dmnstyle

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20230324/DMNDI/"


@dataclass
class Dmndi:
    class Meta:
        name = "DMNDI"
        namespace = "https://www.omg.org/spec/DMN/20230324/DMNDI/"

    dmndiagram: list[Dmndiagram] = field(
        default_factory=list,
        metadata={
            "name": "DMNDiagram",
            "type": "Element",
        },
    )
    dmnstyle: list[Dmnstyle] = field(
        default_factory=list,
        metadata={
            "name": "DMNStyle",
            "type": "Element",
        },
    )
