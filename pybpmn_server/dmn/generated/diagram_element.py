from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.dmnstyle import Dmnstyle
from pybpmn_server.dmn.generated.style import Style

__NAMESPACE__ = "http://www.omg.org/spec/DMN/20180521/DI/"


@dataclass
class DiagramElement:
    """DiagramElement is the abstract super type of all elements in diagrams,
    including diagrams themselves.

    When contained in a diagram, diagram elements are laid out relative
    to the diagram's origin.

    Attributes:
        extension:
        dmnstyle:
        style: an optional locally-owned style for this diagram element.
        shared_style: a reference to an optional shared style element
            for this diagram element.
        id:
        other_attributes:
    """

    extension: Optional["DiagramElement.Extension"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.omg.org/spec/DMN/20180521/DI/",
        },
    )
    dmnstyle: Optional[Dmnstyle] = field(
        default=None,
        metadata={
            "name": "DMNStyle",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20230324/DMNDI/",
        },
    )
    style: Optional[Style] = field(
        default=None,
        metadata={
            "name": "Style",
            "type": "Element",
            "namespace": "http://www.omg.org/spec/DMN/20180521/DI/",
        },
    )
    shared_style: Optional[str] = field(
        default=None,
        metadata={
            "name": "sharedStyle",
            "type": "Attribute",
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
