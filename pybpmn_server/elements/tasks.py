"""Implementation for BPMN tasks."""

from __future__ import annotations

import builtins
import contextlib
import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

from opentelemetry import trace
from pybpmn_parser.bpmn.activities.business_rule_task import BusinessRuleTask as BusinessRuleTaskDef
from pybpmn_parser.bpmn.activities.call_activity import CallActivity as CallActivityDef
from pybpmn_parser.bpmn.activities.receive_task import ReceiveTask as ReceiveTaskDef
from pybpmn_parser.bpmn.activities.script_task import ScriptTask as ScriptTaskDef
from pybpmn_parser.bpmn.activities.send_task import SendTask as SendTaskDef
from pybpmn_parser.bpmn.activities.service_task import ServiceTask as ServiceTaskDef
from pybpmn_parser.bpmn.activities.sub_process import (
    AdHocSubProcess as AdHocSubProcessDef,
)
from pybpmn_parser.bpmn.activities.sub_process import (
    SubProcess as SubProcessDef,
)
from pybpmn_parser.bpmn.activities.user_task import UserTask as UserTaskDef

from pybpmn_server.common.utils import import_string
from pybpmn_server.elements.node import Node
from pybpmn_server.interfaces.enums import BpmnType, ExecutionStatus, ItemStatus, NodeAction, TokenType

if TYPE_CHECKING:
    from pybpmn_server.elements.interfaces import INode
    from pybpmn_server.elements.process import Process
    from pybpmn_server.engine.item import IItem

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class ScriptTask(Node[ScriptTaskDef]):
    """Script task implementation."""

    def __init__(self, type_: str, def_: ScriptTaskDef, id_: str, process: Process):
        super().__init__(type_, def_, id_, process)
        self.script = self.def_.script

    @tracer.start_as_current_span("script_task.run")
    async def run(self, item: IItem) -> NodeAction:
        """
        Execute the script task.

        Args:
            item: The current item being processed.

        Returns:
            The action to take after executing the script task.
        """
        trace.get_current_span().set_attributes({"node_id": self.id, "node_name": self.name or self.id})
        if self.script:
            item.token.log("executing script task")
            item.token.log(self.script)
            ret = item.context.script_handler.execute_script(item, self.script)
            if isinstance(ret, dict):
                if ret.get("escalation"):
                    item.token.process_escalation(ret["escalation"], item)
                if ret.get("bpmn_error"):
                    item.token.process_error(ret["bpmn_error"], item)
        return NodeAction.END


class ServiceTask(Node[ServiceTaskDef]):
    """Service task implementation."""

    def __init__(self, type_: str, def_: ServiceTaskDef, id_: str, process: Process):
        super().__init__(type_, def_, id_, process)
        self.implementation = self.def_.implementation
        self.delegate_expression = getattr(self.def_, "camunda_delegate_expression", None)

    @property
    def service_name(self) -> Optional[str]:
        """
        Returns the service name for the task, either from implementation or delegate expression.
        """
        if self.implementation:
            return self.implementation
        elif self.delegate_expression:
            return self.delegate_expression
        return None

    @tracer.start_as_current_span("service_task.run")
    async def run(self, item: IItem) -> NodeAction:
        """
        Executes the service task by invoking the specified service with the provided item input.
        """
        trace.get_current_span().set_attributes({"node_id": self.id, "node_name": self.name or self.id})

        item.context.action = NodeAction.WAIT
        item.context.item = item

        config = item.token.execution.configuration
        logger.info(f"invoking service:{self.service_name} input:{json.dumps(item.input, default=str)}")

        service_provider = config.services_provider
        method = import_string(service_provider[self.service_name]) if service_provider and self.service_name else None
        ret = method(item.input, item.context) if method and callable(method) else None

        logger.info(f"service returned {ret}")
        item.output = ret
        logger.info(f"service {self.service_name} completed-output:{ret}{item.output}")

        if isinstance(ret, dict):
            if ret.get("escalation"):
                item.token.process_escalation(ret["escalation"], item)
            if ret.get("bpmn_error"):
                item.token.process_error(ret["bpmn_error"], item)

        if hasattr(item.context, "action") and item.context.action == NodeAction.WAIT:
            return item.context.action

        return NodeAction.END


