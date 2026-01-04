from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_named_element import TNamedElement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TDrgelement(TNamedElement):
    class Meta:
        name = "tDRGElement"
