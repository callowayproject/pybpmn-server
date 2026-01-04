# Migration Strategy: TypeScript to Python

This document outlines a safe, incremental conversion path from the TypeScript `bpmn-server` to a Python-based implementation.
## Decisions
- **BPMN Parser Choice**
    - The TypeScript implementation uses `bpmn-moddle`. We will use the `pybpmn` library mentioned in Step 4.
    - This affects `Definition.ts` and `DefaultAppDelegate.ts`.
- **Script Sandbox Strategy**
    - The TS engine uses Node's `vm` or `child_process`. We need to decide on a safe way to execute user-provided scripts in Python.
    - We will use `RestrictedPython`
- **FEEL Engine for DMN**
    - We will use `bkflow-feel`.
- **Event Emitter Implementation**
    - `eventemitter3` is central to the TS implementation. We will use `pymitter` asynchronous event emitter.

## Special Cases Flagged

### Cyclical Dependencies
- **Identification:** `Node` <-> `Behaviour`, `Token` <-> `Execution`, `Item` <-> `Token`.
- **Mitigation:** Group these into "Coupled Units" (Steps 3, 4, and 5) and translate them as a single conceptual block. Use Python's type hinting with strings (e.g., `'Execution'`) to handle forward references.

### Generated or Vendor Code
- **Identification:** `src/elements/js-bpmn-moddle.ts` appears to be a helper for `bpmn-moddle`.
- **Strategy:** This is not a direct dependency of the core engine and can be safely ignored.

### Language-Specific Constructs
- **EventEmitter:** Used in `BPMNServer` and `Listener`. Python's `pymitter` is a direct equivalent.
- **Node `vm` / `child_process`:** Used for scripts. Use `RestrictedPython` for sandboxing.
- **Barrel Files (`index.ts`):** These should be replaced with Python `__init__.py` files to manage exports, but avoid creating the same circularity issues seen in the TS implementation.

## Verification
Each step must include:
1. **Static Analysis:** `mypy` for type correctness.
2. **Unit Testing:** `pytest` for functional correctness of the translated unit.
3. **Mocking:** Use `unittest.mock` to satisfy dependencies on not-yet-translated modules.

## Dependency Graph & Translation Order

The following order is determined by starting from leaf modules (no internal dependencies) and moving upward toward orchestration and entry points.

### Step 1
- **Files or modules:** 
    - `src/interfaces/User.ts`
    - `src/interfaces/Enums.ts`
    - `src/interfaces/DataObjects.ts`
    - `src/interfaces/common.ts`
    - `src/interfaces/elements.ts`
    - `src/interfaces/engine.ts`
    - `src/interfaces/datastore.ts`
    - `src/interfaces/server.ts`
- **Reason for order:** These define the data structures and contracts used throughout the entire system. They are almost entirely leaf modules (though some have cross-references, they are mostly type-only).
- **Dependencies that must already be translated:** None (mostly external or type-only).
- **Expected verification method:** Static type checking (mypy) of the generated Python classes/interfaces.
- **Expected Python artifact:** `bpmn_python/interfaces/*.py` (using `dataclasses`, `Enum`, and `Protocol` or abstract base classes).
- **Other instructions:** 
    - `Enums.ts` has a type import for `Transaction`. This should be handled by using type strings or moving the enum to a more foundational module if needed.
    - Python `Protocols` should be used for interfaces.

### Step 2
- **Files or modules:** 
    - `src/common/timer.ts`
    - `src/common/Logger.ts`
    - `src/common/DefaultConfiguration.ts`
    - `src/engine/DataHandler.ts`
    - `src/datastore/QueryTranslator.ts`
    - `src/server/ServerComponent.ts`
    - `src/elements/js-bpmn-moddle.ts`
- **Reason for order:** Generic utilities, foundational base classes, and simple handlers that do not depend on the core execution engine but are used by it.
- **Dependencies that must already be translated:** Step 1 (Interfaces).
- **Expected verification method:** Unit tests for logging, timer logic, and query translation.
- **Expected Python artifact:** `bpmn_python/common/*.py`, `bpmn_python/engine/data_handler.py`, foundational base classes.
- **Other instructions:** 
    - `DefaultConfiguration` depends on `ModelsDatastore` and `AppDelegate`. Reference their interfaces instead (`IModelsDatastore` and `IAppDelegate`).
    - `js-bpmn-moddle.ts` can be safely ignored.

### Step 3
- **Files or modules:** 
    - `src/engine/Item.ts`
    - `src/engine/Token.ts`
    - `src/engine/Loop.ts`
    - `src/engine/Model.ts`
