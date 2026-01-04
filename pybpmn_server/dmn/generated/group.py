from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_group import TGroup

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Group(TGroup):
    class Meta:
        name = "group"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
