from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TRuleAnnotationClause:
    class Meta:
        name = "tRuleAnnotationClause"

    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
