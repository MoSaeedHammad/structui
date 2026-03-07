<!--
Sync Impact Report:
- Version change: Unversioned -> 1.1.0
- Added sections:
  - Principle 6: Mandatory Testing & Coverage
  - Principle 7: Continuous Documentation
  - Governance
- Templates requiring updates:
  - .specify/templates/tasks-template.md (✅ updated)
-->
# The StructUI Constitution

## System Context & Role
StructUI is an expert-level configuration editor and validator, designed to provide a robust, generic, and metadata-driven interface for complex data structures. This constitution dictates the engineering philosophy and contribution rules for the project.

## Engineering Principles

### 1. Separation of Concerns
The UI layer **MUST** remain entirely ignorant of the underlying data format.
- Parsers (JSON, YAML, XML, CSV) map purely to an internal unified state.
- The UI reads exclusively from this unified generic state, never parsing files directly.

### 2. Strict Immutability in Validation
UI inputs **CANNOT** modify the underlying schema.
- The schema is the absolute source of truth and dictates all validation rules.
- The UI strictly enforces these rules and rejects invalid state mutations.

### 3. Domain Extensibility (The AUTOSAR Principle)
The core engine **MUST** remain generic.
- Complex, domain-specific logic (e.g., standardizing open-source AUTOSAR configurations) must be implemented strictly via modular plugins or sub-classing.
- No domain-specific hacks or hardcoded business logic shall clutter the core codebase.

### 4. Agent-Friendly CLI
The tool **MUST** support headless or CLI-driven execution alongside the GUI.
- It must be fully interoperable with external AI orchestration workflows and agentic pipelines (e.g., OpenClaw integrations).
    - Core actions (loading, validating, saving) must be accessible via programmatic APIs and CLI entrypoints.

### 5. Versioning
The `pyproject.toml` version **MUST** be updated each time a new change or feature is requested. This ensures that every contribution is explicitly tracked as a separate release version.

### 6. Mandatory Testing & Coverage
Pytest is mandatory. Every new feature or implementation **MUST** maintain a minimum of 90% test coverage.
- Code changes without corresponding tests or dropping coverage below the threshold are rejected.

### 7. Continuous Documentation
Auto update for the documentations and GitHub page content **MUST** be performed for each change.
- Every functional change must be accompanied by relevant updates to system documentation to ensure accuracy and freshness.

## Governance
This Constitution supersedes all other practices and architectural decisions.
- All PRs and code reviews must verify compliance with the stated principles.
- Amendments to this document require a structured review and an update to the version header.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): Original adoption date unknown | **Last Amended**: 2026-03-07
