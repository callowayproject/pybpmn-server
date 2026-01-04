from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_dmnelement import TDMNElement
from pybpmn_server.dmn.generated.t_literal_expression import TLiteralExpression
from pybpmn_server.dmn.generated.t_unary_tests import TUnaryTests

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TOutputClause(TDMNElement):
    class Meta:
        name = "tOutputClause"

    output_values: Optional[TUnaryTests] = field(
        default=None,
        metadata={
            "name": "outputValues",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    default_output_entry: Optional[TLiteralExpression] = field(
        default=None,
        metadata={
            "name": "defaultOutputEntry",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    type_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "typeRef",
            "type": "Attribute",
        },
    )
