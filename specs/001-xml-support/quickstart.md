# Quickstart: XML Support

This guide demonstrates how to use `StructUI` with XML configuration files.

## Loading an XML File

You can load an XML file exactly the same way as JSON or YAML files via the CLI:

```bash
# Load an XML configuration file using the built-in Generic Viewer
structui config.xml

# Load an XML configuration file with a strict schema
structui --schema my_schema.yaml config.xml
```

## UI Interaction

Once loaded, the UI visualizes the XML data.
- **Attributes** are displayed with an `@` symbol prefix to distinguish them from child tags.
- Editing an attribute or a value updates the internal structure in real-time.
- Saving the file from the UI will serialize the data back into well-formed XML, preserving your attributes and schema constraints.

*Note: For complex XML array logic (where a single tag should be treated as a list in the UI), ensure you provide a valid JSON/YAML Schema to the StructUI engine.*
