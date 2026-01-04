from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_decision_table import TDecisionTable

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class DecisionTable(TDecisionTable):
    class Meta:
        name = "decisionTable"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
