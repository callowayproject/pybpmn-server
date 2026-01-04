from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_input_data import TInputData

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class InputData(TInputData):
    class Meta:
        name = "inputData"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
