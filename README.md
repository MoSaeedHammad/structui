# StructUI

[![PyPI version](https://img.shields.io/pypi/v/structui.svg)](https://pypi.org/project/structui/)
[![CI](https://github.com/MoSaeedHammad/structui/actions/workflows/ci.yml/badge.svg)](https://github.com/MoSaeedHammad/structui/actions/workflows/ci.yml)
[![CD](https://github.com/MoSaeedHammad/structui/actions/workflows/publish.yml/badge.svg)](https://github.com/MoSaeedHammad/structui/actions/workflows/publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

StructUI is a format-agnostic, schema-driven, hierarchical configuration UI engine built in Python. Designed as a flexible architectural backbone, it parses standard configuration files (YAML, JSON, CSV, XML) and dynamically generates a live web-based property editor based on constraints and metadata defined in a schema file.

The architecture is explicitly decoupled, making it readily extensible to strict domain-specific specifications (e.g., AUTOSAR configurators) and agent-driven programmatic workflows.

## Features

- **Pillar A: Format-Agnostic Parsers:** cleanly separate UI generation from underlying data formats. Out-of-the-box support for YAML, JSON, and XML (including schema-driven arrays and attributes), with abstract base classes extensible to CSV and others.
- **Pillar B: Hierarchical UI:** Dynamic tree-based rendering with full support for multidimensional containers, dynamic polymorphic list additions, and node mapping. Powered natively by NiceGUI.
- **Pillar C: Data Validity:** Enforces schema metadata strictly at the UI layer. Missing fields gracefully populate via defaults, required flags trigger locking, and nested typings are continuously evaluated.
- **Pillar D: Extensibility & Programmatic Control:** Decomposed core logic (App, Parser, State, Schema, UI) allowing external tools and wrappers (e.g. CLI, Agent Workflows) to invoke the editor or inject properties safely.

## Installation

### From PyPI (recommended)

```bash
pip install structui
```

### From Source (development)

```bash
git clone https://github.com/MoSaeedHammad/structui.git
cd structui
pip install -e .
```

## Quick Start

Launch the editor in the current directory against your local configuration files by simply typing:

```bash
structui --dir . --schema .structui_schema.yaml --port 8080
```
