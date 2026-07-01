# Research: Dynamic Options References

## Wildcard Path Evaluation
- **Decision**: Implement a recursive path evaluation function `evaluate_dynamic_path(data: Any, path: str) -> List[str]` in `state.py` that parses dot-notation strings and handles the `[*]` wildcard by iterating through array elements and recursively resolving the remainder of the path.
- **Rationale**: `state.py` manages `config_data` and is the natural place for state-querying utilities. A recursive approach gracefully handles nested structures and multiple wildcards.
- **Alternatives considered**: Using JSONPath libraries (like `jsonpath-ng`). Rejected because we only need basic `[*]` array support and exact property matching, and introducing a heavy dependency violates the lightweight nature of this project.

## UI Dropdown Updating Strategy
- **Decision**: Evaluate the dynamic options in `ui.py` during `draw_editor(path)` and assign the result to the `ui.select` options. No cross-component reactive triggers are needed beyond the existing `refresh_tree_and_editor()` behavior.
- **Rationale**: `NiceGUI` re-renders the `editor_scroll_area` completely when a node is selected. By pulling the latest evaluated options right before rendering the select input, the data will always be perfectly in sync with the `AppState`.
- **Alternatives considered**: Subscribing the dropdown's `options` list to state changes directly. Rejected because it complicates the `state.py` architecture with observer patterns that aren't currently present.
