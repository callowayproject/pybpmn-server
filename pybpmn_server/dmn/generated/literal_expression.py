from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_literal_expression import TLiteralExpression

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class LiteralExpression(TLiteralExpression):
    class Meta:
        name = "literalExpression"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
