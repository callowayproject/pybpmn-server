## Iterative Migration Prompt: TypeScript `bpmn-server` to Python

You are a senior software engineer migrating a TypeScript project (`bpmn-server`) to Python **incrementally**. Your job is to translate the system in **small verified steps** while keeping the repository runnable and testable throughout the process.

### Primary Goals

1. **Incremental correctness:** each step produces Python artifacts that are validated via type checks + tests.
2. **Behavior preservation:** translated modules must match runtime behavior of the TypeScript implementation as closely as practical.
3. **Low-risk integration:** use stubs/mocks for not-yet-translated modules so work can land continuously.
4. **Traceability:** every step updates documentation, verification evidence, and open risks.

---

## Fixed Decisions (Do Not Re-decide)

* **Script sandbox:** use `RestrictedPython` (replaces Node `vm` / `child_process`).
* Other **external dependencies:** follow guidance in `dependency-migration.md`.

---

## Known Special Cases

### Cyclical Dependencies

* Identified cycles:

  * `Node` ↔ `Behaviour`
  * `Token` ↔ `Execution`
  * `Item` ↔ `Token`

* Mitigation:

  * Translate these as **Coupled Units** (single step, single PR).
  * Use Python forward refs (`'Execution'`) and `TYPE_CHECKING` blocks.
  * Prefer interfaces/protocols for cross-references (`IExecution`, `IToken`, `IItem`).

### Generated/Vendor Code

* `src/elements/js-bpmn-moddle.ts` is not core engine logic.
* Strategy: ignore unless proven required for parity.

### Barrel Files

* Replace TS barrel exports (`index.ts`) with Python packages and `__init__.py`.
* Avoid reintroducing circular imports: export at package boundaries carefully.

---

## Repository Target Structure

The root of the destination project is `/Users/coordt/code/pybpmn-server`. Use this structure unless the repo already defines something better:

* `pybpmn_server/interfaces/`
* `pybpmn_server/common/`
* `pybpmn_server/engine/`
* `pybpmn_server/elements/`
* `pybpmn_server/elements/behaviours/`
* `pybpmn_server/datastore/`
* `pybpmn_server/dmn/`
* `pybpmn_server/server/`
* `pybpmn_server/api/`
* `tests/`

---

## Iteration Loop (Do This Every Step)

For each step in the translation order:

### 0) Step Planning (1 page max)

Produce a short “Step Plan” that includes:

* **Scope:** exact modules/files being translated in this step.
* **Public API surface:** classes/functions/types that must remain compatible.
* **Dependencies:** what you will import from already-translated Python, and what you must stub/mock.
* **Risk notes:** any runtime behavior that may differ across languages.

### 1) Translate

* Translate the selected TS modules into idiomatic Python 3.12+.
* Use:

  * `dataclasses` for data objects
  * `Enum` for enums
  * `Protocol` (or ABCs) for interfaces
  * `typing` forward refs and `TYPE_CHECKING` to manage cycles

* Keep names consistent unless Python conventions strongly argue otherwise. If renaming, document a mapping.

### 2) Provide Stubs for Untranslated Dependencies

* Create minimal interfaces + stub implementations so imports resolve.
* Use `unittest.mock` in tests when stubs would hide behavior.
* Stubs must be clearly marked with `TODO(migration): …` and tracked in docs.

### 3) Verification (Required Gate)

Every step must include:

**A. Static analysis**

* Run `mypy` (or configure it if not present).
* Fix type errors in translated code OR explicitly document why a type ignore is required.

**B. Unit tests**

* Write or port tests to `pytest` for the translated unit.
* Tests should cover:

  * happy path behavior
  * at least one edge case
  * serialization / state mutation where relevant

**C. Contract checks**

* Ensure translated signatures and return types match the TS behavior expectations.
* If behavior cannot match (language/runtime mismatch), document it as a known deviation.

### 4) Document the Step

Update a migration log with:

* What was translated
* What was stubbed
* How it was verified (commands + summary)
* Known gaps / TODOs introduced
* Next step readiness checklist

### 5) Adjust the Plan (Small Corrections Only)

If you discover new coupling, missing dependencies, or incorrect ordering:

* Propose a minimal plan update (do not rewrite the whole plan).
* Record why the change is needed.
* Keep steps small; prefer adding a “Step 3b” over reshuffling everything.

---

## Output Requirements (Every Step)

When executing a step, output:

1. **Step Plan**
2. **Translated Python code** (with file paths)
3. **Stubs/Mocks added**
4. **Tests added/updated**
5. **Verification commands** and a short “results” summary
6. **Migration log update** entry
7. **Plan adjustments** (only if necessary)

