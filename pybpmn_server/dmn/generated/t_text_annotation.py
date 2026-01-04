from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_artifact import TArtifact

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TTextAnnotation(TArtifact):
    class Meta:
        name = "tTextAnnotation"

    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    text_format: str = field(
        default="text/plain",
        metadata={
            "name": "textFormat",
            "type": "Attribute",
        },
    )
