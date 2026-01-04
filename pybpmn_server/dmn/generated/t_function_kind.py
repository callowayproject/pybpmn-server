from enum import Enum

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


class TFunctionKind(Enum):
    FEEL = "FEEL"
    JAVA = "Java"
    ONNX = "ONNX"
    PMML = "PMML"
