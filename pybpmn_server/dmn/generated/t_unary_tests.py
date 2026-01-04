from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_expression import TExpression

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TUnaryTests(TExpression):
    class Meta:
        name = "tUnaryTests"

    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )
    expression_language: Optional[str] = field(
        default=None,
        metadata={
            "name": "expressionLanguage",
            "type": "Attribute",
        },
    )
