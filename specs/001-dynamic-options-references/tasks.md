---
description: "Task list for Dynamic Options References feature implementation"
---

# Tasks: Dynamic Options References

**Input**: Design documents from `/specs/001-dynamic-options-references/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Tests are MANDATORY according to Constitution Principle 6 (Minimum 90% coverage).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Ensure `tests/` directory is prepared for dynamic path testing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Update `src/structui/state.py` to expose necessary config data structures to the dynamic evaluator (if not already public)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Defining Dynamic Options in Schema (Priority: P1) 🎯 MVP

**Goal**: Schema authors need to define dropdown options that dynamically reference other parts of the document.

**Independent Test**: Can be fully tested by providing a schema with a dynamic path reference and ensuring the parser/schema engine evaluates it correctly without UI logic.

### Tests for User Story 1 (MANDATORY) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T003 [P] [US1] Create unit tests for path parsing and wildcard resolution in `tests/test_state_dynamic_paths.py`
- [x] T004 [P] [US1] Create unit tests for deduplication and null-filtering in `tests/test_state_dynamic_paths.py`

### Implementation for User Story 1

- [x] T005 [US1] Implement `evaluate_dynamic_path(data, path)` recursive resolver in `src/structui/state.py`
- [x] T006 [US1] Add deduplication and null-filtering logic to the return output of `evaluate_dynamic_path` in `src/structui/state.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and the core algorithm independently testable.

---

## Phase 4: User Story 2 - Using Dynamic Dropdowns in the UI (Priority: P1)

**Goal**: End users need to see options in a dropdown that are derived from the current state of their data, ensuring they only select valid, existing references.

**Independent Test**: Can be fully tested by rendering a UI with predefined document data containing multiple items, clicking the dropdown, and verifying the options match the data.

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T007 [P] [US2] Create UI integration tests for dynamic dropdown rendering in `tests/test_ui_dynamic_dropdown.py`

### Implementation for User Story 2

- [x] T008 [US2] Update `src/structui/ui.py` (`draw_editor`) to check if `options` from schema is a dynamic reference string containing `[*]`.
- [x] T009 [US2] Update `src/structui/ui.py` to call `state.evaluate_dynamic_path()` and build the `safe_options` array when rendering the `ui.select`.
- [x] T010 [US2] Implement an inline warning UI in `src/structui/ui.py` for when the schema author provides a syntactically invalid path.
- [x] T011 [US2] Add validation logic in `src/structui/ui.py` to mark fields as invalid (validation error) if the currently selected value is deleted from the reference source.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Real-time Option Updates (Priority: P2)

**Goal**: End users need the dynamic dropdown to instantly reflect any additions, modifications, or deletions made to the referenced data elsewhere in the UI.

**Independent Test**: Can be fully tested by adding a new item to the referenced array (e.g., a new interface) and immediately checking if the dropdown includes it.

### Tests for User Story 3 (MANDATORY) ⚠️

- [x] T012 [P] [US3] Create integration test verifying <1s reactive updates to dropdowns after data mutation in `tests/test_ui_dynamic_dropdown.py`

### Implementation for User Story 3

- [x] T013 [US3] Verify and adjust `src/structui/ui.py` to ensure dynamic options are re-evaluated just-in-time when a dependent node is selected.
- [x] T014 [US3] Ensure rendering processing stays under the 200ms threshold for 1,000 array items (add performance logging if needed in `src/structui/state.py`).

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T015 [P] Update documentation with dynamic options syntax in `docs/` and GitHub page content (MANDATORY)
- [x] T016 Verify >90% test coverage threshold via `pytest --cov` across the new state and ui modifications
- [x] T017 Run `quickstart.md` validation to ensure the tutorial schema correctly operates in the final application

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) must complete before User Story 2 (P1) starts interacting with `evaluate_dynamic_path`.
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1's `evaluate_dynamic_path` function.
- **User Story 3 (P2)**: Depends on US2's dropdown implementation.

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models/State functions before UI services
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- Unit tests for US1 (`T003`, `T004`) can run parallel to foundational setup.
- Integration test stubs for US2/US3 (`T007`, `T012`) can be written parallel to US1 state implementation.
- Documentation updates (`T015`) can run in parallel with US3 performance testing.

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create unit tests for path parsing and wildcard resolution in tests/test_state_dynamic_paths.py"
Task: "Create unit tests for deduplication and null-filtering in tests/test_state_dynamic_paths.py"

# Then execute the implementation:
Task: "Implement evaluate_dynamic_path(data, path) recursive resolver in src/structui/state.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Phase 1 & 2: Setup and Foundational
2. Complete Phase 3: User Story 1 (Path Evaluator Core)
3. Complete Phase 4: User Story 2 (UI Dropdown integration)
4. **STOP and VALIDATE**: Test User Story 1 and 2 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Resolver function) → Test independently 
3. Add User Story 2 (UI Integration) → Test independently → Deploy/Demo (MVP!)
4. Add User Story 3 (Reactivity) → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories
