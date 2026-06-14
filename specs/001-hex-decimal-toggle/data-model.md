# Data Model: Hex/Decimal Toggle

## Entities

### `HexInt`
- **Base Type**: `int`
- **Description**: A subclass of Python's standard `int` used to flag that the numeric value was originally formatted as a hexadecimal string in the loaded YAML file, or set to hex mode via the UI toggle.
- **Validation**:
  - Bound by a 64-bit unsigned maximum limit.
  - UI inputs must be valid hex strings (e.g., `0x1A`) when in hex mode.
- **State Transitions**:
  - **Load**: PyYAML implicit resolver detects `0x...` and returns a `HexInt` instance.
  - **UI Update**: Toggling formats changes the UI string representation but the underlying state value remains numeric. If hex mode is toggled on, value becomes `HexInt`.
  - **Save**: PyYAML representer converts `HexInt` back to `0x` prefixed hex strings upon serialization.
