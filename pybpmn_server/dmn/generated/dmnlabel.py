from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.shape import Shape

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20230324/DMNDI/"


@dataclass
class Dmnlabel(Shape):
    class Meta:
        name = "DMNLabel"
        namespace = "https://www.omg.org/spec/DMN/20230324/DMNDI/"

    text: Optional[str] = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Element",
        },
    )
