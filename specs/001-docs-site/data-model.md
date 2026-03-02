# Data Model: Documentation Subsystem (docs-site)

## Entities

### `docs-site/` (Docusaurus Application)
- **Type**: External React/Node.js Framework Host
- **Relationships**:
  - Requires isolated `package.json` for frontend tooling.
  - Generates to `build/` directory for static GitHub Pages routing.
- **Constraints**:
  - Must remain completely segregated from `src/structui` core package logic.
  - `docusaurus.config.js` sets domain/repo configuration.
- **State**: Build transitions from local `.md` state -> static `html` delivery on `gh-pages` branch.

### `examples/embedded_designer.py` (Script)
- **Type**: NiceGUI Execution Context (Parent App)
- **Relationships**:
  - Imports `structui.ui.StructUI` directly.
  - Instantiates `AppState` and `SchemaManager` manually.
- **Constraints**:
  - Exists as a standalone demo script to prove plugin/embed-ability.
  - Renders the editor within a sub-frame (e.g. `ui.card()`).
