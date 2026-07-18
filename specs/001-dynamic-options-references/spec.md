# Feature Specification: Dynamic Options References

**Feature Branch**: `001-dynamic-options-references`  
**Created**: 2026-06-14  
**Status**: Draft  
**Input**: User description: "i want to support for references for data for options for example to describe cross reference information to be used as part of parsable data ,, for example connections[*].interfaces[*].itf_name can be used in the schema as options for the drop downlist of another attribute, when this drop down list is clicked, the data is constructed based on the combination of all connections , all interfaces all itf_name"

## Clarifications

### Session 2026-06-14

- Q: Behavior on Reference Deletion → A: Keep the value but mark the field as invalid (validation error).
- Q: Option Format → A: Simple strings only (display matches value).
- Q: Ordering of Options → A: In the order they appear in the source data array.
- Q: Invalid Path Syntax → A: Display a visible warning inline in the UI for the author.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Defining Dynamic Options in Schema (Priority: P1)

Schema authors need to define dropdown options that dynamically reference other parts of the document, so they don't have to duplicate data or write complex custom logic.

**Why this priority**: This is the core capability that enables all other features. Without the ability to define the cross-references in the schema, the UI cannot render them.

**Independent Test**: Can be fully tested by providing a schema with a dynamic path reference and ensuring the parser/schema engine accepts it and stores the reference correctly.

**Acceptance Scenarios**:

1. **Given** a schema definition, **When** an author configures a field's options with a path like `connections[*].interfaces[*].itf_name`, **Then** the system registers the field as having dynamic options based on that data path.

---

### User Story 2 - Using Dynamic Dropdowns in the UI (Priority: P1)

End users need to see options in a dropdown that are derived from the current state of their data, ensuring they only select valid, existing references.

**Why this priority**: This is the user-facing value of the feature, ensuring the data references actually work in practice.

**Independent Test**: Can be fully tested by rendering a UI with predefined document data containing multiple items (e.g., connections and interfaces), clicking the dropdown, and verifying the options match the data.

**Acceptance Scenarios**:

1. **Given** a document with existing connections and interfaces, **When** the user opens the dependent dropdown, **Then** the options list contains all interface names found in the document.
2. **Given** multiple interfaces with the same name across different connections, **When** the user opens the dropdown, **Then** the options list shows deduplicated values.

---

### User Story 3 - Real-time Option Updates (Priority: P2)

End users need the dynamic dropdown to instantly reflect any additions, modifications, or deletions made to the referenced data elsewhere in the UI.

**Why this priority**: Ensures data consistency during an editing session. It's a key UX expectation but relies on the foundational features in P1.

**Independent Test**: Can be fully tested by adding a new item to the referenced array (e.g., a new interface) and immediately checking if the dropdown includes it.

**Acceptance Scenarios**:

1. **Given** a document with an existing dynamic dropdown, **When** the user adds a new interface to a connection, **Then** the dropdown immediately includes the new interface name as an option.
2. **Given** a document, **When** a referenced item is deleted, **Then** it is immediately removed from the dropdown options.

### Edge Cases

- What happens when the reference points to a path that does not exist in the current data (e.g., no connections defined yet)? The dropdown should be empty or disabled.
- How does the system handle null, undefined, or empty string values found at the reference path? They should be ignored or filtered out of the options list.
- How does the system handle circular references or deeply nested paths? The evaluation should be bounded or safely traverse without infinite loops.
- **Data Deletion**: If a currently selected value becomes invalid because the underlying referenced data is deleted, the system MUST keep the value but mark the field as invalid (validation error) to prevent accidental data loss.
- **Invalid Path Syntax**: If the schema author provides a syntactically invalid path reference, the system MUST display a visible warning inline in the UI to alert the author, without crashing the broader schema rendering.

### Dependencies and Assumptions

- **Assumption**: The underlying UI framework can support dynamic option lists that evaluate custom string paths.
- **Assumption**: The syntax for path references is based on a standard object property access notation with `[*]` wildcard support.
- **Dependency**: Requires the existing schema parsing mechanism to accept dynamic references for the `options` attribute.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow schema authors to specify options for a field using a path reference string (e.g., `connections[*].interfaces[*].itf_name`).
- **FR-002**: System MUST dynamically resolve the path reference against the current state of the document data.
- **FR-003**: System MUST support wildcard array indexing (e.g., `[*]`) to collect values from all elements within an array.
- **FR-004**: System MUST construct the list of dropdown options at runtime (e.g., when clicked or rendered).
- **FR-005**: System MUST deduplicate the resolved values so that identical string values only appear once in the dropdown.
- **FR-006**: System MUST filter out null or undefined values from the final options list.
- **FR-007**: System MUST automatically update the available options when the underlying referenced data changes.
- **FR-008**: System MUST treat resolved options as simple strings where the display label exactly matches the underlying value (separate label/value pairs are out of scope).
- **FR-009**: System MUST preserve the order of options as they appear in the source data array when rendering the dropdown.

### Key Entities

- **Option Reference Path**: A string representation defining a specific path in the JSON/data tree, including support for collection wildcards (`[*]`), used to locate available options.
- **Dynamic Field**: A schema attribute configured to use an Option Reference Path instead of a static list of options.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully configure a cross-referenced dropdown in a schema without writing custom scripting.
- **SC-002**: The dynamic dropdown accurately displays 100% of the matching values present in the referenced data.
- **SC-003**: Dropdown options update to reflect data changes in under 1 second.
- **SC-004**: The system can extract and deduplicate options from an array of 1,000 referenced items without causing noticeable UI degradation (under 200ms processing time).
