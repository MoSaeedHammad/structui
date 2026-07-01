# Implementation Plan: Dynamic Options References

**Branch**: `001-dynamic-options-references` | **Date**: 2026-06-14 | **Spec**: [spec.md](file:///E:/Git_Repos/structui/specs/001-dynamic-options-references/spec.md)
**Input**: Feature specification from `/specs/001-dynamic-options-references/spec.md`

## Summary

This feature allows schema authors to define dynamic dropdown options using path strings with wildcards (e.g. `connections[*].interfaces[*].itf_name`). The UI will evaluate these strings at runtime against the current state of the document data, deduplicate them, and render them as dropdown options, ensuring data consistency and reducing manual duplication.

## Technical Context

**Language/Version**: Python 3
**Primary Dependencies**: NiceGUI
**Storage**: JSON/YAML/XML files
**Testing**: pytest
**Target Platform**: Desktop app / Web UI (via NiceGUI)
**Project Type**: library/desktop-app
**Performance Goals**: <200ms processing time for evaluating 1,000 array items
**Constraints**: <1 second UI updates when referenced data changes
**Scale/Scope**: Real-time evaluation of data paths in memory

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Separation of Concerns**: Passed. The UI layer (`ui.py`) will just call a state evaluation function and not parse files.
- **Strict Immutability**: Passed. The UI will only query the schema and data tree. It won't mutate the schema.
- **Domain Extensibility**: Passed. The path evaluator is generic and schema-driven.
- **Agent-Friendly CLI**: Passed. Path parsing functions will be exposed in `state.py`, accessible to any CLI.
- **Versioning**: Passed. `pyproject.toml` version will be updated.
- **Mandatory Testing**: Passed. We will add unit tests for `evaluate_dynamic_path`.
- **Continuous Documentation**: Passed. We will update the documentation with the new schema feature.

## Project Structure

### Documentation (this feature)

```text
specs/001-dynamic-options-references/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

### Source Code (repository root)

```text
src/structui/
├── state.py    # Will house evaluate_dynamic_path
└── ui.py       # Will resolve dynamic options using the state function
tests/
└── test_state_dynamic_paths.py # Unit tests for path resolution
```

**Structure Decision**: The single Python package structure is utilized. We modify the core logic within `state.py` to maintain a separation of concerns from the UI components.
