# Step 5 Plan: Execution Orchestration

## Scope
Translate the core orchestration logic of the engine:
- `src/engine/Execution.ts` -> `pybpmn_server/engine/execution.py`
- `src/engine/ScriptHandler.ts` -> `pybpmn_server/engine/script_handler.py`
- `src/engine/DefaultAppDelegate.ts` -> `pybpmn_server/engine/default_app_delegate.py`

## Public API Surface
- `Execution` class (implements `IExecution`)
- `ScriptHandler` class (implements `IScriptHandler`)
- `DefaultAppDelegate` class (implements `IAppDelegate`)

## Dependencies
- `pybpmn_server/interfaces/*.py`
- `pybpmn_server/common/*.py`
- `pybpmn_server/engine/{item,token,loop,model}.py`
- `pybpmn_server/elements/*.py`
- Stubs/Mocks from `pybpmn_server/stubs.py`:
    - `IBPMNServer`
    - `IDataStore`
    - `IModelsDatastore`
    - `ICacheManager`
    - `ICron`

## Risk Notes
- `Execution` is highly coupled with `Token`. Cycle is managed via forward refs and `TYPE_CHECKING`.
- `ScriptHandler` in TypeScript uses Node's `vm`. As per fixed decisions, it will eventually use `RestrictedPython`. In this step, it will be a stub or a simple `eval`/`exec` for basic testing.
- `DefaultAppDelegate` provides default implementations for various hooks.
- Asynchronous patterns (`async/await`) must be carefully preserved for execution flow.
