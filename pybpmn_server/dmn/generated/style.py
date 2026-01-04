from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "http://www.omg.org/spec/DMN/20180521/DI/"


@dataclass
class Style:
    """This element should never be instantiated directly, but rather concrete
    implementation should.

    It is placed there only to be referred in the sequence
    """

    class Meta:
        namespace = "http://www.omg.org/spec/DMN/20180521/DI/"

    extension: Optional["Style.Extension"] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    id: Optional[str] = field(
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
    class Extension:
        other_element: list[object] = field(
            default_factory=list,
            metadata={
                "type": "Wildcard",
                "namespace": "##other",
            },
        )
