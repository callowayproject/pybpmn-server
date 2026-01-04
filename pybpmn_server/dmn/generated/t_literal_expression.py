from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_expression import TExpression
from pybpmn_server.dmn.generated.t_imported_values import TImportedValues

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TLiteralExpression(TExpression):
    class Meta:
        name = "tLiteralExpression"

    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    imported_values: Optional[TImportedValues] = field(
        default=None,
        metadata={
            "name": "importedValues",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    expression_language: Optional[str] = field(
        default=None,
        metadata={
            "name": "expressionLanguage",
            "type": "Attribute",
        },
    )
