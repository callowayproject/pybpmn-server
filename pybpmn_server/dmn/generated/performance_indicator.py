from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_performance_indicator import TPerformanceIndicator

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class PerformanceIndicator(TPerformanceIndicator):
    class Meta:
        name = "performanceIndicator"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
