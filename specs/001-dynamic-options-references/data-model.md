# Data Model: Dynamic Options References

## Entities

### Option Reference Path
- **Type**: `String`
- **Description**: A dot-notation path indicating where to find option values in the configuration tree.
- **Rules**:
  - Supports `[*]` to indicate iteration over all elements in an array.
  - E.g., `connections[*].interfaces[*].itf_name`
- **Validation**:
  - Nulls and empty strings found at the target are ignored/filtered out.
  - Resulting values must be deduplicated.

### Dynamic Options Resolver
- **Description**: A stateless utility function embedded in the state management layer.
- **Input**:
  - `data_tree`: The root data tree or sub-tree (dict/list) to evaluate against.
  - `path`: The Option Reference Path string.
- **Output**: `List[str]` containing the deduplicated, non-null values resolved from the path.
- **Behavior**:
  - Splits path by `.` (dot).
  - Iteratively traverses dictionaries for key matches.
  - When encountering `[*]`, branches the evaluation to all elements in the current array node and aggregates the results.
