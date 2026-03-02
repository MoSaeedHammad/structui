"""
Example of embedding the StructUI NiceGUI component inside a larger custom host application.
"""

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
        ui.button("Dashboard", on_click=lambda: ui.notify("Going to Dashboard..."), icon='dashboard').classes('w-full mb-2')
        ui.button("Settings Editor", on_click=lambda: ui.notify("Already here!"), icon='settings').classes('w-full mb-2')
        ui.button("User Profiles", on_click=lambda: ui.notify("Loading users..."), icon='person').classes('w-full')

    # 4. Instantiate StructUI within a specific column/card
    with ui.column().classes('w-full max-w-5xl mx-auto p-4'):
        ui.label("Embedded Configuration Editor").classes("text-2xl font-bold mb-4")
        with ui.card().classes('w-full bg-white shadow-md'):
            # Instantiate the StructUI editor component inside this container
            designer = StructUI(app_state, schema_manager)
            designer.render()

if __name__ in {"__main__", "__mp_main__"}:
    
    @ui.page('/')
    def main_page():
        create_embedded_designer()
        
    ui.run(title="Embedded StructUI Example", port=8080)
