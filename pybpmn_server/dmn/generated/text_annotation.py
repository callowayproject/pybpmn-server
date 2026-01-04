from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_text_annotation import TTextAnnotation

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TextAnnotation(TTextAnnotation):
    class Meta:
        name = "textAnnotation"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
