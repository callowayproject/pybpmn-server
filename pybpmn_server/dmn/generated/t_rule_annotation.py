from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TRuleAnnotation:
    class Meta:
        name = "tRuleAnnotation"

    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
