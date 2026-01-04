"""
Cache managers for storing and managing execution instances in a BPMN server.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pybpmn_server.common.configuration import Settings
from pybpmn_server.interfaces.enums import ExecutionEvent
from pybpmn_server.server.interfaces import ICacheManager

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IExecution
    from pybpmn_server.server.bpmn_server import BPMNServer

logger = logging.getLogger(__name__)


class NoCacheManager(ICacheManager):
    """
    A cache manager that does not store any execution instances.
    """

    def __init__(self, server: BPMNServer):
        super().__init__(server)

    def list(self) -> List[IExecution]:
        return []

    def get_instance(self, _: str) -> Optional[IExecution]:
        return None

    def add(self, _: IExecution):
        return None

    def remove(self, _: str):
        return None

    async def shutdown(self):
        pass

    def restart(self):
        pass


class CacheManager(ICacheManager):
    """
    A cache manager that stores execution instances.
    """

    def __init__(self, configuration: Optional[Settings] = None) -> None:
        from pybpmn_server.common.configuration import settings

        self.configuration = configuration or settings
        self.live_instances: Dict[str, IExecution] = {}

        def on_process_end(data: Dict[str, Any]):
            context = data.get("context")
            if context and hasattr(context, "instance"):
                self.remove(context.instance.id)

        settings.listener.on(ExecutionEvent.process_end, on_process_end)

    def list(self) -> List[IExecution]:
        return list(self.live_instances.values())

    def get_instance(self, instance_id: str) -> Optional[IExecution]:
        return self.live_instances.get(instance_id)

    def add(self, execution: IExecution):
        self.live_instances[execution.id] = execution

    def remove(self, instance_id: str):
        if instance_id in self.live_instances:
            del self.live_instances[instance_id]

    async def shutdown(self):
        logger.info("Shutdown..")
        instances = self.live_instances
        list_to_shutdown = list(instances.values())
        for engine in list_to_shutdown:
            logger.info(f"shutdown engine {engine.name} status : {getattr(engine, 'state', 'unknown')}")
            if engine.id in instances:
                del instances[engine.id]
