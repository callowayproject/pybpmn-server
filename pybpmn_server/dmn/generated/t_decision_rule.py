from dataclasses import dataclass, field

from pybpmn_server.dmn.generated.t_dmnelement import TDMNElement
from pybpmn_server.dmn.generated.t_literal_expression import TLiteralExpression
from pybpmn_server.dmn.generated.t_rule_annotation import TRuleAnnotation
from pybpmn_server.dmn.generated.t_unary_tests import TUnaryTests

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TDecisionRule(TDMNElement):
    class Meta:
        name = "tDecisionRule"

    input_entry: list[TUnaryTests] = field(
        default_factory=list,
        metadata={
            "name": "inputEntry",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    output_entry: list[TLiteralExpression] = field(
        default_factory=list,
        metadata={
            "name": "outputEntry",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "min_occurs": 1,
        },
    )
    annotation_entry: list[TRuleAnnotation] = field(
        default_factory=list,
        metadata={
            "name": "annotationEntry",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