- **Reason for order:** These represent the runtime state of a process. They are tightly coupled (e.g., `Token` references `Item`, `Item` references `Token`). Grouping them allows resolving their mutual dependencies in one pass.
- **Dependencies that must already be translated:** Step 1 (Interfaces), Step 2 (Utilities).
- **Expected verification method:** Unit tests for state management and state transitions within these objects.
- **Expected Python artifact:** `bpmn_python/engine/{item, token, loop, model}.py`.
- **Other isntructions:**
    - `Item` should reference `IToken` instead of `Token`.
    - `Token` should reference `IItem` instead of `Item`.
    - `Token` should reference `IExecution` instead of `Execution`.

### Step 4
- **Files or modules:** 
    - `src/elements/Element.ts`
    - `src/elements/Node.ts`
    - `src/elements/Flow.ts`
    - `src/elements/behaviours/*`
    - `src/elements/NodeLoader.ts`
    - `src/elements/Tasks.ts`
    - `src/elements/Gateway.ts`
    - `src/elements/Events.ts`
    - `src/elements/Transaction.ts`
    - `src/elements/Process.ts`
    - `src/elements/Definition.ts`
    - `src/elements/js-bpmn-moddle.ts`
- **Reason for order:** Elements and their behaviours are the heart of the BPMN logic. They depend heavily on each other and the Core Engine Data Objects. Grouping them is necessary because of the inheritance and composition patterns used.
- **Dependencies that must already be translated:** Step 1, 2, and 3.
- **Expected verification method:** Verification of BPMN element loading and basic behaviour logic (e.g., timer behaviour parsing).
- **Expected Python artifact:** `bpmn_python/elements/*.py`, `bpmn_python/elements/behaviours/*.py`.
- **Other instructions:** 
    - Refer to "dependency-migration.md" for dependency migration instructions.

### Step 5
- **Files or modules:** 
    - `src/engine/Execution.ts`
    - `src/engine/ScriptHandler.ts`
    - `src/engine/DefaultAppDelegate.ts`
- **Reason for order:** This is the primary orchestration layer that coordinates Tokens, Items, and Elements. It depends on almost everything below it.
- **Dependencies that must already be translated:** Step 1 through 4.
- **Expected verification method:** Full execution of a simple BPMN process (mocking datastore).
- **Expected Python artifact:** `bpmn_python/engine/execution.py`, etc.
- **Other instructions:** 
    - Only stub`ScriptHandler`. The actual implementation will be added in a later step.

### Step 6
- **Files or modules:** 
    - `src/datastore/MongoDB.ts`
    - `src/datastore/DataStore.ts`
    - `src/datastore/ModelsData.ts`
    - `src/datastore/ModelsDatastore.ts`
    - `src/datastore/ModelsDatastoreDB.ts`
    - `src/datastore/InstanceLocker.ts`
    - `src/datastore/Aggregate.ts`
- **Reason for order:** Handles saving and loading of process state. Depends on `Execution` and `Interfaces`.
- **Dependencies that must already be translated:** Step 1 through 5.
- **Expected verification method:** Integration tests with MongoDB (using `pymongo`).
- **Expected Python artifact:** `bpmn_python/datastore/*.py`.
- **Other instructions:** 
    - Refer to "dependency-migration.md" for dependency migration instructions.

### Step 7
- **Files or modules:** 
    - `src/dmn/DMNParser.ts`
    - `src/dmn/DMNEngine.ts`
- **Reason for order:** DMN is a separate but integrated component. It depends on the `BusinessRuleTask` in Elements but can be tested independently.
- **Dependencies that must already be translated:** Step 1, 2, and 4.
- **Expected verification method:** DMN table evaluation tests.
- **Expected Python artifact:** `bpmn_python/dmn/*.py`.
- **Other instructions:** 
    - Refer to "dependency-migration.md" for dependency migration instructions.

### Step 8
- **Files or modules:** 
    - `src/server/BPMNServer.ts`
    - `src/server/Engine.ts`
    - `src/server/CacheManager.ts`
    - `src/server/Cron.ts`
    - `src/server/Listener.ts`
    - `src/API/API.ts`
    - `src/API/AccessManager.ts`
    - `src/API/SecureUser.ts`
- **Reason for order:** These are the top-level entry points and runtime wiring. They coordinate the server lifecycle and public API.
- **Dependencies that must already be translated:** All previous steps.
- **Expected verification method:** End-to-end API tests and server lifecycle tests.
- **Expected Python artifact:** `bpmn_python/server/*.py`, `bpmn_python/api/*.py`.
- **Other instructions:** 
    - Refer to "dependency-migration.md" for dependency migration instructions.
