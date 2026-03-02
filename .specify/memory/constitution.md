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
