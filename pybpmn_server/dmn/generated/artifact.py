from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_artifact import TArtifact

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Artifact(TArtifact):
    class Meta:
        name = "artifact"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
