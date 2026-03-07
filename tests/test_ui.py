import pytest
from unittest.mock import patch, MagicMock

# Mock nicegui before importing ui
mock_ui = MagicMock()
mock_app = MagicMock()
with patch.dict('sys.modules', {'nicegui': MagicMock(ui=mock_ui, app=mock_app)}):
    from structui.ui import StructUI

@pytest.fixture
def mock_app_state():
    state = MagicMock()
    state.config_data = {
        "config.yaml": {
            "setting": "value",
            "bool_val": True,
            "int_val": 42,
            "list_val": ["item", 2],
            "dict_val": {"nested": "str"},
            "enum_val": "opt1"
        }
    }
    state.get_data_by_path.return_value = state.config_data["config.yaml"]
    return state

@pytest.fixture
def mock_schema_manager():
    manager = MagicMock()
    manager.get_schema_key_for_path.return_value = "config"
    def mock_get_meta(key):
        if key == "enum_val":
            return {"type": "string", "options": ["opt1", "opt2"]}
        return {
            "allowed_children": ["setting", "new_set"],
            "type": "dict",
            "label_key": "name"
        }
    manager.get_meta.side_effect = mock_get_meta
    manager.get_item_label.return_value = "config.yaml"
    return manager

def test_structui_init(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    assert ui_inst.state == mock_app_state
    assert ui_inst.schema_manager == mock_schema_manager
    assert ui_inst.dark_mode is None

def test_get_allowed_options(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    
    def side_effect(k):
        return {
            "config": {"allowed_children": ["setting", "new_set"], "type": "dict"},
            "setting": {"type": "string"},
            "new_set": {"type": "boolean", "label_key": "custom"}
        }.get(k, {})
    
    mock_schema_manager.get_meta.side_effect = side_effect
    
    opts = ui_inst.get_allowed_options("root/config.yaml", {"setting": "value"})
    assert len(opts) > 0
    assert opts[0]["label"] == "Add New Set"

def test_build_tree_nodes(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    
    nodes = ui_inst.build_tree_nodes(mock_app_state.config_data, "root", "Root")
    assert isinstance(nodes, dict)
    assert nodes["id"] == "root"

def test_update_save_btn_state(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.save_btn = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    
    mock_app_state.is_dirty = True
    ui_inst.update_save_btn_state()

def test_refresh_tree_and_editor(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_area = MagicMock()
    ui_inst.active_path = "root/config.yaml"
    
    ui_inst.build_tree_nodes = MagicMock(return_value=[])
    ui_inst.draw_editor = MagicMock()
    ui_inst.update_save_btn_state = MagicMock()
    ui_inst.update_footer = MagicMock()
    
    ui_inst.refresh_tree_and_editor()
    
    ui_inst.build_tree_nodes.assert_called_once()
    ui_inst.draw_editor.assert_called_once()
    ui_inst.update_save_btn_state.assert_called_once()

def test_render(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.build_tree_nodes = MagicMock(return_value=[{"id": "root", "children": []}])
    
    with patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.splitter'), \
         patch('structui.ui.ui.card'), \
         patch('structui.ui.ui.tree') as mock_tree, \
         patch('structui.ui.ui.button'), \
         patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.space'), \
         patch('structui.ui.ui.scroll_area'), \
         patch('structui.ui.ui.footer'), \
         patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.dark_mode'):
         
         ui_inst.render()

def test_draw_editor(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_area = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    mock_app_state.get_data_by_path.return_value = {"key1": "val1"}
    
    
    def mock_button(*args, **kwargs):
        click_fn = kwargs.get('on_click')
        if click_fn:
            try:
                click_fn()
            except Exception:
                pass
        m = MagicMock()
        m.props.return_value = m
        m.classes.return_value = m
        m.tooltip.return_value = m
        return m

    with patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.space'), \
         patch('structui.ui.ui.button', side_effect=mock_button), \
         patch('structui.ui.ui.input'), \
         patch('structui.ui.ui.number'), \
         patch('structui.ui.ui.menu'), \
         patch('structui.ui.ui.menu_item'), \
         patch('structui.ui.ui.checkbox'), \
         patch('structui.ui.ui.icon'):
         
         ui_inst.draw_editor("root/config.yaml")

def test_handle_add_node(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.refresh_tree_and_editor = MagicMock()
    
    # 1. dict_key
    data_node = {}
    mock_app_state.get_data_by_path.return_value = data_node
    mock_schema_manager.get_meta.return_value = {'type': 'string'}
    ui_inst.handle_add_node("root/config.yaml", {"type": "dict_key", "key": "new_prop"})
    assert "new_prop" in data_node
    
    # 2. list_item
    data_list = []
    mock_app_state.get_data_by_path.return_value = data_list
    ui_inst.handle_add_node("root/list", {"type": "list_item"})
    assert len(data_list) == 1
    
    # 3. list_item_append
    data_dict = {"my_list": []}
    mock_app_state.get_data_by_path.return_value = data_dict
    ui_inst.handle_add_node("root/config", {"type": "list_item_append", "key": "my_list"})
    assert len(data_dict["my_list"]) == 1



def test_handle_add_node_custom_dict(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.refresh_tree_and_editor = MagicMock()
    mock_app_state.get_data_by_path.return_value = {}
    
    with patch('structui.ui.ui.dialog'), patch('structui.ui.ui.card'),          patch('structui.ui.ui.label'), patch('structui.ui.ui.input') as mock_in,          patch('structui.ui.ui.select') as mock_sel, patch('structui.ui.ui.button'):
         
         ui_inst.handle_add_node('root/config.yaml', {'type': 'custom_dict'})

def test_update_footer(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.footer_pane = MagicMock()
    
    with patch('structui.ui.ui.label'), patch('structui.ui.ui.row'),          patch('structui.ui.ui.icon'), patch('structui.ui.ui.badge'),          patch('structui.ui.ui.markdown'):
         
         ui_inst.update_footer(None)
         mock_schema_manager.get_meta.return_value = {'type': 'string', 'desc': 'Desc', 'required': True}
         ui_inst.update_footer('setting1')
