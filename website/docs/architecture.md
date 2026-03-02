---
sidebar_position: 2
---

# Architecture

## Separation of Concerns

The foundational principle of StructUI is the strict boundary maintained between **UI Representation** and **Parser Logic**. This separation ensures that the system is scalable, easily testable, and capable of supporting numerous data formats without bloating the UI layer.

### The UI Layer
The UI layer is responsible purely for rendering the Abstract Syntax Tree (AST) and capturing user inputs. It does not know whether the source data came from a JSON file, a YAML configuration, or a proprietary binary format. It relies entirely on the Node metadata (type, boundaries, validation rules) provided by the parser.

### The Parser Logic
Parsers are responsible for reading the raw input and constructing the AST. A parser implements the specific rules required to traverse the source format and emit standard StructUI Nodes. Each node contains references back to its position in the original source, allowing for accurate updates and error reporting.

### The Abstract Syntax Tree (AST)
The AST acts as the universal contract between the parsers and the UI. It standardizes elements such as:
- **Primitives**: Strings, Numbers, Booleans.
- **Collections**: Lists, Dictionaries.
- **Validation Rules**: Constraints (e.g., min/max length, regex patterns) that the UI must enforce.
