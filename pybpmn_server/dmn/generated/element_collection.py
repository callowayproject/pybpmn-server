from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_element_collection import TElementCollection

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class ElementCollection(TElementCollection):
    class Meta:
        name = "elementCollection"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
