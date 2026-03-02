# Quickstart: Docusaurus Documentation Subsystem

This quickstart explains how to scaffold and develop the centralized documentation site for StructUI.

## Pre-requisites
- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher for running the NiceGUI examples)

## 1. Initializing the Documentation Site
The documentation resides in a `website/` project spawned using Docusaurus. 
*(If the folder does not exist, it is generated via `npx create-docusaurus@latest website classic`.)*

```bash
cd website
npm install
npm run start
```
This commands builds the local React instance and hosts a live-reload server at `http://localhost:3000`.

## 2. Editing Content
Content is completely partitioned from implementation code. 
- All articles exist as Markdown (`.md`) files inside `website/docs/`.
- The sidebar navigation is controlled by `website/sidebars.js`.
- The homepage layout and React imports sit in `website/src/pages/index.js`.

## 3. Running the Embedded NiceGUI Demo
To prove out StructUI's modularity, users can test the embedding example without touching the React documentation site:

```bash
# In the root repository
pip install -e .
python examples/embedded_designer.py
```
This will launch a discrete NiceGUI instance (typically on port `8080`) showing StructUI confined natively inside a parent dashboard.
