"""Behavior loader module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, List

from pybpmn_server.elements.behaviors.error import ErrorEventBehavior
from pybpmn_server.elements.behaviors.escalation import EscalationEventBehavior
from pybpmn_server.elements.behaviors.form import CamundaFormData
from pybpmn_server.elements.behaviors.io import IOBehavior
from pybpmn_server.elements.behaviors.loop import LoopBehavior
from pybpmn_server.elements.behaviors.message_signal import MessageEventBehavior, SignalEventBehavior
from pybpmn_server.elements.behaviors.script import ScriptBehavior
from pybpmn_server.elements.behaviors.terminate import TerminateBehavior
from pybpmn_server.elements.behaviors.timer import TimerBehavior
from pybpmn_server.elements.behaviors.trans_events import CancelEventBehavior, CompensateEventBehavior

if TYPE_CHECKING:
    from pybpmn_server.elements.behaviors.behavior import Behavior
    from pybpmn_server.elements.interfaces import INode


class BehaviorName:
    """
    Names of different behavior types in BPMN elements.
    """

    TimerEventDefinition = "bpmn:TimerEventDefinition"
    LoopCharacteristics = "loopCharacteristics"
    IOSpecification = "ioSpecification"
    TerminateEventDefinition = "bpmn:TerminateEventDefinition"
    MessageEventDefinition = "bpmn:MessageEventDefinition"
    SignalEventDefinition = "bpmn:SignalEventDefinition"
    ErrorEventDefinition = "bpmn:ErrorEventDefinition"
    EscalationEventDefinition = "bpmn:EscalationEventDefinition"
    CancelEventDefinition = "bpmn:CancelEventDefinition"
    CompensateEventDefinition = "bpmn:CompensateEventDefinition"
    CamundaFormData = "camunda:formData"
    CamundaScript = "camunda:script"
    CamundaScript2 = "camunda:executionListener"
    CamundaScript3 = "camunda:taskListener"
    CamundaIO = "camunda:inputOutput"


class BehaviorLoader:
    """
    Loader for behaviors associated with BPMN elements.
    """

    behaviours: ClassVar[List[Dict[str, Any]]] = [
        {"name": BehaviorName.TimerEventDefinition, "funct": lambda node, def_: TimerBehavior(node, def_)},
        {"name": BehaviorName.LoopCharacteristics, "funct": lambda node, def_: LoopBehavior(node, def_)},
        {"name": BehaviorName.CamundaFormData, "funct": lambda node, def_: CamundaFormData(node, def_)},
        {"name": BehaviorName.CamundaIO, "funct": lambda node, def_: IOBehavior(node, def_)},
        {"name": BehaviorName.MessageEventDefinition, "funct": lambda node, def_: MessageEventBehavior(node, def_)},
        {"name": BehaviorName.SignalEventDefinition, "funct": lambda node, def_: SignalEventBehavior(node, def_)},
        {"name": BehaviorName.ErrorEventDefinition, "funct": lambda node, def_: ErrorEventBehavior(node, def_)},
        {
            "name": BehaviorName.EscalationEventDefinition,
            "funct": lambda node, def_: EscalationEventBehavior(node, def_),
        },
        {
            "name": BehaviorName.CompensateEventDefinition,
            "funct": lambda node, def_: CompensateEventBehavior(node, def_),
        },
        {"name": BehaviorName.CancelEventDefinition, "funct": lambda node, def_: CancelEventBehavior(node, def_)},
        {"name": BehaviorName.CamundaScript, "funct": lambda node, def_: ScriptBehavior(node, def_)},
        {"name": BehaviorName.CamundaScript2, "funct": lambda node, def_: ScriptBehavior(node, def_)},
        {"name": BehaviorName.CamundaScript3, "funct": lambda node, def_: ScriptBehavior(node, def_)},
        {"name": BehaviorName.TerminateEventDefinition, "funct": lambda node, def_: TerminateBehavior(node, def_)},
    ]

    @classmethod
    def register(cls, name: str, funct: Callable[[INode, Any], Behavior]) -> None:
        """
        Registers a new behavior with the loader.

        Args:
            name: The name of the behavior.
            funct: The function to create the behavior instance.
        """
        cls.behaviours.append({"name": name, "funct": funct})

    @classmethod
    def load(cls, node: INode) -> None:
        """
        Loads behaviors for the given node.

        Args:
            node: The node to load behaviors for.
        """
        for behav in cls.behaviours:
            if hasattr(node.def_, behav["name"]):
                node.add_behaviour(behav["name"], behav["funct"](node, getattr(node.def_, behav["name"])))
            elif isinstance(node.def_, dict) and behav["name"] in node.def_:
                node.add_behaviour(behav["name"], behav["funct"](node, node.def_[behav["name"]]))

        if hasattr(node.def_, "eventDefinitions") and node.def_.eventDefinitions:
            for ed in node.def_.eventDefinitions:
                for behav in cls.behaviours:
                    if ed.get("$type") == behav["name"] or getattr(ed, "$type", None) == behav["name"]:
                        node.add_behaviour(behav["name"], behav["funct"](node, ed))

        if hasattr(node.def_, "extensionElements") and node.def_.extensionElements:
            values = getattr(node.def_.extensionElements, "values", [])
            for ext in values:
                for behav in cls.behaviours:
                    if ext.get("$type") == behav["name"] or getattr(ext, "$type", None) == behav["name"]:
                        node.add_behaviour(behav["name"], behav["funct"](node, ext))
