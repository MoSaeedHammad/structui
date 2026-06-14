# Feature Specification: Hex/Decimal Toggle in UI Input

**Feature Branch**: `001-hex-decimal-toggle`
**Created**: 2026-06-14
**Status**: Draft
**Input**: User description: "i want to let the UI handle showing hex values or decimal values based on the loaded yaml input, and if ui.input is added as 0xff for example , save it as hex and support in the ui to have toggle inside the ui.input that toggles the data between hex and decimal"

## Clarifications

### Session 2026-06-14

- Q: What happens when a user types an invalid hex string? → A: Show a validation error and block saving.
- Q: How does the system handle negative numbers in hex format? → A: Treat as unsigned two's complement.
- Q: What happens if the numeric value exceeds the maximum integer size? → A: Show a validation error and block saving.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Smart Loading of Numeric Formats (Priority: P1)

As a user, when I load a YAML file containing numeric values formatted as hex (e.g., `0xff`), the UI input field should automatically recognize and display the value in its original hex format rather than converting it to decimal.

**Why this priority**: Preserving the original data format on load is critical so users do not lose context or see unexpected conversions of hardware/memory addresses or flags.

**Independent Test**: Can be tested by loading a YAML file containing hex values and verifying the UI displays them as hex.

**Acceptance Scenarios**:

1. **Given** a YAML file containing a hex value (e.g., `0x1A`), **When** the file is loaded into the UI, **Then** the UI input field displays the value as `0x1A`.
2. **Given** a YAML file containing a decimal value (e.g., `26`), **When** the file is loaded into the UI, **Then** the UI input field displays the value as `26`.

---

### User Story 2 - Toggling Between Formats (Priority: P1)

As a user, I want a toggle button inside the numeric UI input field that allows me to switch the displayed value instantly between hex and decimal formats.

**Why this priority**: It provides immediate value and flexibility for users who need to view or edit numbers in different formats without manual conversion.

**Independent Test**: Can be tested by interacting with the toggle on an input field and observing the format change.

**Acceptance Scenarios**:

1. **Given** a numeric input field displaying `26`, **When** the user clicks the format toggle, **Then** the value changes to `0x1A` and the toggle indicates hex mode.
2. **Given** a numeric input field displaying `0x1A`, **When** the user clicks the format toggle, **Then** the value changes to `26` and the toggle indicates decimal mode.

---

### User Story 3 - Smart Saving Based on Input Format (Priority: P2)

As a user, when I type a value into the UI input field using hex format (e.g., `0xff`) or have toggled the field to hex mode, the application should save the value in the YAML file as hex.

**Why this priority**: It ensures that data entered or modified by the user is preserved in the desired format when serialized back to YAML.

**Independent Test**: Can be tested by modifying a value in hex format and saving to YAML, then verifying the saved file.

**Acceptance Scenarios**:

1. **Given** a UI input field in hex mode, **When** the user types `0xff` and saves, **Then** the resulting YAML file contains the value `0xff` (not `255`).
2. **Given** a UI input field in decimal mode, **When** the user types `255` and saves, **Then** the resulting YAML file contains the value `255`.

### Edge Cases

- **Invalid Hex Input**: If a user types an invalid hex string (e.g., `0xZZ`), the system MUST show a validation error on the UI input field and block saving.
- **Value Exceeds Max Size**: The system MUST show a validation error and block saving if the numeric value exceeds the maximum supported integer size for the platform.
- **Negative Hex Numbers**: The system MUST treat negative numbers in hex format as unsigned two's complement values rather than using a minus sign.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse numeric values from YAML and detect if they were originally formatted as hexadecimal or decimal strings.
- **FR-002**: System MUST display the initial value in the UI input field matching the detected format from the YAML file.
- **FR-003**: The UI input field for numeric values MUST contain a toggle control (e.g., a button or icon) to switch the display mode between hexadecimal and decimal.
- **FR-004**: System MUST instantly convert the displayed value between hex and decimal when the toggle is activated, without changing the underlying logical value until saved.
- **FR-005**: System MUST allow users to manually type values in either `0x...` format or decimal format, automatically updating the toggle state if appropriate.
- **FR-006**: System MUST serialize and save the numeric value back to YAML in the format currently indicated by the UI toggle (or as typed by the user).

### Key Entities *(include if feature involves data)*

- **Numeric Input Field**: Represents a UI component that holds a numeric value, its current display format state (hex or decimal), and a control to toggle the format.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can load, toggle, edit, and save a file containing hex values with 100% format retention for unmodified fields.
- **SC-002**: Toggling between hex and decimal formats occurs instantly (under 100ms response time).
- **SC-003**: 100% of values saved while in "hex mode" are serialized to the YAML file with the `0x` prefix.
