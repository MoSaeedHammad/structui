---
sidebar_position: 3
---

# API Reference

## Mapping Custom Parsers

StructUI is built to be extensible. By implementing a custom parser mapping, you can generate interfaces for your proprietary data formats.

### The Parser Interface

To create a custom parser, you must implement the base `Parser` class and define how your format translates into the StructUI AST.

```python
from structui.parser import BaseParser
from structui.ast import Node, StringNode, IntegerNode

class MyCustomParser(BaseParser):
    def parse(self, raw_data: bytes) -> Node:
        # Implementation details here
        pass
```

### Steps to Implement a Custom Parser:
1. **Define the Mapping Rules**: Determine how your raw data structures correspond to the available AST nodes (`StringNode`, `IntegerNode`, `ListNode`, etc.).
2. **Implement the Parsing Logic**: Traverse your raw data and instantiate the corresponding AST nodes.
3. **Attach Node Metadata**: Ensure that each node captures relevant metadata, such as its exact position in the source file, to facilitate error reporting and source updates.
4. **Register the Parser**: Register your custom parser with the core StructUI framework so it can be invoked appropriately when a supported file type is loaded.

### Example: JSON Parser Mapping
When parsing JSON, a JSON object `{}` maps to a StructUI `DictionaryNode`, a JSON array `[]` maps to a `ListNode`, and leaf values map to their respective primitive nodes. The validation rules defined in a corresponding JSON Schema can be attached directly to these nodes during the parsing phase.
