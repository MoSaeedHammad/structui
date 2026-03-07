# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add new feature to support XML file visualization and editing in the StructUI editor along with existing YAML and JSON support. The system will parse XML into the existing unified state dictionary format, utilizing schema-driven enforcement to natively detect and parse XML lists.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python >= 3.9
**Primary Dependencies**: NiceGUI, pyyaml, built-in xml module (or 3rd party xmltodict - documented in research.md)
**Storage**: File-based (XML)
**Testing**: pytest (Mandatory >= 90% coverage)
**Target Platform**: Cross-platform Web/Desktop UI & CLI
**Project Type**: Python Library / CLI / GUI Application
**Performance Goals**: Load valid XML configuration files up to 5MB in under 2 seconds
**Constraints**: UI component must remain ignorant of XML structure; purely mapped to internal unified dictionary state
**Scale/Scope**: Handling standard application and system XML configuration files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Separation of Concerns**: UI remains completely ignorant of XML format. XML is parsed entirely into a generic Python dictionary representation.
- [x] **Strict Immutability in Validation**: Users cannot modify XML schemas from the UI.
- [x] **Domain Extensibility**: XML parsing feature adds a generic file loader, no domain-specific rules.
- [x] **Agent-Friendly CLI**: CLI support for parsing and loading `.xml` extension files.
- [x] **Versioning**: `pyproject.toml` version must be bumped.
- [x] **Mandatory Testing & Coverage**: Pytest will be written for the XML parser and coverage kept >= 90%.
- [x] **Continuous Documentation**: Docs and Github Pages will be updated with XML support instructions.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
└── structui/
    ├── app.py           # Add XML extension detection
    ├── core.py          # Implement or plug in XML generic parsing logic
    └── cli.py           # Expose XML file support to CLI

tests/
└── core/                # New unit tests for xml loading/saving guaranteeing 90% coverage
```

**Structure Decision**: Integrating XML parser natively into the `structui` core package (likely modifying `app.py` or a dedicated `utils.py`/`parser.py` if present) keeping the single project structure. No new projects needed.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*(No violations exist. XML support fits perfectly into the established configuration viewer/editor paradigm.)*
