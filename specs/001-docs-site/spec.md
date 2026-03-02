# Feature Specification: Repository Documentation & Docusaurus Site

**Feature Branch**: `001-docs-site`  
**Created**: 2026-03-02
**Status**: Draft  
**Input**: User description: "implement compelete repo documentation along with github.io for the docs via docusaurus , documentation shall show examples along with using the ui editor in another nicegui ui context as sub page in case there is designer mode in the tool"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Public API & Architecture Reference (Priority: P1)

Developers integrating or contributing to StructUI need a centralized, deeply structured documentation site to understand the core parsers, schema definitions, and architecture patterns.

**Why this priority**: Without core architectural documentation, external developers cannot safely build plugins or understand the internal AST and `AppState` lifecycles governing validation.

**Independent Test**: Can be verified by a clean build of the Docusaurus site locally containing populated Markdown files detailing the Python API.

**Acceptance Scenarios**:

1. **Given** a fresh clone of the repository, **When** running the local docs server, **Then** all API and architectural reference pages render correctly without broken links.
2. **Given** a push to the `main` branch, **When** the GitHub Pages action triggers, **Then** the updated documentation is deployed live to the `.github.io` domain.

---

### User Story 2 - Embedding StructUI in Custom Host Applications (Priority: P1)

Organizations building domain-specific tools (like custom AUTOSAR "designer modes") need practical examples of how to embed the `StructUI` NiceGUI component seamlessly inside their own, larger NiceGUI applications.

**Why this priority**: A massive selling point of StructUI is its embeddability. Users must explicitly see how to instantiate the editor not just as a standalone CLI, but as a component within a broader dashboard.

**Independent Test**: Can be fully tested by running the provided `examples/embedded_designer.py` script and verifying the StructUI editor appears bounded within a sub-container or sub-page of a parent app.

**Acceptance Scenarios**:

1. **Given** the documentation site, **When** the user navigates to the "Usage Examples" section, **Then** an explicit snippet and tutorial on embedding the UI within a parent NiceGUI context is visible.
2. **Given** the provided embed example script, **When** executed, **Then** the UI successfully handles standard editing functions without breaking the parent application's routing or state.

---

### Edge Cases

- What happens when the host NiceGUI application uses clashing Tailwind styles or global CSS alongside StructUI?
- How does the system handle dark/light mode synchronization between a parent NiceGUI chassis and the embedded StructUI editor?
- What happens if the documentation build fails during the GitHub Actions deployment pipeline?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST include a fully initialized Docusaurus documentation workspace in a `/website` or `/docs-site` directory.
- **FR-002**: System MUST configure GitHub Actions to deploy the built Docusaurus static site to GitHub Pages on merges to `main`.
- **FR-003**: System MUST provide comprehensive architectural and API usage documentation.
- **FR-004**: System MUST include a dedicated section detailing how to embed StructUI within a larger, external NiceGUI application (e.g., a "designer mode" layout).
- **FR-005**: System MUST provide working, runnable Python example scripts demonstrating this embedded integration.

### Key Entities *(include if feature involves data)*

- **Docusaurus Config**: The `docusaurus.config.js` defining site metadata, GitHub repo URL, and deployment configs.
- **Embedded StructUI Instantiation**: The specific Python pattern (`ui.column()` encapsulation or `ui.page('/editor')` routing) used to inject `App` logic safely.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A minimum of 5 core documentation pages (Getting Started, Architecture, Schema Guide, Embedding, Examples) are published and accessible.
- **SC-002**: The `.github.io` site successfully loads and navigates with zero 404 broken internal links.
- **SC-003**: A user can copy the provided embedded NiceGUI example, execute it via Python without modifications, and successfully see the editor load inside a parent page in under 60 seconds.
