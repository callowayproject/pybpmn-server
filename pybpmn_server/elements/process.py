"""Process element implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pybpmn_server.interfaces.enums import NodeSubtype, TokenType

if TYPE_CHECKING:
    from pybpmn_parser.bpmn.process.process import Process as ProcessDefinition

    from pybpmn_server.elements.interfaces import INode
    from pybpmn_server.engine.interfaces import IExecution, IItem, IToken


class Process:
    """
    Represents a BPMN process element, encapsulating its definition and related components.
    """

    def __init__(self, definition: ProcessDefinition, parent: Optional[Process] = None):
        self.id = definition.id
        self.is_executable = definition.is_executable
        self.name = definition.name
        self.def_ = definition
        self.parent = parent
        self.children_nodes: List[INode] = []
        self.event_sub_processes: List[Process] = []
        self.sub_process_events: List[IItem] = []
        self.scripts: Dict[str, List[str]] = {}
        self.candidate_starter_groups = getattr(definition, "camunda_candidate_starter_groups", None)
        self.candidate_starter_users = getattr(definition, "camunda_candidate_starter_users", None)
        self.history_time_to_live = getattr(definition, "camunda_history_time_to_live", None)
        self.is_startable_in_tasklist = getattr(definition, "camunda_is_startable_in_tasklist", True)

    def init(self, children: List[INode], event_sub_processes: List[Process]) -> None:
        """
        Initializes the process with its children nodes and event sub-processes.
        """
        self.children_nodes = children
        self.event_sub_processes = event_sub_processes

    async def start(self, execution: IExecution, parent_token: Optional[IToken]) -> None:
        """
        Starts the process execution, initiating the start event and handling subprocess events.
        """
        from pybpmn_server.engine.token import Token as TokenClass

        await self.do_event(execution, "start")

        self.sub_process_events = []
        events = []
        for p in self.event_sub_processes:
            events.extend(p.get_start_nodes())

        for st in events:
            execution.log(f"..starting event start subprocess {st.id}")
            if parent_token and parent_token.id == 0:
                parent_token = None
            new_token = await TokenClass.start_new_token(
                TokenType.EventSubProcess, execution, st, None, parent_token, None, None
            )
            if new_token.current_item:
                self.sub_process_events.append(new_token.current_item)

    async def end(self, execution: IExecution) -> None:
        """
        Ends the process execution, terminating any remaining event subprocess tokens.
        """
        if getattr(execution, "ending", False):
            return
        execution.ending = True

        await self.do_event(execution, "end")

        tks = [tk for tk in execution.tokens.values() if tk.type == "EventSubProcess" and tk.parent_token is None]

        for tk in tks:
            await tk.terminate()

        if hasattr(execution, "ending"):
            delattr(execution, "ending")

    def get_start_node(self, user_invokable: bool = False) -> Optional[INode]:
        """
        Retrieves the start node for the process, considering user-invokable start events.
        """
        nodes = self.get_start_nodes(user_invokable)
        return nodes[0] if nodes else None

    def get_start_nodes(self, user_invokable: bool = False) -> List[INode]:
        """
        Retrieves the start nodes for the process, considering user-invokable start events.
        """
        starts = []
        for node in self.children_nodes:
            is_start_event = node.type == "bpmn:StartEvent"
            is_invalid_subtype = node.sub_type in (
                NodeSubtype.timer,
                NodeSubtype.error,
                NodeSubtype.message,
                NodeSubtype.signal,
            )
            if is_start_event and not (user_invokable and is_invalid_subtype):
                starts.append(node)
        return starts

    def get_event_sub_process_start(self) -> List[INode]:
        """
        Retrieves the start nodes for all event subprocesses within the process.
        """
        starts = []
        for sp in self.event_sub_processes:
            start_nodes = sp.get_start_nodes()
            starts.extend(start_nodes)
        return starts

    async def do_event(
        self, execution: IExecution, event: str, event_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Executes scripts associated with an event within the process, handling event details and execution events.
        """
        execution.log(f"Process({self.name}|{self.id}).do_event: executing script for event:{event}")
        event_details = event_details or {}
        scripts = self.scripts.get(event, [])
        for script in scripts:
            execution.script_handler.execute_script(execution, script)

        await execution.do_execution_event(self, event, event_details)
