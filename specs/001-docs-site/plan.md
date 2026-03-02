# Implementation Plan: Documentation Architecture & Docusaurus Site

**Branch**: `001-docs-site` | **Date**: 2026-03-02 | **Spec**: [spec.md](file:///E:/Git_Repos/structui/specs/001-docs-site/spec.md)
**Input**: Feature specification from `/specs/001-docs-site/spec.md`

## Summary

The user requests an expansive Docusaurus documentation website hosted on GitHub Pages detailing the architecture of StructUI, alongside a practical example of embedding the NiceGUI editor inside a broader host application.

## Technical Context

**Language/Version**: Node 18+ (Docusaurus), Python 3.9+ (Examples)  
**Primary Dependencies**: `docusaurus`, `nicegui`, `structui`  
**Storage**: Flat-file `.md` generation via Docusaurus  
**Testing**: Local Docusaurus serve / `tests/test_ui.py` context checks  
**Target Platform**: GitHub Pages (`.github.io`)
**Project Type**: Static Site + Demo Script  
**Performance Goals**: N/A  
**Constraints**: UI integration must support component injection into a parent DOM block.  
**Scale/Scope**: ~5 Markdown Tutorial Pages  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Separation of Concerns:** Does not blend parsers with UI logic. Simply creates documentation detailing the boundary. (PASS)
- **Immutability in Validation:** Examples will showcase how validation rules reject input via UI. (PASS)
- **Domain Extensibility:** Fulfills the AUTOSAR mandate by explicitly demonstrating how to embed the GUI in domain-specific downstream projects via `embedded_designer.py`. (PASS)
- **Agent-Friendly CLI:** Documenting architecture naturally benefits secondary LLM ingestion. (PASS)

## Project Structure

### Documentation (this feature)

```text
specs/001-docs-site/
├── plan.md              
├── research.md          
├── data-model.md        
├── quickstart.md        
└── tasks.md             
```

### Source Code (repository root)

```text
website/                    # The standalone Docusaurus project
├── docs/                   # Markdown guides
│   ├── intro.md
│   ├── architecture.md
│   ├── api.md
│   └── embedding.md
├── src/                    # React components
├── docusaurus.config.js    # Crucial gh-pages configuration
└── package.json

examples/
└── embedded_designer.py    # Required demonstrator script
```

**Structure Decision**: A strictly isolated `/website` folder scaffolded by `create-docusaurus` handles React compilation independently from the core Python package. Example scripts reside in `/examples` in the repository root.
