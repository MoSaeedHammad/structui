# Research & Architecture Decisions

## YAML Parsing & Hex Preservation
- **Decision**: Extend PyYAML's `SafeLoader` and `Dumper` with a custom implicit resolver for hex strings, mapping them to a custom `HexInt(int)` Python class.
- **Rationale**: PyYAML natively converts `0x...` into standard Python `int`, discarding the format. By creating a `HexInt` subclass of `int` and adding an implicit resolver (`re.compile(r'^[-+]?0x[0-9a-fA-F_]+$')`) that constructs this type, we preserve the original format. A corresponding representer will ensure `HexInt` instances are serialized back as hex strings prefixed with `0x`. This satisfies the Constitution's mandate to keep the UI ignorant of parsing intricacies by unifying the state to Python objects.
- **Alternatives considered**: 
  - Switching to `ruamel.yaml` (provides round-trip format preservation out-of-the-box, but introduces a heavy dependency and might require rewriting existing parser logic). 
  - Storing format separately in metadata dictionaries (complex mapping overhead between data state and UI state).

## UI Toggle & Validation (NiceGUI)
- **Decision**: Use `ui.input` with an appended icon button (`<template v-slot:append>`) for the toggle, and implement `validation` rules to block invalid inputs.
- **Rationale**: `ui.input` is flexible and allows injecting elements (like a toggle button) inside the input box using slots. The `validation` parameter in `ui.input` handles error messages naturally, satisfying the requirement to display validation errors and block saving for invalid hex strings or out-of-bound values.
- **Alternatives considered**: 
  - Two separate input fields toggled by `v-if` (clunky UI).
  - External toggle switch next to the input (less clean than inline).

## Handling Negative Hex and Integer Size Limits
- **Decision**: Parse negative hex strings utilizing unsigned two's complement behavior, and validate max size against standard 64-bit bounds (or Python's arbitrary size if appropriate, though UI must enforce practical limits).
- **Rationale**: The specification requires treating negative numbers as unsigned two's complement and blocking inputs that exceed integer sizes. We will enforce a 64-bit unsigned limit (since Python supports arbitrary precision, the limit is artificial but useful for UI validation).
- **Alternatives considered**: None.
