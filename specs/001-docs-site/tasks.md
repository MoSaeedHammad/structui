# Tasks: Repository Documentation & Docusaurus Site

**Input**: Design documents from `/specs/001-docs-site/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Docusaurus framework via `npx create-docusaurus@latest website classic`
- [x] T002 Update `.gitignore` to exclude `website/node_modules/`, `website/build/`, and `website/.docusaurus/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core documentation configuration and page structuring

- [x] T003 Configure `website/docusaurus.config.ts` with correct GitHub Pages deployment parameters (`url`, `baseUrl`, `organizationName`, `projectName`)
- [x] T004 [P] Scaffold base Markdown files: `website/docs/intro.md`, `website/docs/architecture.md`, `website/docs/api.md`, `website/docs/embedding.md`
- [x] T005 Update `website/src/pages/index.tsx` (Homepage) to reflect the StructUI branding and purpose
- [x] T006 Update `website/sidebars.ts` to link the new documentation pages

**Checkpoint**: Foundation ready - Docusaurus site structure is running and configured for deployment.

---

## Phase 3: User Story 1 - Public API & Architecture Reference (Priority: P1)

**Goal**: Centralized documentation for developers integrating StructUI to understand the core parsers, schema definitions, and architecture patterns.

**Independent Test**: Running `npm start` in `website/` shows populated Architecture and API pages.

### Implementation for User Story 1

- [x] T007 [P] [US1] Write content for `website/docs/intro.md` explaining the project overview.
- [x] T008 [P] [US1] Write content for `website/docs/architecture.md` detailing the Separation of Concerns between UI and parsers.
- [x] T009 [P] [US1] Write content for `website/docs/api.md` explaining how to map custom parsers (JSON, YAML, CSV) to the internal AST.

**Checkpoint**: At this point, User Story 1 provides all foundational reference material for the repository.

---

## Phase 4: User Story 2 - Embedding StructUI in Custom Host Applications (Priority: P1)

**Goal**: Provide practical examples and documentation on how to embed the `StructUI` NiceGUI component inside external, larger NiceGUI applications.

**Independent Test**: Executing `python examples/embedded_designer.py` launches a NiceGUI instance with StructUI injected into a sub-container.

### Implementation for User Story 2

- [x] T010 [US2] Create and implement `examples/embedded_designer.py` showing `ui.column()` instantiation of `StructUI`.
- [x] T011 [US2] Write content for `website/docs/embedding.md` explaining the embedding code and linking to the example script.

**Checkpoint**: At this point, User Stories 1 AND 2 are fully realized. The Docusaurus site documents both theory and practical embedding.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect deployment and validation

- [x] T012 Validate Docusaurus build process locally (`npm run build`).
- [x] T013 Verify the `.github/workflows/publish.yml` or `ci.yml` properly handles the GitHub Pages push (or if a separate `gh-pages.yml` workflow needs slight adjustments).

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** unblocks **Phase 2 (Foundational)**.
- **Phase 3 (US1)** and **Phase 4 (US2)** can be executed sequentially or in parallel after Phase 2.
- **Phase 5 (Polish)** must run last to validate the entire production build output.
