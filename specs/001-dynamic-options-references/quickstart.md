# Quickstart: Dynamic Options References

To utilize the dynamic options references feature in StructUI schemas:

1. **Schema Definition**: Locate the property you want to provide dropdown options for in your schema.
2. **Define the Reference**: Instead of passing a list to the `options` attribute, pass a dot-notated path string containing `[*]` wildcards.

**Example**:
If your underlying data looks like this:
```json
{
  "connections": [
    {
      "interfaces": [
        {"itf_name": "eth0"},
        {"itf_name": "wlan0"}
      ]
    }
  ],
  "routing": {
    "default_interface": ""
  }
}
```

You can define the schema for `default_interface` to dynamically list all interface names:

```yaml
routing:
  type: dict
  allowed_children:
    - default_interface

default_interface:
  type: string
  options: "connections[*].interfaces[*].itf_name"
```

The StructUI editor will automatically aggregate, deduplicate, and present "eth0" and "wlan0" as dropdown options for `default_interface`.
