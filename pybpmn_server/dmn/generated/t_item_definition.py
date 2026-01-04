from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_function_item import TFunctionItem
from pybpmn_server.dmn.generated.t_named_element import TNamedElement
from pybpmn_server.dmn.generated.t_unary_tests import TUnaryTests

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TItemDefinition(TNamedElement):
    class Meta:
        name = "tItemDefinition"

    type_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "typeRef",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    allowed_values: Optional[TUnaryTests] = field(
        default=None,
        metadata={
            "name": "allowedValues",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    type_constraint: Optional[TUnaryTests] = field(
        default=None,
        metadata={
            "name": "typeConstraint",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    item_component: list["TItemDefinition"] = field(
        default_factory=list,
        metadata={
            "name": "itemComponent",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    function_item: Optional[TFunctionItem] = field(
        default=None,
        metadata={
            "name": "functionItem",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    type_language: Optional[str] = field(
        default=None,
        metadata={
            "name": "typeLanguage",
            "type": "Attribute",
        },
    )
    is_collection: bool = field(
        default=False,
        metadata={
            "name": "isCollection",
            "type": "Attribute",
        },
    )
