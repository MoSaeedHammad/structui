# Dynamic Options References

StructUI supports dynamic cross-referenced option lists. Instead of defining static choices in your schema, you can configure dropdowns that extract option values directly from other parts of the active configuration data tree at runtime.

## Schema Configuration

To configure a field to use dynamic options, specify a dot-notation path referencing the target attribute in the schema's `options` field.

### Wildcard Support

You can use the `[*]` wildcard to traverse lists and aggregate values from nested elements.

```yaml
# Schema snippet

routing:
  type: dict
  allowed_children:
    - default_interface

default_interface:
  type: string
  desc: "Select the primary active network interface."
  options: "connections[*].interfaces[*].itf_name"
```

## How It Works

1. **Resolution:** The engine parses the path and traverses the active configuration data.
2. **Deduplication:** Duplicate values are automatically filtered out.
3. **Null-Filtering:** Null, undefined, and empty values are skipped.
4. **Order Preservation:** Option choices maintain their original order in the source data list.
5. **JIT Loading:** Options are resolved just-in-time when rendering or opening the dropdown editor.

## Validation & Robustness

- **Syntax Checks:** If the schema author provides an invalid path syntax, an inline warning is shown in the editor UI without crashing.
- **Reference Deletion:** If a value selected in the dropdown is deleted from the source reference array, the value remains intact in the configuration, but the field is marked invalid with a validation error to prevent data loss.
