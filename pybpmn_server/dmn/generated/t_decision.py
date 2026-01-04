from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.decision_table import DecisionTable
from pybpmn_server.dmn.generated.literal_expression import LiteralExpression
from pybpmn_server.dmn.generated.t_authority_requirement import TAuthorityRequirement
from pybpmn_server.dmn.generated.t_context import (
    Conditional,
    Context,
    Every,
    Filter,
    For,
    FunctionDefinition,
    Invocation,
    List,
    Relation,
    Some,
)
from pybpmn_server.dmn.generated.t_dmnelement_reference import TDmnelementReference
from pybpmn_server.dmn.generated.t_drgelement import TDrgelement
from pybpmn_server.dmn.generated.t_information_item import TInformationItem
from pybpmn_server.dmn.generated.t_information_requirement import TInformationRequirement
from pybpmn_server.dmn.generated.t_knowledge_requirement import TKnowledgeRequirement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TDecision(TDrgelement):
    class Meta:
        name = "tDecision"

    question: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    allowed_answers: Optional[str] = field(
        default=None,
        metadata={
            "name": "allowedAnswers",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    variable: Optional[TInformationItem] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    information_requirement: list[TInformationRequirement] = field(
        default_factory=list,
        metadata={
            "name": "informationRequirement",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    knowledge_requirement: list[TKnowledgeRequirement] = field(
        default_factory=list,
        metadata={
            "name": "knowledgeRequirement",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    authority_requirement: list[TAuthorityRequirement] = field(
        default_factory=list,
        metadata={
            "name": "authorityRequirement",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    supported_objective: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "supportedObjective",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    impacted_performance_indicator: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "impactedPerformanceIndicator",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    decision_maker: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "decisionMaker",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    decision_owner: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "decisionOwner",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    using_process: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "usingProcess",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    using_task: list[TDmnelementReference] = field(
        default_factory=list,
        metadata={
            "name": "usingTask",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    filter: Optional[Filter] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    conditional: Optional[Conditional] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    some: Optional[Some] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    every: Optional[Every] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    for_value: Optional[For] = field(
        default=None,
        metadata={
            "name": "for",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    list_value: Optional[List] = field(
        default=None,
        metadata={
            "name": "list",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    relation: Optional[Relation] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    function_definition: Optional[FunctionDefinition] = field(
        default=None,
        metadata={
            "name": "functionDefinition",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    context: Optional[Context] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    decision_table: Optional[DecisionTable] = field(
        default=None,
        metadata={
            "name": "decisionTable",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    invocation: Optional[Invocation] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    literal_expression: Optional[LiteralExpression] = field(
        default=None,
        metadata={
            "name": "literalExpression",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
