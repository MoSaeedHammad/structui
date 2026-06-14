# Implementation Plan: Hex/Decimal Toggle

**Branch**: `001-hex-decimal-toggle` | **Date**: 2026-06-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-hex-decimal-toggle/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

The feature introduces the ability to automatically preserve hex formatting when loading YAML files into StructUI. It utilizes a custom `HexInt` PyYAML extension to retain format information while keeping the state numeric. The NiceGUI frontend will be updated to display this format, provide a toggle button inside numeric inputs to switch between hex and decimal, and perform validation to prevent saving invalid hex strings.

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**: NiceGUI >= 1.4.0, PyYAML >= 6.0.1
**Storage**: Local YAML files
**Testing**: pytest
**Target Platform**: Cross-platform Web/Desktop App
**Project Type**: Python UI Application
**Performance Goals**: Instant format toggling (< 100ms)
**Constraints**: Must strictly adhere to PyYAML extension rather than swapping parsing libraries. UI must remain ignorant of format parsing specifics.
**Scale/Scope**: Impacts all numeric inputs loaded from YAML within the application.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **1. Separation of Concerns**: PASSED. UI does not parse YAML. `HexInt` class keeps the UI ignorant by acting as a native integer with format metadata handled during serialization.
- **2. Strict Immutability in Validation**: PASSED. Invalid hex strings trigger UI validation errors and block mutation of the schema/state.
- **6. Mandatory Testing & Coverage**: PENDING. Will require adding tests for PyYAML loader/dumper extensions and UI toggle interactions to maintain 90% coverage.

## Project Structure

### Documentation (this feature)

```text
specs/001-hex-decimal-toggle/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
└── structui/
    ├── parser.py        # Add HexInt, PyYAML resolvers, and representers
    └── ui.py            # Update UI components (ui.input) to include hex/dec toggle and validation

tests/
├── test_parser.py       # Add tests for HexInt parsing and dumping
└── test_ui.py           # Add tests for UI toggle interactions and validation
```

**Structure Decision**: The project uses a standard Python package structure (`src/structui`). Changes will be isolated to the parser module (for YAML format preservation) and the UI module (for the toggle and validation logic).
