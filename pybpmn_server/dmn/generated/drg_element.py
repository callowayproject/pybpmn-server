from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_drgelement import TDrgelement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class DrgElement(TDrgelement):
    class Meta:
        name = "drgElement"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
