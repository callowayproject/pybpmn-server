from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_business_context_element import TBusinessContextElement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class BusinessContextElement(TBusinessContextElement):
    class Meta:
        name = "businessContextElement"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
