from dataclasses import dataclass, field
from typing import Optional

from pybpmn_server.dmn.generated.association import Association
from pybpmn_server.dmn.generated.business_knowledge_model import BusinessKnowledgeModel
from pybpmn_server.dmn.generated.decision import Decision
from pybpmn_server.dmn.generated.decision_service import DecisionService
from pybpmn_server.dmn.generated.dmndi import Dmndi
from pybpmn_server.dmn.generated.group import Group
from pybpmn_server.dmn.generated.import_mod import Import
from pybpmn_server.dmn.generated.input_data import InputData
from pybpmn_server.dmn.generated.knowledge_source import KnowledgeSource
from pybpmn_server.dmn.generated.organization_unit import OrganizationUnit
from pybpmn_server.dmn.generated.performance_indicator import PerformanceIndicator
from pybpmn_server.dmn.generated.t_element_collection import TElementCollection
from pybpmn_server.dmn.generated.t_item_definition import TItemDefinition
from pybpmn_server.dmn.generated.t_named_element import TNamedElement
from pybpmn_server.dmn.generated.text_annotation import TextAnnotation

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class TDefinitions(TNamedElement):
    class Meta:
        name = "tDefinitions"

    import_value: list[Import] = field(
        default_factory=list,
        metadata={
            "name": "import",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    item_definition: list[TItemDefinition] = field(
        default_factory=list,
        metadata={
            "name": "itemDefinition",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    knowledge_source: list[KnowledgeSource] = field(
        default_factory=list,
        metadata={
            "name": "knowledgeSource",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    input_data: list[InputData] = field(
        default_factory=list,
        metadata={
            "name": "inputData",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    decision_service: list[DecisionService] = field(
        default_factory=list,
        metadata={
            "name": "decisionService",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    business_knowledge_model: list[BusinessKnowledgeModel] = field(
        default_factory=list,
        metadata={
            "name": "businessKnowledgeModel",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    decision: list[Decision] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    association: list[Association] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    text_annotation: list[TextAnnotation] = field(
        default_factory=list,
        metadata={
            "name": "textAnnotation",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    group: list[Group] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    element_collection: list[TElementCollection] = field(
        default_factory=list,
        metadata={
            "name": "elementCollection",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    organization_unit: list[OrganizationUnit] = field(
        default_factory=list,
        metadata={
            "name": "organizationUnit",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    performance_indicator: list[PerformanceIndicator] = field(
        default_factory=list,
        metadata={
            "name": "performanceIndicator",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20240513/MODEL/",
        },
    )
    dmndi: Optional[Dmndi] = field(
        default=None,
        metadata={
            "name": "DMNDI",
            "type": "Element",
            "namespace": "https://www.omg.org/spec/DMN/20230324/DMNDI/",
        },
    )
    expression_language: str = field(
        default="https://www.omg.org/spec/DMN/20240513/FEEL/",
        metadata={
            "name": "expressionLanguage",
            "type": "Attribute",
        },
    )
    type_language: str = field(
        default="https://www.omg.org/spec/DMN/20240513/FEEL/",
        metadata={
            "name": "typeLanguage",
            "type": "Attribute",
        },
    )
    namespace: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    exporter: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    exporter_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "exporterVersion",
            "type": "Attribute",
        },
    )
