from dataclasses import dataclass

from pybpmn_server.dmn.generated.edge import Edge

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20230324/DMNDI/"


@dataclass
class DmndecisionServiceDividerLine(Edge):
    class Meta:
        name = "DMNDecisionServiceDividerLine"
        namespace = "https://www.omg.org/spec/DMN/20230324/DMNDI/"
