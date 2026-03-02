---
sidebar_position: 4
---

# Embedding StructUI

One of StructUI's core design principles is modularity. It is not just a standalone application; it is built atop [NiceGUI](https://nicegui.io/) as a set of nested components. This allows developers to embed the entire StructUI designer inside a broader custom application interface.

## Core Concept
StructUI's primary view is encapsulated in the `StructUI` class, which exposes a `.render()` method. When `.render()` is called, it mounts all its sub-components (the tree view, the editor pane, toolbars) into the current Active NiceGUI context (such as a `ui.column()` or `ui.card()`).

## Example Usage

The following is an excerpt from `examples/embedded_designer.py`, demonstrating how to wrap StructUI with a custom enterprise application layout containing a header, sidebar, and constrained main content area.

```python
from nicegui import ui
from structui.ui import StructUI
from structui.state import AppState
from structui.schema import SchemaManager

def create_embedded_designer():
    # 1. Initialize core state and schema manager
    schema_manager = SchemaManager(".structui_schema.yaml")
    app_state = AppState(".", schema_manager)
    
    # 2. Add an overarching application header
    with ui.header().classes('bg-blue-900 justify-between'):
        ui.label("Enterprise Configuration Hub").classes('text-lg font-bold')
        ui.label("v1.2.0").classes('text-sm')
    
    # 3. Create a layout with a sidebar
    with ui.left_drawer().classes('bg-blue-50 p-4'):
        ui.label("Navigation Menu").classes("text-lg font-bold mb-4")
        ui.button("Dashboard", on_click=lambda: ui.notify("Going to Dashboard..."))

    # 4. Instantiate StructUI within a specific column/card container
    with ui.column().classes('w-full max-w-5xl mx-auto p-4'):
        ui.label("Embedded Configuration Editor").classes("text-2xl font-bold mb-4")
        
        with ui.card().classes('w-full bg-white shadow-md'):
            # Instantiate and render the StructUI editor component
            designer = StructUI(app_state, schema_manager)
            designer.render()

if __name__ in {"__main__", "__mp_main__"}:
    @ui.page('/')
    def main_page():
        create_embedded_designer()
        
    ui.run(title="Embedded StructUI Example", port=8080)
```

By providing localized `AppState` and `SchemaManager` instances, multiple `StructUI` instances could technically run side-by-side or on different routes within the same NiceGUI server, handling entirely distinct schemas.
