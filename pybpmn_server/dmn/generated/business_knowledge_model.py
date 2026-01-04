from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_business_knowledge_model import TBusinessKnowledgeModel

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class BusinessKnowledgeModel(TBusinessKnowledgeModel):
    class Meta:
        name = "businessKnowledgeModel"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
