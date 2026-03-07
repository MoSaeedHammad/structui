# Feature Specification: XML Support

**Feature Branch**: `001-xml-support`  
**Created**: 2026-03-07  
**Status**: Draft  
**Input**: User description: "add new feature to support xml files visualization along with yamls and jsons"

## Clarifications

### Session 2026-03-07
- Q: XML intrinsically lacks a native array structure. How should the system enforce or detect lists natively mapped to single sibling tags vs objects? → A: Schema-driven enforcement: Rely strictly on the underlying schema metadata to enforce a list type, correctly parsing a single element as a single-item array in the unified state.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load and Visualize XML File (Priority: P1)

Users need to open and visualize the contents of an XML file in the UI, similarly to how they currently view JSON or YAML files.

**Why this priority**: Core request of the feature. Without the ability to load and view XML, the feature delivers no value.

**Independent Test**: Can be fully tested by loading a valid XML document via the application interface and verifying that its hierarchical structure is accurately reflected in the editor view.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** the user selects a valid XML file to load, **Then** the application accurately displays the XML elements and attributes in a hierarchical structure.
2. **Given** the application is running, **When** the user selects a malformed XML file, **Then** the application rejects it and displays an appropriate parsing error message.

---

### User Story 2 - Edit and Save XML File (Priority: P2)

Users need to edit the loaded XML data using the generic UI and save the modifications back to a valid XML file format.

**Why this priority**: Since StructUI is a configuration editor, users will expect to not just visualize but also modify and persist XML configurations, following the same pattern as YAML and JSON.

**Independent Test**: Can be fully tested by modifying an existing loaded XML value in the UI and saving it, then verifying the output file is a valid, well-formed XML document containing the changes.

**Acceptance Scenarios**:

1. **Given** an XML file is loaded and visualized, **When** the user modifies a value and saves the file, **Then** the resulting file is a well-formed XML document containing the updated value.

### Edge Cases

- What happens when an XML file contains complex namespaces?
- How does the system handle XML files with attributes but no text content?
- What happens when the XML file contains CDATA sections?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse valid XML files into the internal unified state.
- **FR-002**: System MUST display the unified state of the loaded XML file in the UI, mapping XML elements directly to the existing hierarchical view.
- **FR-003**: System MUST elegantly handle malformed XML files and present a descriptive error message to the user.
- **FR-004**: System MUST allow saving the generalized internal state back into a well-formed XML format.
- **FR-005**: System MUST preserve XML attributes and distinguish them correctly from child elements in the unified state (e.g., using standard prefix notations like `@attribute`).
- **FR-006**: System MUST handle XML namespaces, retaining their semantic meaning during parsing and serialization scenarios.

### Assumptions

- The standard industry representation of XML properties into flat dictionary/JSON-like objects will be utilized for baseline parsing.
- Since XML intrinsically lacks a native array structure, the system will use **schema-driven enforcement** to detect arrays. It will rely strictly on the underlying schema metadata to enforce list types, ensuring that even a single XML element matching an array schema is cast into a single-item array in the unified internal state to prevent unpredictable parsing heuristic errors.
- Advanced XML features such as arbitrary DTD validations and external entity resolution are not required for standard configuration workflows and will be ignored or disabled to prevent security risks (e.g., XXE).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully load, visualize, and save valid XML configuration files up to 5MB in under 2 seconds.
- **SC-002**: 100% of recognized elements and attributes from valid loaded XML files are present in the editor view without data loss.
- **SC-003**: Any modifications saved produce a strictly well-formed XML document format, as verified by standard XML linters.
