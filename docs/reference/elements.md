# Elements

## How elements are created

- Engine receives the start command with the BPMN source
- Engine creates an Execution Context with the provided BPMN source
- Execution Context creates a Definition element with the BPMN source
- Engine calls Execution Context's execute method
- Execution Context's execute method calls the Definition element's load method
- Definition element parses the BPMN source and creates Process element(s)
- The Definition converts all the BPMN elements into internal Node representations
- The Definition passes Nodes to the Process element for further processing
