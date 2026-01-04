from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_association import TAssociation

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Association(TAssociation):
    class Meta:
        name = "association"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
