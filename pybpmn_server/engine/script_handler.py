"""This module provides functionality to evaluate and execute scripts."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Union

from pybpmn_server.engine.interfaces import IExecution, IItem, IToken, ScriptHandler

logger = logging.getLogger(__name__)


class DefaultScriptHandler(ScriptHandler):
    """
    Handles evaluation and execution of scripts with advanced input parsing and context management.

    This class is designed to evaluate specific expressions and execute scripts
    within a given context, which could include data and execution instances. It
    supports both inline script evaluation and external Python script execution
    through subprocess calls. The class provides functionality to handle different
    types of expressions and scope configurations while utilizing custom global
    mappings.
    """

    async def evaluate_input_expression(self, item: IItem, exp: Any, date_format: bool = False) -> Any:
        """
        Evaluates input expressions based on the provided item and expression.

        If the expression is empty, returns None. Otherwise, processes the expression
        to handle string values, custom expressions starting with '$', and comma-separated
        values. If date_format is True and the value is a string, attempts to convert
        it to a datetime object.

        Args:
            item: The item context for expression evaluation.
            exp: The expression to evaluate.
            date_format: Flag to indicate date formatting. Defaults to False.

        Returns:
            The evaluated expression value, or None if the expression is empty.
        """
        if not exp:
            return None

        val = exp
        if isinstance(exp, str):
            if exp.startswith("$"):
                val = await self.evaluate_expression(item, exp)
            elif "," in exp:
                val = exp.split(",")

        if date_format and val and isinstance(val, str):
            with contextlib.suppress(ValueError):
                val = datetime.fromisoformat(val.replace("Z", "+00:00"))

        return val

    async def evaluate_expression(self, scope: Union[IItem, IToken], expression: str) -> Any:
        """
        Evaluates a given expression in the context of a provided scope using Python's `eval` or `exec` functions.

        The function determines whether the expression starts with a "$" to adjust its processing accordingly.
        Evaluation is supported for both single-line expressions and multi-line scripts.

        Args:
            scope: The context or scope in which the expression is evaluated. This is used to provide global
                variables during evaluation.
            expression: The code expression or script to evaluate.

        Returns:
            The result of the evaluated expression. Returns `None` if the input
                expression is empty.

        Raises:
            Exception: Propagates any exception encountered during expression evaluation
                after logging the error.
        """
        if not expression:
            return None

        script = expression
        if expression.startswith("$"):
            script = expression[1:]

        try:
            globals_dict = self._get_globals(scope)
            if "\n" not in script and "return " not in script:
                return eval(script, globals_dict)
            else:
                locs: Dict[str, Any] = {}
                exec_script = "def __temp_func__():\n"
                for line in script.split("\n"):
                    exec_script += f"    {line}\n"
                exec_script += "result = __temp_func__()"

                exec(exec_script, globals_dict, locs)
                return locs.get("result")

        except Exception as exc:
            logger.error(f"Error in script evaluation: {script}")
            logger.exception(exc)
            raise exc

    async def execute_script(self, scope: Union[IItem, IExecution], script: str) -> Any:
        """
        Executes a given script in the context of a provided scope using Python's `exec` function.

        Args:
            scope: The context or scope in which the script is executed. This is used to provide global
                variables during execution.
            script: The code script to execute.

        Returns:
            The result of the executed script. Returns `None` if the input script is empty.
        """
        if not script:
            return None

        try:
            if script.startswith("$py"):
                return await self.run_python(scope, script[3:])

            script = script.replace("#", "")  # remove symbol '#'

            globals_dict = self._get_globals(scope)
            locs: Dict[str, Any] = {}

            exec_lines = []
            for line in script.split("\n"):
                if line.strip():
                    exec_lines.append(f"    {line}")

            if not exec_lines:
                return None

            exec_script = "def __temp_func__():\n" + "\n".join(exec_lines) + "\nresult = __temp_func__()"

            exec(exec_script, globals_dict, locs)
            return locs.get("result")

        except Exception as exc:
            logger.error(f"Error in script execution: {script}")
            logger.exception(exc)
            raise exc

    def _get_globals(self, scope: Any) -> Dict[str, Any]:
        """
        Retrieves the global variables for the given scope.

        Args:
            scope: The context or scope in which the script is executed. This is used to provide global
                variables during execution.

        Returns:
            A dictionary containing the global variables for the given scope.
        """
        is_token = hasattr(scope, "start_node_id")
        is_execution = hasattr(scope, "tokens")

        g = {}
        if is_token:
            g["data"] = scope.data
            g["instance"] = scope.execution.instance
            g["input"] = getattr(scope, "input", None)
            g["output"] = getattr(scope, "output", None)
            g["app_delegate"] = scope.execution.app_delegate
            g["app_services"] = getattr(scope.execution, "services_provider", None)
            g["app_utils"] = getattr(g["app_delegate"], "app_utils", None)
            g["item"] = scope  # for backward support
        elif is_execution:
            g["app_delegate"] = scope.app_delegate
            g["instance"] = scope.instance
            g["app_services"] = getattr(scope, "services_provider", None)
            g["app_utils"] = getattr(g["app_delegate"], "app_utils", None)
        else:
            g["item"] = scope
            g["data"] = scope.data
            g["instance"] = scope.token.execution.instance
            g["input"] = getattr(scope, "input", None)
            g["output"] = getattr(scope, "output", None)
            g["app_delegate"] = scope.token.execution.app_delegate
            g["app_services"] = getattr(scope.token.execution, "services_provider", None)
            g["app_utils"] = getattr(g["app_delegate"], "app_utils", None)

        g["this"] = scope
        return g

    async def run_python(self, item: Any, code: str, input_data: Any = None) -> Any:
        """
        Runs a Python script in a subprocess and returns the output.

        Args:
            item: The item associated with the script execution.
            code: The Python code to execute.
            input_data: Optional input data to pass to the script.

        Returns:
            The output of the executed Python script.
        """
        python_cmd = os.environ.get("PYTHON_CMD", "python3")
        data_json = json.dumps(getattr(item, "data", {}))
        item_info = json.dumps(
            {
                "id": getattr(item, "id", None),
                "name": getattr(item, "name", None),
                "elementId": getattr(item, "element_id", None),
            }
        )

        py_code = f"""
import sys, json
input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {{}}
data = {data_json}
item = {item_info}
{code.strip()}
"""

        process = await asyncio.create_subprocess_exec(
            python_cmd,
            "-c",
            py_code,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        input_bytes = json.dumps(input_data).encode() if input_data is not None else b"{}"
        stdout, stderr = await process.communicate(input=input_bytes)

        if process.returncode != 0:
            raise Exception(f"Python error: {stderr.decode() or 'Exit code ' + str(process.returncode)}")

        output = stdout.decode().strip()
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return output
