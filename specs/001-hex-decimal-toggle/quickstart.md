# Quickstart: Hex/Decimal Toggle Feature

## Overview
This feature introduces automatic preservation of hexadecimal formats from YAML configuration files. Values starting with `0x` will be loaded as a special `HexInt` object and displayed in the StructUI interface in their original format. A toggle button on numeric inputs allows users to instantly switch the display and serialization format between hex and decimal.

## Getting Started

1. **Load a YAML File**
   Load any YAML file containing hex values (e.g. `memory_addr: 0x4000`).
2. **View in UI**
   Observe that the numeric input field displays `0x4000` rather than its decimal equivalent `16384`.
3. **Toggle Format**
   Click the toggle icon inside the input field to switch the display to `16384`. The toggle will visually indicate that the field is now in decimal mode.
4. **Edit and Validate**
   Try typing an invalid hex string like `0xZZ`. A validation error will appear below the input, and the save action will be blocked until it is corrected.
5. **Save**
   Save the file. If left in hex mode, the resulting YAML will preserve the `0x4000` format. If toggled to decimal, it will save as `16384`.
