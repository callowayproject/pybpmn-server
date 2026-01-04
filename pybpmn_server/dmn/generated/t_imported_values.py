from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_import import TImport

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TImportedValues(TImport):
    class Meta:
        name = "tImportedValues"

    imported_element: Optional[str] = field(
        default=None,
        metadata={
            "name": "importedElement",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
            "required": True,
        },
    )
    expression_language: Optional[str] = field(
        default=None,
        metadata={
            "name": "expressionLanguage",
            "type": "Attribute",
        },
    )
