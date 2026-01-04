from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_information_item import TInformationItem

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class InformationItem(TInformationItem):
    class Meta:
        name = "informationItem"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
