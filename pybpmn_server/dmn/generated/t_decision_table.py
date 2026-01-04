from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_builtin_aggregator import TBuiltinAggregator
from pybpmn_server.dmn.generated.t_decision_rule import TDecisionRule
from pybpmn_server.dmn.generated.t_decision_table_orientation import TDecisionTableOrientation
from pybpmn_server.dmn.generated.t_expression import TExpression
from pybpmn_server.dmn.generated.t_hit_policy import THitPolicy
from pybpmn_server.dmn.generated.t_input_clause import TInputClause
from pybpmn_server.dmn.generated.t_output_clause import TOutputClause
from pybpmn_server.dmn.generated.t_rule_annotation_clause import TRuleAnnotationClause

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TDecisionTable(TExpression):
    class Meta:
        name = "tDecisionTable"

    input: list[TInputClause] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    output: list[TOutputClause] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "min_occurs": 1,
        },
    )
    annotation: list[TRuleAnnotationClause] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    rule: list[TDecisionRule] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    hit_policy: THitPolicy = field(
        default=THitPolicy.UNIQUE,
        metadata={
            "name": "hitPolicy",
            "type": "Attribute",
        },
    )
    aggregation: Optional[TBuiltinAggregator] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    preferred_orientation: TDecisionTableOrientation = field(
        default=TDecisionTableOrientation.RULE_AS_ROW,
        metadata={
            "name": "preferredOrientation",
            "type": "Attribute",
        },
    )
    output_label: Optional[str] = field(
        default=None,
        metadata={
            "name": "outputLabel",
            "type": "Attribute",
        },
    )
