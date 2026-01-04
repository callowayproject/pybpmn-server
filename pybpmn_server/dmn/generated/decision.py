from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_decision import TDecision

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Decision(TDecision):
    class Meta:
        name = "decision"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
