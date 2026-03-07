---
description: "Task list for XML Support implementation"
---

# Tasks: XML Support

**Input**: Design documents from `/specs/001-xml-support/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Tests are MANDATORY according to Constitution Principle 6 (Minimum 90% coverage).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 [P] Verify `xmltodict` or any other undesired third party dependencies aren't present in `pyproject.toml`
- [x] T002 Update `pyproject.toml` version (Constitution Principle 5)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented
**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create `src/structui/xml_parser.py` outline for core logic (ElementTree imports)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Load and Visualize XML File (Priority: P1) 🎯 MVP

**Goal**: Users need to open and visualize the contents of an XML file in the UI, similarly to how they currently view JSON or YAML files.
**Independent Test**: Load a valid XML document via the application interface and verify that its hierarchical structure is accurately reflected in the editor view without data loss.

### Tests for User Story 1 (MANDATORY) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T004 [P] [US1] Unit test for strictly well-formed XML parsing without lists in `tests/test_xml_parser.py`
- [x] T005 [P] [US1] Unit test for XML parsing with single elements strictly mapped to single-item arrays based on schema in `tests/test_xml_parser.py`
- [x] T006 [P] [US1] Unit test for handling malformed XML elegantly in `tests/test_xml_parser.py`

### Implementation for User Story 1

- [x] T007 [US1] Implement `load_xml` method in `src/structui/xml_parser.py` utilizing `xml.etree.ElementTree`
- [x] T008 [US1] Implement attribute parsing logic in `load_xml` applying the `@` prefix to attribute keys
- [x] T009 [US1] Implement schema-driven array inference logic in `load_xml` to parse matching nodes into lists
- [x] T010 [US1] Add malformed XML `xml.etree.ElementTree.ParseError` handling and user prompts into the main UI loading flow at `src/structui/app.py`
- [x] T011 [US1] Integrate `load_xml` into the core file loader routing in `src/structui/core.py` (or equivalent loader mechanism) for `.xml` extensions

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Edit and Save XML File (Priority: P2)

**Goal**: Users need to edit the loaded XML data using the generic UI and save the modifications back to a valid XML file format.
**Independent Test**: Modify an existing loaded XML value in the UI and save it, then verify the output file is a valid, well-formed XML document containing the changes.

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T012 [P] [US2] Unit test for serializing unified dictionary back to XML strings in `tests/test_xml_parser.py`
- [x] T013 [P] [US2] Unit test for expanding Lists back to sibling tags during XML serialization in `tests/test_xml_parser.py`
- [x] T014 [P] [US2] Unit test for stripping `@` prefixes off dictionary keys and restoring them as XML properties during serialization in `tests/test_xml_parser.py`

### Implementation for User Story 2

- [x] T015 [US2] Implement `dict_to_xml` and `save_xml` methods in `src/structui/xml_parser.py`
- [x] T016 [US2] Implement dictionary to XML Element unrolling, resolving List values into sibling XML tags in `src/structui/xml_parser.py`
- [x] T017 [US2] Implement dictionary key analysis to convert keys starting with `@` back into XML attributes strictly in `src/structui/xml_parser.py`
- [x] T018 [US2] Integrate `save_xml` into the core file saving routing in `src/structui/core.py` (or equivalent saver mechanism) for `.xml` extensions

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T019 [P] Update documentation `docs/index.html` (or equivalent repository docs) and GitHub page content with XML feature (MANDATORY)
- [x] T020 Run `pytest --cov=src` to verify over 90% test coverage threshold met
- [x] T021 Code cleanup and format verification (e.g. `black`, `flake8`, or `ruff` if present)

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery
1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Each story adds value without breaking previous stories
