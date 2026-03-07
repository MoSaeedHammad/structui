import pytest
from unittest.mock import patch, MagicMock
from structui.ui import StructUI

@pytest.fixture
def mock_app_state():
    state = MagicMock()
    return state

@pytest.fixture
def mock_schema_manager():
    manager = MagicMock()
    return manager

def test_delete_prop_in_list(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.refresh_tree_and_editor = MagicMock()
    
    # Coverage for line 307
    parent_list = [10, 20]
    # We use side_effect to return parent_list regardless of path for this test
    # But wait, in ui.py it calls get_data_by_path(parent_path)
    mock_app_state.get_data_by_path.side_effect = lambda p: parent_list
    
    with patch('structui.ui.ui.row'), patch('structui.ui.ui.button') as mock_btn:
        del_cb = None
        def mock_btn_side(*args, **kwargs):
            nonlocal del_cb
            if kwargs.get('icon') == 'delete_outline':
                del_cb = kwargs.get('on_click')
            return MagicMock()
        mock_btn.side_effect = mock_btn_side
        
        ui_inst.draw_editor("root/list")
        if del_cb: del_cb()
        assert len(parent_list) == 1

def test_tree_expanded_logic(mock_app_state, mock_schema_manager):
    # Coverage for 442-452
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.refresh_tree_and_editor = MagicMock()
    ui_inst.selected_path = {"value": "root"}
    
    class Ev:
        args = ["root", "root/sub"]
    
    with patch('structui.ui.ui.tree') as mock_tree_sys, \
         patch('nicegui.ui.scroll_area'), patch('nicegui.ui.card'), \
         patch('nicegui.ui.row'), patch('nicegui.ui.column'), \
         patch('nicegui.ui.header'), patch('nicegui.ui.button'), \
         patch('nicegui.ui.icon'), patch('nicegui.ui.label'), \
         patch('nicegui.ui.badge'), patch('nicegui.ui.separator'), \
         patch('nicegui.ui.input'), patch('nicegui.ui.dialog'), \
         patch('nicegui.ui.menu'), patch('nicegui.ui.menu_item'), \
         patch('nicegui.ui.dark_mode'):
             
        # Important: self.tree must be assigned THE MOCK that is being interacted with
        m = MagicMock()
        m._props = {"expanded": ["root"]}
        mock_tree_sys.return_value = m
        
        # We need to capture the handler and call it AFTER self.tree = m is done in render()
        actual_handler = None
        def capture_on(evt, handler):
            nonlocal actual_handler
            if evt == 'update:expanded':
                actual_handler = handler
            return MagicMock()
        
        m.on.side_effect = capture_on
        
        ui_inst.render()
        
        if actual_handler:
            actual_handler(Ev())
            
        assert ui_inst.selected_path["value"] == "root/sub"


