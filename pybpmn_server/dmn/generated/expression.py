from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_expression import TExpression

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Expression(TExpression):
    class Meta:
        name = "expression"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
