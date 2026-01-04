"""Models for BPMN Server DMN."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class InputEntry:
    id: str
    input: str
    description: str = ""
    text: str = ""
    operators: list[str] = field(default_factory=list)


@dataclass
class OutputEntry:
    id: str
    output: str
    description: str = ""
    text: str = ""
    parsed_value: str | None = None


@dataclass
class Rule:
    id: str
    description: str = ""
    input_entries: list[InputEntry] = field(default_factory=list)
    output_entries: list[OutputEntry] = field(default_factory=list)

    def output_as_dict(self):
        out = {entry.output: entry.parsed_value for entry in self.output_entries}
        return out


@dataclass
class DecisionTable:
    id: str
    name: str
    inputs: list[InputEntry] = field(default_factory=list)
    outputs: list[OutputEntry] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)


@dataclass
class Decision:
    """A decision."""

    id: str
    name: str
    decision_tables: list[DecisionTable] = field(default_factory=list)


@dataclass
class Input:
    id: str
    label: str
    name: str
    type_ref: str


@dataclass
class Output:
    id: str
    label: str
    name: str
    type_ref: str


@dataclass
class DMNElement:
    """DMNElement is the abstract superclass for the decision model elements."""

    id: Optional[str]
    """Optional identifier for this element. SHALL be unique within its containing Definitions element."""

    description: Optional[str]
    """A description of this element."""

    label: Optional[str]
    """An alternative short description of this element.
    It should primarily be used on elements that do not have a name attribute, e.g., an Input Expression."""


@dataclass
class NamedElement(DMNElement):
    """NamedElement is the abstract superclass for elements that have a name attribute."""

    name: str