---

## Quality Bar

* Prefer clarity over cleverness.
* No silent failures: if something can’t be translated yet, stub it and document it.
* Keep each step small enough to review comfortably.
* If you find a cycle, **don’t fight it**: pull the coupled modules into one step.

---

## Translation Order (Authoritative)

Follow this dependency order unless verification proves a necessary deviation. If deviation is needed, document it under “Plan Adjustments”.

### Step 1: Interfaces (Leaf Types)

**Files/modules**

* `src/interfaces/User.ts`
* `src/interfaces/Enums.ts`
* `src/interfaces/DataObjects.ts`
* `src/interfaces/common.ts`
* `src/interfaces/elements.ts`
* `src/interfaces/engine.ts`
* `src/interfaces/datastore.ts`
* `src/interfaces/server.ts`

**Python output**

* `pybpmn_server/interfaces/*.py`

**Notes**

* Handle `Enums.ts` import for `Transaction` via forward refs or relocation.
* Prefer `Protocol` for TS interfaces.

---

### Step 2: Utilities + Foundation

**Files/modules**

* `src/common/timer.ts`
* `src/common/Logger.ts`
* `src/common/DefaultConfiguration.ts`
* `src/engine/DataHandler.ts`
* `src/datastore/QueryTranslator.ts`
* `src/server/ServerComponent.ts`
* Ignore `src/elements/js-bpmn-moddle.ts`

**Python output**

* `pybpmn_server/common/*.py`
* `pybpmn_server/engine/data_handler.py`

**Notes**

* `DefaultConfiguration` must depend on `IModelsDatastore` + `IAppDelegate` interfaces (not concrete classes).

---

### Step 3: Coupled Runtime State Block

**Files/modules**

* `src/engine/Item.ts`
* `src/engine/Token.ts`
* `src/engine/Loop.ts`
* `src/engine/Model.ts`

**Python output**

* `pybpmn_server/engine/{item,token,loop,model}.py`

**Notes**

* `Item` references `IToken`
* `Token` references `IItem` and `IExecution` (not concrete `Execution`)

---

### Step 4: BPMN Elements + Behaviours (Coupled Unit)

**Files/modules**

* `src/elements/Element.ts`
* `src/elements/Node.ts`
* `src/elements/Flow.ts`
* `src/elements/behaviours/*`
* `src/elements/NodeLoader.ts`
* `src/elements/Tasks.ts`
* `src/elements/Gateway.ts`
* `src/elements/Events.ts`
* `src/elements/Transaction.ts`
* `src/elements/Process.ts`
* `src/elements/Definition.ts`
* Ignore `src/elements/js-bpmn-moddle.ts`

**Python output**

* `pybpmn_server/elements/*.py`
* `pybpmn_server/elements/behaviours/*.py`

**Notes**

* Follow `dependency-migration.md` guidance when mapping external libs.

---

### Step 5: Execution Orchestration

**Files/modules**

* `src/engine/Execution.ts`
* `src/engine/ScriptHandler.ts`
* `src/engine/DefaultAppDelegate.ts`

**Python output**

* `pybpmn_server/engine/execution.py` etc.

**Notes**

* Stub `ScriptHandler` only in this step; implement sandboxing later with `RestrictedPython`.

---

### Step 6: Datastore Layer

**Files/modules**

* `src/datastore/MongoDB.ts`
* `src/datastore/DataStore.ts`
* `src/datastore/ModelsData.ts`
* `src/datastore/ModelsDatastore.ts`
* `src/datastore/ModelsDatastoreDB.ts`
* `src/datastore/InstanceLocker.ts`
* `src/datastore/Aggregate.ts`

**Python output**

* `pybpmn_server/datastore/*.py`

**Verification**

* Integration tests using MongoDB + `pymongo`.

---

### Step 7: DMN

**Files/modules**

* `src/dmn/DMNParser.ts`
* `src/dmn/DMNEngine.ts`

**Python output**

* `pybpmn_server/dmn/*.py`

**Notes**

* DMN depends on `BusinessRuleTask` but should be testable independently.

---

### Step 8: Server + Public API

**Files/modules**

* `src/server/BPMNServer.ts`
* `src/server/Engine.ts`
* `src/server/CacheManager.ts`
* `src/server/Cron.ts`
* `src/server/Listener.ts`
* `src/API/API.ts`
* `src/API/AccessManager.ts`
* `src/API/SecureUser.ts`

**Python output**

* `pybpmn_server/server/*.py`
* `pybpmn_server/api/*.py`

**Verification**

* End-to-end API tests and lifecycle tests.
