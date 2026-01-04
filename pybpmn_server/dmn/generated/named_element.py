from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_named_element import TNamedElement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class NamedElement(TNamedElement):
    class Meta:
        name = "namedElement"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
