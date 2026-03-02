from nicegui import ui
from structui.ui import StructUI
from structui.state import AppState
from structui.schema import SchemaManager

def run_app(data_dir: str = ".", schema_filepath: str = ".structui_schema.yaml", port: int = 8080):
    schema_manager = SchemaManager(schema_filepath)
    app_state = AppState(data_dir, schema_manager)
    
    ui_instance = StructUI(app_state, schema_manager)
    
    @ui.page('/')
    def main_page():
        ui_instance.render()
    ui.run(port=port, title="StructUI Editor", show=False, reload=False)
