from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.alignment_kind import AlignmentKind
from pybpmn_server.dmn.generated.color import Color
from pybpmn_server.dmn.generated.style import Style

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20230324/DMNDI/"


@dataclass
class Dmnstyle(Style):
    class Meta:
        name = "DMNStyle"
        namespace = "https://www.omg.org/spec/DMN/20230324/DMNDI/"

    fill_color: Optional[Color] = field(
        default=None,
        metadata={
            "name": "FillColor",
            "type": "Element",
        },
    )
    stroke_color: Optional[Color] = field(
        default=None,
        metadata={
            "name": "StrokeColor",
            "type": "Element",
        },
    )
    font_color: Optional[Color] = field(
        default=None,
        metadata={
            "name": "FontColor",
            "type": "Element",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "fontFamily",
            "type": "Attribute",
        },
    )
    font_size: Optional[float] = field(
        default=None,
        metadata={
            "name": "fontSize",
            "type": "Attribute",
        },
    )
    font_italic: Optional[bool] = field(
        default=None,
        metadata={
            "name": "fontItalic",
            "type": "Attribute",
        },
    )
    font_bold: Optional[bool] = field(
        default=None,
        metadata={
            "name": "fontBold",
            "type": "Attribute",
        },
    )
    font_underline: Optional[bool] = field(
        default=None,
        metadata={
            "name": "fontUnderline",
            "type": "Attribute",
        },
    )
    font_strike_through: Optional[bool] = field(
        default=None,
        metadata={
            "name": "fontStrikeThrough",
            "type": "Attribute",
        },
    )
    label_horizontal_alignement: Optional[AlignmentKind] = field(
        default=None,
        metadata={
            "name": "labelHorizontalAlignement",
            "type": "Attribute",
        },
    )
    label_vertical_alignment: Optional[AlignmentKind] = field(
        default=None,
        metadata={
            "name": "labelVerticalAlignment",
            "type": "Attribute",
        },
    )
