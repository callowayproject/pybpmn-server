# Step 6 Plan: Datastore Layer

## Scope
Translate the datastore layer which handles persistence for process instances and models:
- `src/datastore/DataStore.ts` -> `pybpmn_server/datastore/data_store.py`
- `src/datastore/ModelsData.ts` -> `pybpmn_server/datastore/models_data.py`
- `src/datastore/ModelsDatastore.ts` -> `pybpmn_server/datastore/models_datastore.py`
- `src/datastore/ModelsDatastoreDB.ts` -> `pybpmn_server/datastore/models_datastore_db.py`
- `src/datastore/MongoDB.ts` -> `pybpmn_server/datastore/mongodb.py`
- `src/datastore/InstanceLocker.ts` -> `pybpmn_server/datastore/instance_locker.py`
- `src/datastore/Aggregate.ts` -> `pybpmn_server/datastore/aggregate.py`

## Public API Surface
- `DataStore` class (implements `IDataStore`)
- `ModelsDatastore` class (implements `IModelsDatastore`)
- `MongoDB` class
- `InstanceLocker` class
- `Aggregate` class

## Dependencies
- `pybpmn_server/interfaces/datastore.py`
- `pybpmn_server/common/` (Logger, Configuration)
- `pybpmn_server/engine/execution.py` (for Instance restoration)
- `pymongo` for MongoDB implementation

## Risk Notes
- MongoDB operations in TS use `mongodb` driver. Python will use `pymongo` (blocking) or `motor` (async). Strategy says "Integration tests using MongoDB + pymongo". However, the engine is `async`. We should use `motor` if we want to stay fully async, or wrap `pymongo` calls if they are called in async contexts.
- The `QueryTranslator` from Step 2 will be used for filtering.
- `InstanceLocker` uses MongoDB for distributed locking.
