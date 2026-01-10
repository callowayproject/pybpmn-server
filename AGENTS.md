# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Build, Lint, and Test Commands

### Installation

```bash
uv sync --extra test  # Install with test dependencies
```

### Running Tests

```bash
uv run pytest              # Run all tests
uv run pytest path/to/test.py::test_function  # Run single test
uv run pytest -k "test_name"  # Run tests matching pattern
uv run pytest --no-cov      # Run tests without coverage
uv run pytest -v            # Verbose output
uv run pytest -s            # Show print statements
```

### Linting and Formatting

```bash
uv run ruff check .                 # Check for issues
uv run ruff check --fix .           # Auto-fix issues
uv run ruff format .                # Format code
uv run black pybpmn_server tests    # Format with black
uv run mypy pybpmn_server           # Type checking
uv run pydoclint                    # Docstring checks
uv run interrogate                  # Documentation coverage
```

### Pre-commit Hooks

```bash
uv run pre-commit run --all-files   # Run all hooks
uv run pre-commit run --files <files>  # Run on specific files
```

### Documentation

```bash
uv run mkdocs serve                 # Serve docs locally
uv run mkdocs build                 # Build docs
```

## Code Style Guidelines

### General Principles

- Write clean, readable, async-first code (this is a workflow engine)
- Use type hints consistently - this codebase uses strict typing
- Follow the Single Responsibility Principle
- Keep functions focused and under 50 lines when possible
- Use descriptive variable and function names

### Python Version and Features

- **Python 3.12+** required
- Use `from __future__ import annotations` for all files to enable postponed evaluation
- Use structural pattern matching where appropriate
- Use dataclasses for simple data containers

### Imports

- Use `TYPE_CHECKING` guard for imports only needed for type hints
- Group imports: stdlib, third-party, local application
- Sort imports with ruff/isort (configured)
- Avoid wildcard imports (`from module import *`)
- Use relative imports for intra-package imports

```python
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Optional

from opentelemetry import trace

from pybpmn_server.engine.execution import Execution
from pybpmn_server.interfaces.enums import ExecutionEvent

if TYPE_CHECKING:
    from pybpmn_server.engine.interfaces import IItem
```

### Type Hints

- Use built-in generics (`list[str]`, `dict[str, int]`) not typing module equivalents
- Use `Optional[T]` instead of `Union[T, None]` or `T | None`
- Use `Any` sparingly - prefer specific types
- Use `cast("Type", value)` for type narrowing
- Annotate all public functions and methods
- Private methods should still have return type annotations

```python
async def start(
    self,
    name: str,
    source: str,
    data: Optional[dict[str, Any]] = None,
    start_node_id: Optional[str] = None,
) -> Optional[Execution]:
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `Engine`, `Token`, `Execution`)
- **Functions/Variables**: `snake_case` (e.g., `get_data`, `execute_task`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private attributes/methods**: Leading underscore (e.g., `_current_node`, `_execute()`)
- **Type variables**: `PascalCase` (e.g., `T`, `ItemT`)
- **Avoid single-letter names** except loop variables (`i`, `k`, `v`) and type variables

### Async/Await

- Use `async def` for all functions that await
- Never block on async code - use `await` or `asyncio.create_task()`
- Use `asyncio.gather()` for concurrent operations
- Handle `asyncio.CancelledError` in long-running tasks

```python
async def execute(self, input_data: Optional[dict[str, Any]] = None) -> Any:
    try:
        result = await self.current_node.execute(item)
        return result
    except Exception as exc:
        await self.exception(exc, execution)
        return None
```

### Error Handling

- Use specific exception types, not bare `except Exception:`
- Let exceptions propagate - catch only where you can handle meaningfully
- Always clean up resources in `finally` blocks or use context managers
- Log errors with `logger.error()` before re-raising or returning None
- Use `try/finally` pattern for lock release in async code

```python
try:
    await self.lock(str(execution.id))
    execution.is_locked = True
    await execution.execute(start_node_id, data)
finally:
    self.running_counter -= 1
    if execution and execution.is_locked:
        await self.release(execution)
```

### Logging

- Use module-level loggers: `logger = logging.getLogger(__name__)`
- Use OpenTelemetry tracing for performance monitoring: `tracer = trace.get_tracer(__name__)`
- Log levels: `DEBUG` (detailed), `INFO` (key actions), `WARNING` (unexpected but handled), `ERROR` (failures)
- Use f-strings for log messages
- Include relevant context (IDs, names, status)

```python
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

logger.info(f"^Action:engine.start {name}")
trace.get_current_span().set_attribute("workflow_name", name)
```

### Docstrings

- Use **Google-style** docstrings (configured in pyproject.toml)
- Document all public classes, methods, and functions
- Include Args, Returns, and Raises sections when applicable
- Use type hints - docstring types are optional when using Google style
- Keep descriptions concise but complete

```python
async def start(
    self,
    name: str,
    source: str,
    data: Optional[dict[str, Any]] = None,
    start_node_id: Optional[str] = None,
) -> Optional[Execution]:
    """
    Starts the execution of a workflow based on the provided parameters.

    This method initializes and manages the execution of a workflow, applying the
    necessary configurations and handling execution control.

    Args:
        name: The name of the workflow to start.
        source: The definition of the workflow to start.
        data: Input data for the workflow execution.
        start_node_id: The ID of the starting node for the workflow execution.

    Returns:
        An instance representing the workflow execution, or None if it failed.
    """
```

### Code Formatting

- **Line length**: 119 characters
- Use `ruff format` or `black` for formatting
- No trailing whitespace
- One blank line between top-level definitions
- Two blank lines between class definitions
- Use parentheses for line continuation

### File Structure

- One public class per file (except closely related classes)
- Put related functionality in same package
- Use `__init__.py` for package exports
- Keep `__init__.py` files minimal - expose only public API

### Testing

- Put tests in `tests/` directory mirroring source structure
- Use `pytest` with `pytest-asyncio` for async tests
- Use `pytest.mark.asyncio` decorator for async test functions
- Use fixtures from `conftest.py` for common setup
- Use `caplog` fixture for logging tests
- Group related tests in classes when appropriate
- Use descriptive test names: `test_<method>_<scenario>`

```python
@pytest.mark.asyncio
async def test_simple_execution(settings: Settings, fixtures_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test that a simple start-token-end workflow executes correctly."""
    caplog.set_level(logging.INFO)
    source = fixtures_path.joinpath("simple.bpmn").read_text(encoding="utf-8")
    engine = Engine(settings)
    await engine.start("simple_test", source)
```

### Pydantic and Settings

- Use Pydantic v2 for settings and data validation
- Use `pydantic-settings` for configuration management
- Settings classes inherit from `BaseSettings`
- Use descriptive field names and types

### Git and Commit Messages

- Write conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Keep commits atomic and focused
- Write meaningful commit body explaining "why"
- Run quality gates before pushing

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
