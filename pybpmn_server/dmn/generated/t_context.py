from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.decision_table import DecisionTable
from pybpmn_server.dmn.generated.literal_expression import LiteralExpression
from pybpmn_server.dmn.generated.t_dmnelement import TDMNElement
from pybpmn_server.dmn.generated.t_expression import TExpression
from pybpmn_server.dmn.generated.t_function_kind import TFunctionKind
from pybpmn_server.dmn.generated.t_information_item import TInformationItem

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TContext(TExpression):
    class Meta:
        name = "tContext"

    context_entry: list["ContextEntry"] = field(
        default_factory=list,
        metadata={
            "name": "contextEntry",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )


@dataclass
class TInvocation(TExpression):
    class Meta:
        name = "tInvocation"

    filter: Optional["Filter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    conditional: Optional["Conditional"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    some: Optional["Some"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    every: Optional["Every"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    for_value: Optional["For"] = field(
        default=None,
        metadata={
            "name": "for",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    list_value: Optional["List"] = field(
        default=None,
        metadata={
            "name": "list",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    relation: Optional["Relation"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    function_definition: Optional["FunctionDefinition"] = field(
        default=None,
        metadata={
            "name": "functionDefinition",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    context: Optional["Context"] = field(
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
    invocation: Optional["Invocation"] = field(
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
    binding: list["TBinding"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )


@dataclass
class TRelation(TExpression):
    class Meta:
        name = "tRelation"

    column: list[TInformationItem] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    row: list["TList"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )


@dataclass
class Context(TContext):
    class Meta:
        name = "context"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Invocation(TInvocation):
    class Meta:
        name = "invocation"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Relation(TRelation):
    class Meta:
        name = "relation"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TFunctionDefinition(TExpression):
    class Meta:
        name = "tFunctionDefinition"

    formal_parameter: list[TInformationItem] = field(
        default_factory=list,
        metadata={
            "name": "formalParameter",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    filter: Optional["Filter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    conditional: Optional["Conditional"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    some: Optional["Some"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    every: Optional["Every"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    for_value: Optional["For"] = field(
        default=None,
        metadata={
            "name": "for",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    list_value: Optional["List"] = field(
        default=None,
        metadata={
            "name": "list",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    relation: Optional["Relation"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    function_definition: Optional["FunctionDefinition"] = field(
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
    kind: TFunctionKind = field(
        default=TFunctionKind.FEEL,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass
class FunctionDefinition(TFunctionDefinition):
    class Meta:
        name = "functionDefinition"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TList(TExpression):
    class Meta:
        name = "tList"

    filter: list["Filter"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    conditional: list["Conditional"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    some: list["Some"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    every: list["Every"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    for_value: list["For"] = field(
        default_factory=list,
        metadata={
            "name": "for",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    list_value: list["List"] = field(
        default_factory=list,
        metadata={
            "name": "list",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    relation: list[Relation] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    function_definition: list[FunctionDefinition] = field(
        default_factory=list,
        metadata={
            "name": "functionDefinition",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    context: list[Context] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    decision_table: list[DecisionTable] = field(
        default_factory=list,
        metadata={
            "name": "decisionTable",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    invocation: list[Invocation] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    literal_expression: list[LiteralExpression] = field(
        default_factory=list,
        metadata={
            "name": "literalExpression",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )


@dataclass
class List(TList):
    class Meta:
        name = "list"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TChildExpression:
    class Meta:
        name = "tChildExpression"

    filter: Optional["Filter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    conditional: Optional["Conditional"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    some: Optional["Some"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    every: Optional["Every"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    for_value: Optional["For"] = field(
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
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass
class TConditional(TExpression):
    class Meta:
        name = "tConditional"

    if_value: Optional[TChildExpression] = field(
        default=None,
        metadata={
            "name": "if",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )
    then: Optional[TChildExpression] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )
    else_value: Optional[TChildExpression] = field(
        default=None,
        metadata={
            "name": "else",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )


@dataclass
class TFilter(TExpression):
    class Meta:
        name = "tFilter"

    in_value: Optional[TChildExpression] = field(
        default=None,
        metadata={
            "name": "in",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )
    match: Optional[TChildExpression] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )


@dataclass
class TTypedChildExpression(TChildExpression):
    class Meta:
        name = "tTypedChildExpression"

    type_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "typeRef",
            "type": "Attribute",
        },
    )


@dataclass
class Conditional(TConditional):
    class Meta:
        name = "conditional"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Filter(TFilter):
    class Meta:
        name = "filter"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TIterator(TExpression):
    class Meta:
        name = "tIterator"

    in_value: Optional[TTypedChildExpression] = field(
        default=None,
        metadata={
            "name": "in",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )
    iterator_variable: Optional[str] = field(
        default=None,
        metadata={
            "name": "iteratorVariable",
            "type": "Attribute",
        },
    )


@dataclass
class TFor(TIterator):
    class Meta:
        name = "tFor"

    return_value: Optional[TChildExpression] = field(
        default=None,
        metadata={
            "name": "return",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )


@dataclass
class TQuantified(TIterator):
    class Meta:
        name = "tQuantified"

    satisfies: Optional[TChildExpression] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )


@dataclass
class Every(TQuantified):
    class Meta:
        name = "every"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class For(TFor):
    class Meta:
        name = "for"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Some(TQuantified):
    class Meta:
        name = "some"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TBinding:
    class Meta:
        name = "tBinding"

    parameter: Optional[TInformationItem] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
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


@dataclass
class TContextEntry(TDMNElement):
    class Meta:
        name = "tContextEntry"

    variable: Optional[TInformationItem] = field(
        default=None,
        metadata={
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


@dataclass
class ContextEntry(TContextEntry):
    class Meta:
        name = "contextEntry"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
