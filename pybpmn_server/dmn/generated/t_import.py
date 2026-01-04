from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.t_named_element import TNamedElement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TImport(TNamedElement):
    class Meta:
        name = "tImport"

    namespace: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    location_uri: Optional[str] = field(
        default=None,
        metadata={
            "name": "locationURI",
            "type": "Attribute",
        },
    )
    import_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "importType",
            "type": "Attribute",
            "required": True,
        },
    )
