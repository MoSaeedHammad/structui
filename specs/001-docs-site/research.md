# Phase 0: Outline & Research

## Docusaurus Setup & Hosting Pattern
- **Decision:** Utilize standard `npx create-docusaurus@latest website classic` scaffolding within a `/docs-site` subdirectory.
- **Rationale:** The repository is Python-based (setup tools/pyproject), so isolating the Node.js/React Docusaurus ecosystem in its own folder prevents polluting the root directory. Docusaurus provides out-of-the-box Markdown parsing, sidebar generation, and GitHub Pages deployment configuration (`docusaurus.config.js` -> `organizationName` and `projectName`).
- **Alternatives considered:** MkDocs with Material theme. While MkDocs is natively Python and fits the ecosystem well, the user explicitly requested **Docusaurus** via `github.io`.

## NiceGUI Embedding Architecture
- **Decision:** Demonstrate embedding StructUI using parameterized instantiation of the `StructUI` class within a `ui.column()` or specific `ui.page()` context, rather than running it via the `app.py` CLI hook.
- **Rationale:** The `StructUI` class in `ui.py` is inherently decoupled from the global `ui.run()` startup server (it only binds UI elements to the current NiceGUI context when `render()` is called). This means external developers can instantiate `AppState` and `SchemaManager`, pass them to `StructUI(...)`, and call `.render()` inside their own layout containers.
- **Alternatives considered:** Using iframe sub-routing. Rejected because it breaks python-level variable sharing and state management between the parent "designer" app and the editor.

## Documentation Structure
- **Decision:** 
  1. `docs/intro.md`: What is StructUI?
  2. `docs/architecture.md`: The Separation of Concerns (Schema vs Editor).
  3. `docs/api.md`: How to write custom parsers.
  4. `docs/embedding.md`: The NiceGUI host tutorial.
- **Rationale:** Fulfills all acceptance criteria in `spec.md` while remaining easily maintainable.
