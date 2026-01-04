from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_knowledge_source import TKnowledgeSource

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class KnowledgeSource(TKnowledgeSource):
    class Meta:
        name = "knowledgeSource"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
