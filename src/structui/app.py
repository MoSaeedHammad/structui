from typing import Optional
from nicegui import ui
from structui.ui import StructUI
from structui.state import AppState
from structui.schema import SchemaManager

def run_app(data_dir: str = ".", schema_filepath: str = ".structui_schema.yaml", port: int = 8080, dark_mode: Optional[bool] = False):
    schema_manager = SchemaManager(schema_filepath)
    try:
        app_state = AppState(data_dir, schema_manager)
        load_error = None
    except Exception as e:
        app_state = AppState(".", schema_manager)
        app_state.config_data = {}
        load_error = str(e)
    
    ui_instance = StructUI(app_state, schema_manager, dark_mode)
    
    @ui.page('/')
    def main_page():
        ui_instance.render()
        if load_error:
            ui.notify(f"XML/Config Load Error: {load_error}", type="negative", position="top", timeout=8000)
            
    ui.run(port=port, title="StructUI Editor", reload=False)
