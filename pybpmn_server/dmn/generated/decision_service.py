from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_decision_service import TDecisionService

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class DecisionService(TDecisionService):
    class Meta:
        name = "decisionService"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
