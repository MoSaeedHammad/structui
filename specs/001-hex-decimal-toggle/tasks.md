---
description: "Task list for Hex/Decimal Toggle feature"
---

# Tasks: Hex/Decimal Toggle

**Input**: Design documents from `/specs/001-hex-decimal-toggle/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Mandatory according to Constitution Principle 6 (Minimum 90% coverage).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Identify UI numeric input locations in `src/structui/ui.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T002 Implement `HexInt` model class extending Python `int` in `src/structui/parser.py`
- [x] T003 Implement PyYAML implicit resolver for `HexInt` loading in `src/structui/parser.py`
- [x] T004 Implement PyYAML representer for `HexInt` serialization in `src/structui/parser.py`

**Checkpoint**: Foundation ready - PyYAML can load and save hex formats natively.

---

## Phase 3: User Story 1 - Smart Loading of Numeric Formats (Priority: P1) 🎯 MVP

**Goal**: Load a YAML file containing numeric values formatted as hex and display it in its original hex format.

**Independent Test**: Can be tested by loading a YAML file with hex values and verifying the parser outputs `HexInt` and the UI shows it correctly.

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T005 [P] [US1] Unit test for PyYAML loading `0x` prefixes into `HexInt` in `tests/test_parser.py`

### Implementation for User Story 1

- [x] T006 [US1] Modify `HexInt.__str__` or `__repr__` to output hex string natively in `src/structui/parser.py`
- [x] T007 [US1] Ensure `ui.input` initialization handles `HexInt` display correctly in `src/structui/ui.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Toggling Between Formats (Priority: P1)

**Goal**: Provide a toggle button inside the numeric UI input field that allows instant switching between hex and decimal formats.

**Independent Test**: Can be tested by interacting with the toggle on an input field and observing the format change.

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T008 [P] [US2] UI test for toggle button injection and format switching in `tests/test_ui.py`
- [x] T009 [P] [US2] UI test for hex input validation errors in `tests/test_ui.py`

### Implementation for User Story 2

- [x] T010 [US2] Inject toggle button inside numeric `ui.input` fields using slots in `src/structui/ui.py`
- [x] T011 [US2] Implement state-switching logic between hex and decimal formats in `src/structui/ui.py`
- [x] T012 [US2] Add regex-based validation rules to block invalid hex strings (e.g. `0xZZ`) in `src/structui/ui.py`
- [x] T013 [US2] Add validation logic to enforce maximum integer size constraints in `src/structui/ui.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Smart Saving Based on Input Format (Priority: P2)

**Goal**: Ensure typed hex values or values toggled to hex mode are saved as hex in the output YAML.

**Independent Test**: Can be tested by modifying a value in hex format and saving to YAML, then verifying the file.

### Tests for User Story 3 (MANDATORY) ⚠️

- [x] T014 [P] [US3] Unit test for PyYAML saving `HexInt` back to `0x` string in `tests/test_parser.py`
- [x] T015 [P] [US3] UI test ensuring input changes generate `HexInt` objects for the schema in `tests/test_ui.py`

### Implementation for User Story 3

- [x] T016 [US3] Update UI change handlers to cast hex-mode inputs back to `HexInt` before updating the underlying unified state in `src/structui/ui.py`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T017 [P] Update documentation and GitHub page content (MANDATORY)
- [x] T018 Run quickstart.md validation to ensure manual testing passes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup. BLOCKS all user stories.
- **User Stories (Phase 3+)**: Depend on Foundational. Proceed sequentially (US1 → US2 → US3) or concurrently.
- **Polish (Final Phase)**: Depends on all user stories.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2.
- **User Story 2 (P1)**: Depends on US1 completion for optimal UI integration, but toggle UI can be developed in parallel.
- **User Story 3 (P2)**: Depends on US2 to capture the format state before saving.

### Parallel Opportunities

- Tests (T005, T008, T009, T014, T015) can be developed concurrently.
- UI Toggle Logic (T010, T011, T012, T013) can be worked on while PyYAML `HexInt` is finalized.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and 2.
2. Implement Phase 3 (US1).
3. Validate loading YAML and viewing natively in hex.

### Incremental Delivery

1. Deliver US1 MVP.
2. Implement US2 for interactive toggling and UI validation.
3. Implement US3 to ensure full round-trip preservation from UI back to YAML.
