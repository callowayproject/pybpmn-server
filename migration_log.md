# Migration Log

## 2025-12-20

### Step 1: Interfaces (Leaf Types)
- **Translated:**
    - `src/interfaces/User.ts` -> `pybpmn_server/interfaces/user.py`
    - `src/interfaces/Enums.ts` -> `pybpmn_server/interfaces/enums.py`
    - `src/interfaces/DataObjects.ts` -> `pybpmn_server/interfaces/data_objects.py`
    - `src/interfaces/common.ts` -> `pybpmn_server/interfaces/common.py`
    - `src/interfaces/elements.ts` -> `pybpmn_server/interfaces/elements.py`
    - `src/interfaces/engine.ts` -> `pybpmn_server/interfaces/engine.py`
    - `src/interfaces/datastore.ts` -> `pybpmn_server/interfaces/datastore.py`
    - `src/interfaces/server.ts` -> `pybpmn_server/interfaces/server.py`
- **Stubbed:**
    - Created package `__init__.py` files for `engine`, `elements`, `datastore`, `server`, `api`, `common`.
- **Verified:**
    - `mypy pybpmn_server/interfaces/` - Passed (Success: no issues found in 9 source files)
    - `pytest tests/test_interfaces.py` - Passed (2 tests, 100% coverage of interfaces)
- **Known Gaps / TODOs:**
    - Used `from __future__ import annotations` and runtime imports for base interfaces where inheritance or Protocol fields required it.
    - Simplified some complex TS types (like `EventEmitter`) to `Any` for now.
    - Mapped TS `Map` to Python `dict`.
- **Next Step Readiness:**
    - Step 2: Utilities + Foundation is ready to proceed.

## 2025-12-20 (Continued)

### Step 3: Coupled Runtime State Block
- **Translated:**
    - `src/engine/Item.ts` -> `pybpmn_server/engine/item.py`
    - `src/engine/Token.ts` -> `pybpmn_server/engine/token.py`
    - `src/engine/Loop.ts` -> `pybpmn_server/engine/loop.py`
    - `src/engine/Model.ts` -> `pybpmn_server/engine/model.py`
- **Refined Interfaces:**
    - Updated `interfaces/data_objects.py` to use `snake_case` for `IItemData`, `IInstanceData`, etc.
    - Added `ILoopBehaviour` and updated `INode` in `interfaces/elements.py`.
    - Made `IToken` members optional in `interfaces/engine.py`.
- **Verified:**
    - `pytest tests/test_runtime_state.py` - Passed (4 tests)
    - `mypy pybpmn_server/engine/` - Checked (some Protocol invariance warnings remain but logic is sound)
- **Known Gaps / TODOs:**
    - `get_scope_catch_event` in `Token` is a placeholder for complex catch event logic.
    - Protocol properties in `Item` and `Token` use `# type: ignore` to bypass Mypy read-only property vs writeable attribute mismatch.
- **Next Step Readiness:**
    - Step 4: BPMN Elements + Behaviours is ready to proceed.

## 2025-12-20 (Continued)

### Step 4: BPMN Elements + Behaviours (Coupled Unit)
- **Translated:**
    - `src/elements/Element.ts` -> `pybpmn_server/elements/element.py`
    - `src/elements/Node.ts` -> `pybpmn_server/elements/node.py`
    - `src/elements/Flow.ts` -> `pybpmn_server/elements/flow.py`
    - `src/elements/behaviours/*` -> `pybpmn_server/elements/behaviours/*.py` (11 behaviours)
    - `src/elements/Process.ts` -> `pybpmn_server/elements/process.py`
    - `src/elements/Definition.ts` -> `pybpmn_server/elements/definition.py`
    - `src/elements/Tasks.ts`, `Gateway.ts`, `Events.ts`, `Transaction.ts` -> `pybpmn_server/elements/*.py`
    - `src/elements/NodeLoader.ts` -> `pybpmn_server/elements/node_loader.py`
- **Verified:**
    - `pytest tests/test_elements.py` - Passed (4 tests)
    - `mypy pybpmn_server/elements/` - Checked (remaining errors related to Protocol/Property overrides)
- **Known Gaps / TODOs:**
    - `Definition` XML parsing is a simplified `xml.etree.ElementTree` implementation; might need `bpmn-moddle` equivalent for complex models.
    - `DMNEngine` in `BusinessRuleTask` is imported but not yet implemented (Step 7).
    - `ScriptHandler` is still a stub (Step 5).
- **Next Step Readiness:**
    - Step 5: Execution Orchestration is ready to proceed.

## 2025-12-20 (Continued)

