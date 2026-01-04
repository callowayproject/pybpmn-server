from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_invocable import TInvocable

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Invocable(TInvocable):
    class Meta:
        name = "invocable"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
