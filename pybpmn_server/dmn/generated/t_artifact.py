from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_dmnelement import TDMNElement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TArtifact(TDMNElement):
    class Meta:
        name = "tArtifact"
