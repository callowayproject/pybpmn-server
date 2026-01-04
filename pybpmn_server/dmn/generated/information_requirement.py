from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_information_requirement import TInformationRequirement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class InformationRequirement(TInformationRequirement):
    class Meta:
        name = "informationRequirement"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
