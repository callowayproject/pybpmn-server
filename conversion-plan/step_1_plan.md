### Step 1 Plan: Interfaces (Leaf Types)

**Scope:**
Translate all TypeScript files in `src/interfaces/` to Python `Protocol` or `Enum` classes in `pybpmn_server/interfaces/`.

**Files:**
- `src/interfaces/User.ts` -> `pybpmn_server/interfaces/user.py`
- `src/interfaces/Enums.ts` -> `pybpmn_server/interfaces/enums.py`
- `src/interfaces/DataObjects.ts` -> `pybpmn_server/interfaces/data_objects.py`
- `src/interfaces/common.ts` -> `pybpmn_server/interfaces/common.py`
- `src/interfaces/elements.ts` -> `pybpmn_server/interfaces/elements.py`
- `src/interfaces/engine.ts` -> `pybpmn_server/interfaces/engine.py`
- `src/interfaces/datastore.ts` -> `pybpmn_server/interfaces/datastore.py`
- `src/interfaces/server.ts` -> `pybpmn_server/interfaces/server.py`

**Public API Surface:**
- Protocols for all `I*` interfaces.
- Enums for all TS enums.

**Dependencies:**
- None (these are leaf types).
- Circular dependency in `Enums.ts` (imports `Transaction` from `../elements`) will be handled via forward refs or by moving `Transaction` enum if it's purely a type/value enum.

**Risk Notes:**
- TypeScript structural typing vs Python `Protocol` (structural typing).
- `any` types in TS will be mapped to `Any` in Python.
- Circular references between interfaces will use `from __future__ import annotations` and string forward refs.

**Verification:**
- `mypy pybpmn_server/interfaces/`
- Minimal `pytest` to ensure enums and protocols can be imported.
