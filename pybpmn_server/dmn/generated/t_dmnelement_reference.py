from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TDmnelementReference:
    class Meta:
        name = "tDMNElementReference"

    href: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
