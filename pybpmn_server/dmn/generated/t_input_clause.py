from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_dmnelement import TDMNElement
from pybpmn_server.dmn.generated.t_literal_expression import TLiteralExpression
from pybpmn_server.dmn.generated.t_unary_tests import TUnaryTests

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TInputClause(TDMNElement):
    class Meta:
        name = "tInputClause"

    input_expression: Optional[TLiteralExpression] = field(
        default=None,
        metadata={
            "name": "inputExpression",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )
    input_values: Optional[TUnaryTests] = field(
        default=None,
        metadata={
            "name": "inputValues",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
