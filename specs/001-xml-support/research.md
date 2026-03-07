# Phase 0: Research (XML Support)

## Research: XML to Generic Dictionary Parsing

**Context:** The `StructUI` application needs to load, visualize, edit, and save XML files using its existing generic JSON-like dictionary state. XML has unique traits like attributes (which JSON lacks) and single-element lists (which cannot be natively distinguished from objects).

**Decision:** Use the built-in `xml.etree.ElementTree` library for parsing combined with a custom recursive dictionary serializer that is schema-aware.
**Rationale:**
1. **Zero External Dependencies:** `xml.etree.ElementTree` is part of the standard library, minimizing the application footprint.
2. **Schema-Driven Arrays:** The project spec mandates that arrays are detected via the schema, not naive heuristics. Off-the-shelf libraries like `xmltodict` use naive heuristics (if >1 identical sibling, list; if 1, object) which break strict validation rules. Hand-rolling the tree traversal allows us to inject schema-awareness directly into the parsing phase.
3. **Attribute Handling:** We will map XML attributes to dictionary keys using a standard prefix (e.g. `@name` for `name="..."`) to preserve them in the unified state without modifying the core UI renderer.

**Alternatives Considered:**
- *xmltodict (3rd party):* Rejected because its list inference is heuristic and unpredictable against strict schemas.
- *lxml (3rd party):* Rejected because it requires C-extensions and offers no distinct advantage for basic configuration parsing over the standard library.
