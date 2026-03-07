# Phase 1: Data Model (XML Support)

## Entities

The XML support feature does not introduce new autonomous data entities. It extends the existing configuration system by adding a new parser strategy.

### 1. XML Unified State Mapping

XML nodes are mapped to the generic `dict` structure used by StructUI as follows:

- **Elements with text:** Mapped to `{ "TagName": "TextValue" }`
- **Elements with children:** Mapped to `{ "TagName": { "ChildName": ... } }`
- **Attributes:** Mapped using an `@` prefix to distinguish from child elements: `{ "TagName": { "@AttributeName": "AttrValue", "ChildName": ... } }`
- **Lists (Schema-Driven):** If the schema defines `TagName` as an array/list type, a single `<TagName>` element is parsed into `{ "TagName": [ ... ] }` instead of an object.

## Constraints & Rules

1. **Attribute Prefix:** Attributes MUST be stored with an `@` prefix.
2. **Schema Enforcement:** When converting XML to Dict, the parser MUST consult the schema definition (if available) to wrap single items into lists where the schema requires an array. When saving (Dict to XML), the serialization MUST correctly unfold lists back into multiple sibling XML tags.
