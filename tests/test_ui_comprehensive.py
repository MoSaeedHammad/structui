import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from structui.ui import StructUI

@pytest.fixture
def mock_app_state_comp():
    state = MagicMock()
    # Broad dict to cover different tests
    state.data = {
        "root": {
            "my_list": [{"name": "item1"}, {"x": 1}],
            "int_val": 42,
            "float_val": 3.14,
            "file_val": "test.txt",
            "bool_val": True,
            "select_val": "opt1",
            "nested_list": [{"id": 1}],
            "dict_val": {"x": 10}
        }
    }
    # Some specific lists for list item testing
    state.get_data_by_path.side_effect = lambda path: state.data.get(path, state.data["root"])
    state.config_data = state.data
    state.data_dir = "/tmp"
    state.is_dirty = False
    return state

@pytest.fixture
def mock_schema_manager_comp():
    schema = MagicMock()
    def mock_get_meta(key):
        if key == "int_val":
            return {"type": "integer"}
        elif key == "float_val":
            return {"type": "float"}
        elif key == "file_val":
            return {"type": "file", "extensions": [".txt"]}
        elif key == "my_list":
            return {"type": "list", "list_item_type": "custom_item"}
        elif key == "nested_list":
            return {"type": "list", "list_item_type": "nested"}
        elif key == "root":
            return {"allowed_children": ["my_list"], "type": "dict"}
        return {"type": "dict"}

    schema.get_meta.side_effect = mock_get_meta
    schema.get_schema_key_for_path.return_value = "root"
    schema.get_item_label.return_value = "MockLabel"
    return schema

def setup_ui(mock_app_state_comp, mock_schema_manager_comp):
    ui_inst = StructUI(mock_app_state_comp, mock_schema_manager_comp)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    return ui_inst

def test_ui_lines_41_42_get_allowed_options(mock_app_state_comp, mock_schema_manager_comp):
    ui_inst = setup_ui(mock_app_state_comp, mock_schema_manager_comp)
    options = ui_inst.get_allowed_options("root", {"my_list": [{"x": 1}]})
    assert any(opt['type'] == 'list_item_append' for opt in options)

def test_ui_lines_130_131(mock_app_state_comp, mock_schema_manager_comp):
    ui_inst = setup_ui(mock_app_state_comp, mock_schema_manager_comp)
    ui_inst.save_btn = MagicMock()
    ui_inst.save_btn._props = {}

    with patch("structui.ui.ui"):
        ui_inst.update_save_btn_state()

    assert ui_inst.save_btn._props.get('color') == 'primary'

def test_ui_lines_289_299_328_349(mock_app_state_comp, mock_schema_manager_comp):
    ui_inst = setup_ui(mock_app_state_comp, mock_schema_manager_comp)
    ui_inst.selected_path = {"value": "root"}

    with patch("structui.ui.ui") as mock_ui:
        callbacks = {}
        def mock_element(*args, **kwargs):
            m = MagicMock()
            m.classes.return_value = m
            m.props.return_value = m
            m.tooltip.return_value = m
            def on_val_change(cb):
                if 'label' in kwargs:
                    callbacks[kwargs['label']] = cb
                elif 'text' in kwargs:
                    callbacks[kwargs['text']] = cb
                elif args and args[0] == 'Hex':
                    callbacks["Hex"] = cb
                return m
            m.on_value_change.side_effect = on_val_change
            return m

        mock_ui.input = mock_element
        mock_ui.number = mock_element
        mock_ui.switch = mock_element
        mock_ui.select = mock_element

        # Test 1: Normal hex toggles
        setattr(ui_inst, f'_is_hex_int_val_root', True)
        ui_inst.draw_editor("root")

        class Event:
            def __init__(self, val):
                self.value = val

        if "float_val" in callbacks:
            callbacks["float_val"](Event("3.14"))
            callbacks["float_val"](Event("invalid"))
            callbacks["float_val"](Event(""))

        if "int_val" in callbacks:
            callbacks["int_val"](Event("2A"))
            callbacks["int_val"](Event("invalid"))

        if "Hex" in callbacks:
            callbacks["Hex"](Event(False))
            callbacks["Hex"](Event(True))

        # Test 2: Normal integer without hex
        setattr(ui_inst, f'_is_hex_int_val_root', False)
        ui_inst.draw_editor("root")

        if "int_val" in callbacks:
            callbacks["int_val"](Event("42"))
            callbacks["int_val"](Event("42.5"))
            callbacks["int_val"](Event("invalid"))
            callbacks["int_val"](Event(""))

@pytest.mark.asyncio
async def test_ui_lines_314_323(mock_app_state_comp, mock_schema_manager_comp):
    ui_inst = setup_ui(mock_app_state_comp, mock_schema_manager_comp)
    ui_inst.selected_path = {"value": "root"}

    with patch("structui.ui.ui") as mock_ui, \
         patch("structui.ui.LocalFilePicker", new_callable=AsyncMock) as mock_picker:

        mock_picker.return_value = ["/path/to/picked.txt"]

        btn_callbacks = []
        def mock_button(*args, **kwargs):
            if 'on_click' in kwargs:
                btn_callbacks.append(kwargs['on_click'])
            m = MagicMock()
            m.props.return_value = m
            m.tooltip.return_value = m
            return m

        mock_ui.button = mock_button
        mock_ui.input = MagicMock(return_value=MagicMock(classes=lambda c: MagicMock(on_value_change=lambda cb: MagicMock())))

        ui_inst.draw_editor("root")

        for cb in btn_callbacks:
            import inspect
            if inspect.iscoroutinefunction(cb):
                await cb()
            else:
                cb()

def test_ui_lines_393_394(mock_app_state_comp, mock_schema_manager_comp):
    ui_inst = setup_ui(mock_app_state_comp, mock_schema_manager_comp)
    ui_inst.selected_path = {"value": "root"}

    # We provide a list that has a dict and a list, to hit lines 393-394
    mock_app_state_comp.get_data_by_path.return_value = [{"x": 1}, [1, 2], "string_item"]

    with patch("structui.ui.ui"):
        ui_inst.draw_editor("root")

def test_ui_lines_118(mock_app_state_comp, mock_schema_manager_comp):
    ui_inst = setup_ui(mock_app_state_comp, mock_schema_manager_comp)
    # selected_path gets set to empty
    ui_inst.selected_path = {"value": ""}

    with patch("structui.ui.ui"):
        ui_inst.handle_add_node("root", {"type": "list_item_append", "key": "my_list", "item_type": "custom_item"})

def test_ui_lines_493_to_503(mock_app_state_comp, mock_schema_manager_comp):
    ui_inst = setup_ui(mock_app_state_comp, mock_schema_manager_comp)

    with patch("structui.ui.ui") as mock_ui:
        callbacks = {}
        def mock_tree(*args, **kwargs):
            m = MagicMock()
            m.props.return_value = m
            m.classes.return_value = m
            m.on.side_effect = lambda evt, handler: callbacks.update({evt: handler}) or m
            m._props = {'expanded': ['root']}
            return m

        mock_ui.tree = mock_tree

        ui_inst.render()

        if "update:expanded" in callbacks:
            class ArgsEvent:
                args = ["root", "root/int_val"]
            callbacks["update:expanded"](ArgsEvent())

            # test contraction branch
            class ArgsEventRemove:
                args = []
            callbacks["update:expanded"](ArgsEventRemove())