class BusinessRuleTask(Node[BusinessRuleTaskDef]):
    """Business rule task implementation."""

    def __init__(self, type_: str, def_: BusinessRuleTaskDef, id_: str, process: Process):
        super().__init__(type_, def_, id_, process)

        self.decision_ref = getattr(self.def_, "camunda_decision_ref", None)

    @tracer.start_as_current_span("business_rule_task.run")
    async def run(self, item: IItem) -> NodeAction:
        """Run the business rule task."""
        # TODO (pybpmn-server-1ay): refactor to use DMN engine
        # from pybpmn_server.dmn.dmn_engine import DMNEngine
        #
        # if self.decision_ref:
        #     config = item.token.execution.server.configuration
        #     path = config.definitions_path
        #     item.token.log(f"invoking business rule:{self.decision_ref}")
        #
        #     # TODO (pybpmn-server-cag): Store the business rules in the database and import them when importing the base file
        #     file_path = f"{path}/{self.decision_ref}.dmn.xml"
        #     dmn = await DMNEngine().load(file_path)
        #     item.output = dmn.evaluate(item.input)

        return NodeAction.END


class SendTask(Node[SendTaskDef]):
    """Send task implementation."""

    @property
    def is_catching(self) -> bool:
        """Is the task catching?"""
        return False


class UserTask(Node[UserTaskDef]):
    """User task implementation."""

    @tracer.start_as_current_span("user_task.end")
    async def end(self, item: IItem, cancel: bool = False) -> None:
        """End the user task."""
        trace.get_current_span().set_attributes(
            {"node_id": self.id, "node_name": self.name or self.id, "item_id": item.id}
        )
        await super().end(item, cancel)

    @tracer.start_as_current_span("user_task.run")
    async def start(self, item: IItem) -> NodeAction:
        """Start the user task."""
        trace.get_current_span().set_attributes({"node_id": self.id, "node_name": self.name, "item_id": item.id})
        assignable_attrs = [
            "camunda_assignee",
            "camunda_candidate_groups",
            "camunda_candidate_users",
            "camunda_due_date",
            "camunda_follow_up_date",
            "camunda_priority",
        ]
        for attr in assignable_attrs:
            await self.set_assign_val(item, attr, date_format=(attr in ("camunda_due_date", "camunda_follow_up_date")))

        if self.lane:
            if item.candidate_groups is None:
                item.candidate_groups = []
            item.candidate_groups.append(self.lane)

        return await super().start(item)

    async def set_assign_val(self, item: IItem, attr: str, date_format: bool = False) -> None:
        """Set an assignable attribute."""
        exp = getattr(self.def_, attr, None)
        if not exp:
            return

        if exp.startswith("$"):
            val = item.context.script_handler.evaluate_expression(item, exp)
        elif exp.startswith("#"):
            val = item.context.script_handler.execute_script(item, f"return {exp[1:]}")
        elif "," in exp:
            val = exp.split(",")
        else:
            val = exp

        if date_format and val and isinstance(val, str):
            with contextlib.suppress(builtins.BaseException):
                val = datetime.fromisoformat(val.replace("Z", "+00:00"))

        setattr(item, attr, val)
        item.token.log(f"..setting attribute {attr} exp: {exp}={val}")

    @property
    def requires_wait(self) -> bool:
        """Does this task require waiting?"""
        return True

    @property
    def can_be_invoked(self) -> bool:
        """Can this task be invoked?"""
        return True


class ReceiveTask(Node[ReceiveTaskDef]):
    """Receive task implementation."""

    @property
    def is_catching(self) -> bool:
        """Is the task catching?"""
        return True

    @property
    def requires_wait(self) -> bool:
        """Does this task require waiting?"""
        return True

    @property
    def can_be_invoked(self) -> bool:
        """Can this task be invoked?"""
        return True


class SubProcess(Node[SubProcessDef]):
    """Subprocess task implementation."""

    def __init__(self, type_: str, def_: SubProcessDef, id_: str, process: Any):
        super().__init__(type_, def_, id_, process)
        self.child_process: Optional[Process] = None

    @property
    def requires_wait(self) -> bool:
        """Does this task require waiting?"""
        return True

    @property
    def can_be_invoked(self) -> bool:
        """Can this task be invoked?"""
        return False

    @tracer.start_as_current_span("subprocess_task.start")
    async def start(self, item: IItem) -> NodeAction:
        """
        Start the subprocess task.
        """
        trace.get_current_span().set_attributes({"node_id": self.id, "node_name": self.name, "item_id": item.id})

        token = item.token
        token.log(f"..executing a sub process item:{item.id}")

        if not self.child_process:
            return NodeAction.CONTINUE

        start_node = self.child_process.get_start_nodes()[0]
        item.status = ItemStatus.wait

        dp = self.id
        if token.loop and len(token.path) == 1:
            dp = token.data_path
        elif token.data_path:
            dp = f"{token.data_path}.{self.id}"

        from ..engine.token import Token

        new_token = await Token.start_new_token(
            TokenType.SubProcess, token.execution, start_node, dp, token, item, None, None, True
        )

        await self.child_process.start(token.execution, new_token)
        await self.start_boundary_events(item, new_token)
        await new_token.execute(None)

        if item.status == ItemStatus.wait:
            return NodeAction.WAIT
        return NodeAction.CONTINUE


