from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TDMNElement:
    class Meta:
        name = "tDMNElement"

    description: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    extension_elements: Optional["TDMNElement.ExtensionElements"] = field(
        default=None,
        metadata={
            "name": "extensionElements",
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
    label: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    other_attributes: dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##other",
        },
    )

    @dataclass
    class ExtensionElements:
        other_element: list[object] = field(
            default_factory=list,
            metadata={
                "type": "Wildcard",
                "namespace": "##other",
            },
        )
