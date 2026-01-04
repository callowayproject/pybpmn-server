from dataclasses import dataclass

from pybpmn_server.dmn.generated.diagram_element import DiagramElement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20230324/DMNDI/"


@dataclass
class DmndiagramElement(DiagramElement):
    """This element should never be instantiated directly, but rather concrete
    implementation should.

    It is placed there only to be referred in the sequence
    """

    class Meta:
        name = "DMNDiagramElement"
        namespace = "https://www.omg.org/spec/DMN/20230324/DMNDI/"
