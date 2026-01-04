# Step 4 Plan: BPMN Elements + Behaviours (Coupled Unit)

## Scope
Translate the core BPMN element model and execution behaviours:
- `src/elements/Element.ts` -> `pybpmn_server/elements/element.py`
- `src/elements/Node.ts` -> `pybpmn_server/elements/node.py`
- `src/elements/Flow.ts` -> `pybpmn_server/elements/flow.py`
- `src/elements/behaviours/*` -> `pybpmn_server/elements/behaviours/*.py`
- `src/elements/NodeLoader.ts` -> `pybpmn_server/elements/node_loader.py`
- `src/elements/Tasks.ts` -> `pybpmn_server/elements/tasks.py`
- `src/elements/Gateway.ts` -> `pybpmn_server/elements/gateway.py`
- `src/elements/Events.ts` -> `pybpmn_server/elements/events.py`
- `src/elements/Transaction.ts` -> `pybpmn_server/elements/transaction.py`
- `src/elements/Process.ts` -> `pybpmn_server/elements/process.py`
- `src/elements/Definition.ts` -> `pybpmn_server/elements/definition.py`

## Public API Surface
- `Element`, `Node`, `Flow`, `Process`, `Definition` base classes.
- `NodeLoader` for instantiating specific BPMN types.
- Specialized classes like `UserTask`, `ServiceTask`, `ParallelGateway`, `StartEvent`, etc.
- `Behaviour` base and specific implementations (Timer, Script, IO, etc.).

## Dependencies
- `pybpmn_server/interfaces/*.py`
- `pybpmn_server/engine/*.py` (Item, Token, Loop, Model)
- `pybpmn_server/common/*.py` (Logger, Timer)
- External: `RestrictedPython` (for Script behaviour later, stubbed for now), `croniter` (for Timer behaviour).

## Risk Notes
- **Cycle node <-> Behaviour:** This is a known cycle. Python forward refs and `TYPE_CHECKING` will be used.
- **BPMN-Moddle:** The original uses `bpmn-moddle` for parsing. We will use `IElementData` and `IDefinitionData` abstractions to decouple the engine from the parser for now.
- **Asynchronous Execution:** Node execution is async in TS and will be `async` in Python.

## Verification Plan
- **Mypy:** Check all new modules.
- **Pytest:** Test element instantiation, behaviour attachment, and basic execution flow (e.g., Node -> Item -> Flow).
- **Contract:** Ensure `INode`, `IElement`, `IFlow` protocols are fully satisfied by the concrete classes.
