# Step 2 Plan: Utilities + Foundation

## Scope
Translate core utility and foundational classes that have minimal dependencies:
- `src/common/timer.ts` -> `pybpmn_server/common/timer.py`
- `src/common/Logger.ts` -> `pybpmn_server/common/logger.py`
- `src/common/DefaultConfiguration.ts` -> `pybpmn_server/common/default_configuration.py`
- `src/engine/DataHandler.ts` -> `pybpmn_server/engine/data_handler.py`
- `src/datastore/QueryTranslator.ts` -> `pybpmn_server/datastore/query_translator.py`
- `src/server/ServerComponent.ts` -> `pybpmn_server/server/server_component.py`

## Public API Surface
- `dateDiff(date_str: str) -> str`
- `Logger` class (implements `ILogger`)
- `Configuration` class (implements `IConfiguration`)
- `DataHandler` static methods: `appendData`, `getData`, `getAndCreateData`
- `QueryTranslator` class
- `ServerComponent` class

## Dependencies
- `pybpmn_server/interfaces/*.py` (Already translated)
- Stubs needed:
    - `IModelsDatastore` concrete implementation (`ModelsDatastore`)
    - `IAppDelegate` concrete implementation (`DefaultAppDelegate`)
    - `IDataStore` concrete implementation (`DataStore`)
    - `ICacheManager` concrete implementation (`NoCacheManager`)
    - `IScriptHandler` concrete implementation (`ScriptHandler`)
    - `Cron` and `CacheManager` (for `ServerComponent`)

## Risk Notes
- `Logger` uses Node's `fs.appendFileSync` and `fs.writeSync`. Python's `open` and `write` will be used.
- `DefaultConfiguration` uses `__dirname`. Python's `__file__` or `pathlib` will be used.
- `DataHandler` and `QueryTranslator` handle object/dictionary manipulation which is similar in TS and Python, but careful with `None` vs `undefined`.
- `ServerComponent` uses many getters; Python's `@property` will be used.
