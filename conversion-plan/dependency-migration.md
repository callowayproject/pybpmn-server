# Dependency migration plan

## mongodb
- Purpose: Official MongoDB driver for Node.js
- Usage status: active
- Key usage:
  - `src/datastore/DataStore.ts` — `import { MongoClient } from 'mongodb'`, database connection and operations
  - `src/datastore/MongoDB.ts` — `import { MongoClient } from 'mongodb'`, database connection management
  - `src/datastore/Aggregate.ts` — `import { MongoClient } from 'mongodb'`, aggregation operations
- Python migration risk: low
- Suggested replacement: pymongo

## xml2js
- Purpose: XML to JavaScript object converter
- Usage status: active
- Key usage:
  - `src/dmn/DMNParser.ts` — `import xml2js from 'xml2js'`, parsing DMN XML files
- Python migration risk: low
- Suggested replacement: xmltodict

## cron-parser
- Purpose: Node.js library for parsing and manipulating crontab instructions
- Usage status: active
- Key usage:
  - `src/server/Cron.ts` — `import parser from 'cron-parser'`, calculating next execution times for cron jobs
- Python migration risk: low
- Suggested replacement: croniter

## iso8601-duration
- Purpose: ISO 8601 duration parsing and serialization
- Usage status: active
- Key usage:
  - `src/server/Cron.ts` — `import { parse, end, add } from 'iso8601-duration'`, handling ISO 8601 durations in cron tasks
  - `src/elements/behaviours/Behaviour.ts` — `import { parse, end, add } from 'iso8601-duration'`, timer behaviour implementation
  - `src/elements/behaviours/BehaviourLoader.ts` — `import { parse, end, add } from 'iso8601-duration'`, loading timer behaviours
- Python migration risk: low
- Suggested replacement: python-dateutil

## dayjs
- Purpose: Minimalist JavaScript library for parsing, validating, manipulating, and displaying dates and times
- Usage status: active
- Key usage:
  - `src/elements/behaviours/Timer.ts` — `import dayjs from 'dayjs'`, date manipulation for timers
- Python migration risk: low — Python's `datetime` module is robust; `pendulum` or `arrow` are good alternatives.
- Suggested replacement: pendulum

## eventemitter3
- Purpose: High-performance EventEmitter for Node.js and the browser
- Usage status: active
- Key usage:
  - `src/server/BPMNServer.ts` — `import { EventEmitter } from 'eventemitter3'`, server-wide event handling
  - `src/interfaces/server.ts` — `import { EventEmitter } from 'eventemitter3'`, interface definition for event emitters
- Python migration risk: medium
- Suggested replacement: pymitter

## feelin
- Purpose: FEEL (Friendly Enough Expression Language) parser and interpreter
- Usage status: active
- Key usage:
  - `src/dmn/DMNParser.ts` — `import { FEEL } from 'feelin'`, evaluating FEEL expressions in DMN
  - `src/dmn/DMNEngine.ts` — `import { FEEL } from 'feelin'`, FEEL expression evaluation
- Python migration risk: medium
- Suggested replacement: bkflow-feel

## bpmn-moddle
- Purpose: Read and write BPMN 2.0 XML files from Node.js
- Usage status: active
- Key usage:
  - `src/elements/Definition.ts` — `import BpmnModdle from 'bpmn-moddle'`, loading and parsing BPMN definitions
- Python migration risk: medium
- Suggested replacement: pybpmn-parser located at /Users/coordt/code/pybpmn-parser

## @lukeed/uuid
- Purpose: Tiny (230B) and fast UUID (v4) generator
- Usage status: active
- Key usage:
  - `src/engine/Execution.ts` — `import { v4 as uuidv4 } from '@lukeed/uuid'`, generating unique identifiers for execution instances
- Python migration risk: low — Use Python's built-in `uuid` module.
- Suggested replacement: uuid

## typescript
- Purpose: TypeScript compiler and language services
- Usage status: active
- Key usage:
  - `src/scripts/tsToApi.ts` — `import * as ts from "typescript"`, script for generating API from TypeScript files
- Python migration risk: high — Not applicable to Python runtime. Python uses type hints.
- Suggested replacement: 

## markdown-toc
- Purpose: Generate a markdown TOC (table of contents) for a markdown file
- Usage status: active
- Key usage:
  - `src/scripts/generate-toc.js` — `const Toc = require('markdown-toc')`, generating TOC for documentation
- Python migration risk: low — Many Python tools (e.g., `markdown-toc`) exist for this.
- Suggested replacement: 
