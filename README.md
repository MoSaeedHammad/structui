# StructUI

StructUI is a format-agnostic, schema-driven, hierarchical configuration UI engine built in Python. Designed as a flexible architectural backbone, it parses standard configuration files (YAML, JSON, CSV, XML) and dynamically generates a live web-based property editor based on constraints and metadata defined in a schema file. 

The architecture is explicitly decoupled, making it readily extensible to strict domain-specific specifications (e.g., AUTOSAR configurators) and agent-driven programmatic workflows.

## Features

- **Pillar A: Format-Agnostic Parsers:** cleanly separate UI generation from underlying data formats. Out-of-the-box support for YAML, JSON, and XML (including schema-driven arrays and attributes), with abstract base classes extensible to CSV and others.
- **Pillar B: Hierarchical UI:** Dynamic tree-based rendering with full support for multidimensional containers, dynamic polymorphic list additions, and node mapping. Powered natively by NiceGUI.
- **Pillar C: Data Validity:** Enforces schema metadata strictly at the UI layer. Missing fields gracefully populate via defaults, required flags trigger locking, and nested typings are continuously evaluated.
- **Pillar D: Extensibility & Programmatic Control:** Decomposed core logic (App, Parser, State, Schema, UI) allowing external tools and wrappers (e.g. CLI, Agent Workflows) to invoke the editor or inject properties safely.

## Installation & Setup

StructUI leverages standard Python packaging mechanisms.

```bash
# Clone the repository
git clone https://github.com/your-username/structui.git
cd structui

# Install the application locally
pip install -e .
```

## Quick Start

Launch the editor in the current directory against your local configuration files by simply typing:

```bash
structui --dir . --schema .structui_schema.yaml --port 8080
```
