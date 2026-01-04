# Step 7 Plan: DMN

## Scope
Translate DMN parsing and evaluation logic:
- `src/dmn/DMNParser.ts` -> `pybpmn_server/dmn/dmn_parser.py`
- `src/dmn/DMNEngine.ts` -> `pybpmn_server/dmn/dmn_engine.py`

## Public API Surface
- `DMNParser` class:
    - `load_dmn_file(file_path: str) -> DecisionTable`
    - `convert_dmn_to_json(parsed_xml: dict) -> DecisionTable`
    - `document_rules(decision_table: DecisionTable) -> str`
- `DMNEngine` class:
    - `load(file_path: str) -> DMNEngine`
    - `evaluate(input_data: dict) -> any`

## Dependencies
- `xmltodict` for DMN XML parsing.
- `feelin` equivalent in Python (will look for `feel-python` or implement a basic evaluator for simple conditions).
- `pybpmn_server/interfaces/*.py`

## Risk Notes
- Parity of FEEL expressions. The TS implementation uses `feelin`. I will try to find a suitable Python replacement or stub it if only simple conditions are needed for now.
- `xmltodict` mapping vs `xml2js` mapping may differ slightly in how they handle attributes and children.