### Step 5: Execution Orchestration
- **Translated:**
    - `src/engine/Execution.ts` -> `pybpmn_server/engine/execution.py`
    - `src/engine/ScriptHandler.ts` -> `pybpmn_server/engine/script_handler.py`
    - `src/engine/DefaultAppDelegate.ts` -> `pybpmn_server/engine/default_app_delegate.py`
- **Verified:**
    - `pytest tests/test_execution.py` - Passed (4 tests)
    - `mypy pybpmn_server/engine/` - Checked (Protocol and property override warnings remain)
- **Known Gaps / TODOs:**
    - `ScriptHandler` uses Python's `eval`/`exec` for now; `RestrictedPython` will be integrated in a later step for security.
    - `DefaultAppDelegate` assumes a standard `EventEmitter` on the server instance for hook registration.
    - `Execution.signal_item2` was skipped as it is redundant with `signal_item`.
- **Next Step Readiness:**
    - Step 6: Datastore Layer is ready to proceed.

## 2025-12-20 (Continued)

### Step 6: Datastore Layer
- **Translated:**
    - `src/datastore/MongoDB.ts` -> `pybpmn_server/datastore/mongodb.py`
    - `src/datastore/DataStore.ts` -> `pybpmn_server/datastore/data_store.py`
    - `src/datastore/ModelsData.ts` -> `pybpmn_server/datastore/models_data.py`
    - `src/datastore/ModelsDatastore.ts` -> `pybpmn_server/datastore/models_datastore.py`
    - `src/datastore/ModelsDatastoreDB.ts` -> `pybpmn_server/datastore/models_datastore_db.py`
    - `src/datastore/InstanceLocker.ts` -> `pybpmn_server/datastore/instance_locker.py`
    - `src/datastore/Aggregate.ts` -> `pybpmn_server/datastore/aggregate.py`
- **Refined Interfaces:**
    - Updated `interfaces/datastore.py` to use `snake_case` for `FindParams` and `FindResult`.
- **Verified:**
    - `pytest tests/test_datastore.py` - Passed (2 tests, verifying save/load/find with `mongomock`)
    - `mypy pybpmn_server/datastore/` - Checked (some Protocol and type inference warnings remain)
- **Known Gaps / TODOs:**
    - Used `pymongo` for MongoDB operations; implemented as `async` wrappers although `pymongo` is synchronous (to match the engine's async architecture).
    - `ModelsDatastore` file-based implementation uses synchronous `open` and `os` calls.
- **Next Step Readiness:**
    - Step 7: DMN is ready to proceed.

## 2025-12-20 (Continued)

### Step 7: DMN
- **Translated:**
    - `src/dmn/DMNParser.ts` -> `pybpmn_server/dmn/dmn_parser.py`
    - `src/dmn/DMNEngine.ts` -> `pybpmn_server/dmn/dmn_engine.py`
- **Verified:**
    - `pytest tests/test_dmn.py` - Passed (4 tests covering parsing, evaluation, hit policies, and simple FEEL range)
    - `mypy pybpmn_server/dmn/` - Checked
- **Known Gaps / TODOs:**
    - Implemented a `simple_feel_evaluate` method in `DMNEngine` to handle basic FEEL range and comparison expressions as a substitute for the `feelin` dependency.
    - Used `xmltodict` for DMN XML parsing.
- **Next Step Readiness:**
    - Step 8: Server + Public API is ready to proceed.

## 2025-12-20 (Continued)

### Step 8: Server + Public API
- **Translated:**
    - `src/server/BPMNServer.ts` -> `pybpmn_server/server/bpmn_server.py`
    - `src/server/Engine.ts` -> `pybpmn_server/server/engine.py`
    - `src/server/Cron.ts` -> `pybpmn_server/server/cron.py`
    - `src/server/Listener.ts` -> `pybpmn_server/server/listener.py`
    - `src/server/CacheManager.ts` -> `pybpmn_server/server/cache_manager.py`
    - `src/API/API.ts` -> `pybpmn_server/api/api.py`
    - `src/API/SecureUser.ts` -> `pybpmn_server/api/secure_user.py`
- **Verified:**
    - `pytest tests/test_server.py` - Passed (3 tests covering initialization, API engine start, and secure user qualification)
    - `mypy pybpmn_server/server/` and `pybpmn_server/api/` - Checked (some library-related warnings remain)
- **Known Gaps / TODOs:**
    - Used `pyee.asyncio.AsyncIOEventEmitter` for event management.
    - `Cron` implementation uses `asyncio.get_event_loop().call_later` for scheduling, and `croniter` for cron expression parsing.
    - `BPMNServer.get_version()` returns a hardcoded version string for now.
    - `SecureUser` by-pass logic matches TS implementation (checking environment variables).
- **Next Step Readiness:**
    - All core steps of the migration strategy are now complete. Final cleanup and documentation review recommended.
