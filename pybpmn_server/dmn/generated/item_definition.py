from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_item_definition import TItemDefinition

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class ItemDefinition(TItemDefinition):
    class Meta:
        name = "itemDefinition"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
