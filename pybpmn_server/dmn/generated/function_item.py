from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_function_item import TFunctionItem

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class FunctionItem(TFunctionItem):
    class Meta:
        name = "functionItem"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
