from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_definitions import TDefinitions

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Definitions(TDefinitions):
    class Meta:
        name = "definitions"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
