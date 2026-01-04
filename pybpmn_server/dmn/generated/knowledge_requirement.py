from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_knowledge_requirement import TKnowledgeRequirement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class KnowledgeRequirement(TKnowledgeRequirement):
    class Meta:
        name = "knowledgeRequirement"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