class AdHocSubProcess(Node[AdHocSubProcessDef]):
    """Ad-hoc subprocess task implementation."""

    def __init__(self, type_: str, def_: AdHocSubProcessDef, id_: str, process: Any):
        super().__init__(type_, def_, id_, process)
        self.child_process: Optional[Process] = None

    @property
    def requires_wait(self) -> bool:
        """Does this task require waiting?"""
        return True

    @property
    def can_be_invoked(self) -> bool:
        """Can this task be invoked?"""
        return False

    @tracer.start_as_current_span("adhoc_subprocess_task.start")
    async def start(self, item: IItem) -> NodeAction:
        """
        Start the ad-hoc subprocess task.
        """
        trace.get_current_span().set_attributes({"node_id": self.id, "node_name": self.name, "item_id": item.id})

        token = item.token
        token.log(f"..executing an ad-hoc sub process item:{item.id}")

        if not self.child_process:
            return NodeAction.CONTINUE

        nodes = self.get_ad_hoc_nodes()
        if not nodes:
            return NodeAction.CONTINUE

        start_node = nodes[0]
        item.status = ItemStatus.wait

        from ..engine.token import Token

        new_token = await Token.start_new_token(
            TokenType.SubProcess, token.execution, start_node, self.id, token, item, None, None, True
        )

        await self.child_process.start(token.execution, new_token)
        await self.start_boundary_events(item, new_token)
        await new_token.execute(None)

        for _i, node in enumerate(nodes[1:], 1):
            item.token.log(f"child node {node.id} {node.type} inbounds {len(node.inbounds)}")
            await Token.start_new_token(
                TokenType.AdHoc, token.execution, node, self.id, token, item, None, None, False
            )

        return NodeAction.WAIT

    @tracer.start_as_current_span("adhoc_subprocess_task.end")
    async def end(self, item: IItem, cancel: bool = False) -> None:
        """
        End the ad-hoc subprocess task.
        """
        trace.get_current_span().set_attributes({"node_id": self.id, "node_name": self.name, "item_id": item.id})
        await super().end(item, cancel)
        children = item.token.get_children_tokens()
        for tok in children:
            if tok.type == "AdHoc":
                await tok.end(True)

    def get_ad_hoc_nodes(self) -> List[INode]:
        """
        Retrieves a list of ad hoc nodes from the child process.

        Ad hoc nodes are defined as nodes that are not of type `EndEvent` or `SequenceFlow` and do not have any
        inbound connections. If the child process is not available, an empty list is returned.

        Returns:
            A list of ad hoc nodes from the child process. If no such nodes exist or the child process is unavailable,
                an empty list is returned.
        """
        if not self.child_process:
            return []
        nodes = self.child_process.children_nodes
        return [
            node
            for node in nodes
            if node.type not in (BpmnType.EndEvent, BpmnType.SequenceFlow) and len(node.inbounds) == 0
        ]


class CallActivity(Node[CallActivityDef]):
    """A call activity node that invokes another process."""

    @property
    def called_element(self) -> Optional[str]:
        """
        Returns the called element for the call activity.
        """
        return self.def_.called_element

    @property
    def requires_wait(self) -> bool:
        """Does this task require waiting?"""
        return True

    @property
    def can_be_invoked(self) -> bool:
        """Can this task be invoked?"""
        return False

    @staticmethod
    async def execution_ended(execution: Any) -> None:
        """
        Handles the end of execution for a call activity.
        """
        item_id = execution.instance.parent_item_id
        engine = execution.server.engine
        await engine.invoke({"items.id": item_id}, execution.instance.data)

    @tracer.start_as_current_span("call_activity_task.start")
    async def start(self, item: IItem) -> NodeAction:
        """
        Starts the execution of a call activity.
        """
        trace.get_current_span().set_attributes({"node_id": self.id, "node_name": self.name, "item_id": item.id})
        token = item.token
        token.log(f"..executing a call activity for item:{item.id} calling {self.called_element}")

        context = item.context
        model_name = self.called_element
        if not model_name:
            return NodeAction.CONTINUE

        response = await context.engine.start(model_name, item.input, None, None, {"parent_item_id": item.id})

        token.log(f"..end of executing a call activity for item:{item.id} calling {self.called_element}")
        token.log(f"..response :{response.execution.status}")

        if response.execution.status == ExecutionStatus.end:
            return NodeAction.CONTINUE
        return NodeAction.WAIT
