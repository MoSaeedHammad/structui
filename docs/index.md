# StructUI

StructUI is a format-agnostic, schema-driven, hierarchical configuration UI engine built in Python. Designed as a flexible architectural backbone, it parses standard configuration files (YAML, JSON, CSV, XML) and dynamically generates a live web-based property editor based on constraints and metadata defined in a schema file.

The architecture is explicitly decoupled, making it readily extensible to strict domain-specific specifications (e.g., AUTOSAR configurators) and agent-driven programmatic workflows.

## Features

- **Format-Agnostic Parsers:** cleanly separate UI generation from underlying data formats. Out-of-the-box support for YAML, JSON, and XML (including schema-driven arrays and attributes), with abstract base classes extensible to CSV and others.
- **Hierarchical UI:** Dynamic tree-based rendering with full support for multidimensional containers, dynamic polymorphic list additions, and node mapping. Powered natively by NiceGUI.
- **Data Validity:** Enforces schema metadata strictly at the UI layer. Missing fields gracefully populate via defaults, required flags trigger locking, and nested typings are continuously evaluated.
- **Extensibility & Programmatic Control:** Decomposed core logic (App, Parser, State, Schema, UI) allowing external tools and wrappers (e.g. CLI, Agent Workflows) to invoke the editor or inject properties safely.
- **Hex/Decimal Toggling:** Automatically detects and preserves hex formatting loaded from YAML configurations. Supports inline format toggling between hex and decimal, with validation logic to restrict inputs to valid hex formats and enforce platform/64-bit size limits.

## Table of Contents

- [Roadmap](ROADMAP.md)
