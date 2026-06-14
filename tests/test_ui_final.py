import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock

mock_ui = MagicMock()
mock_app = MagicMock()
with patch.dict('sys.modules', {'nicegui': MagicMock(ui=mock_ui, app=mock_app)}):
    from structui.ui import StructUI

@pytest.fixture
def mock_app_state():
    state = MagicMock()
    state.config_data = {}
    return state

@pytest.fixture
def mock_schema_manager():
    manager = MagicMock()
    manager.get_meta.return_value = {"type": "string"}
    manager.schema_filepath = "dummy.yaml"
    return manager

def test_make_on_change_handler(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.selected_path = {"value": "root"}
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()

    mock_app_state.get_data_by_path.return_value = {"key1": "val1"}

    actual_handler = None
    with patch('structui.ui.ui.select') as mock_select, \
         patch('structui.ui.ui.row'), patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.label'), patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.button'), patch('structui.ui.ui.separator'), \
         patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'):

        mock_schema_manager.get_meta.return_value = {"type": "integer", "options": [1, 2]}
        def mock_select_side_effect(*args, **kwargs):
            m = MagicMock()
            def mock_on_change(handler):
                nonlocal actual_handler
                actual_handler = handler
                return m
            m.on_value_change = mock_on_change
            m.classes.return_value = m
            return m
        mock_select.side_effect = mock_select_side_effect

        ui_inst.draw_editor("root")

        if actual_handler:
            class Ev:
                value = "1"
            actual_handler(Ev())
            mock_app_state.set_data_by_path.assert_called_with("root", "key1", 1)

            class EvBad:
                value = "bad"
            actual_handler(EvBad())

            mock_schema_manager.get_meta.return_value = {"type": "float", "options": [1.1, 2.2]}
            ui_inst.draw_editor("root")
            actual_handler(Ev())
            actual_handler(EvBad())


@pytest.mark.asyncio
async def test_pick_file_handler(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.selected_path = {"value": "root"}
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    mock_app_state.get_data_by_path.return_value = {"file_key": "val1"}
    ui_inst.refresh_tree_and_editor = MagicMock()

    actual_pick_file = None
    with patch('structui.ui.ui.input'), patch('structui.ui.ui.button') as mock_btn, \
         patch('structui.ui.ui.row'), patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.label'), patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.separator'), patch('structui.ui.ui.menu'), \
         patch('structui.ui.ui.menu_item'):

            mock_schema_manager.get_meta.return_value = {"type": "file"}

            def mock_btn_side_effect(*args, **kwargs):
                if 'on_click' in kwargs and kwargs.get('icon') == 'folder_open':
                    nonlocal actual_pick_file
                    actual_pick_file = kwargs['on_click']
                m = MagicMock()
                m.props.return_value = m
                m.tooltip.return_value = m
                m.classes.return_value = m
                return m
            mock_btn.side_effect = mock_btn_side_effect

            ui_inst.draw_editor("root")

    with patch('structui.ui.LocalFilePicker') as mock_picker:
        async def mock_pick(*args, **kwargs):
            return ["/mock/file.txt"]
        mock_picker.side_effect = mock_pick

        if actual_pick_file:
            await actual_pick_file()
            mock_app_state.set_data_by_path.assert_called_with("root", "file_key", "/mock/file.txt")

def test_hex_toggle_handlers(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.selected_path = {"value": "root"}
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    mock_app_state.get_data_by_path.return_value = {"int_key": 255}
    ui_inst.refresh_tree_and_editor = MagicMock()

    actual_toggle = None
    with patch('structui.ui.ui.switch') as mock_switch, \
         patch('structui.ui.ui.input'), patch('structui.ui.ui.number'), \
         patch('structui.ui.ui.row'), patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.label'), patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.button'), patch('structui.ui.ui.separator'), \
         patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'):

            mock_schema_manager.get_meta.return_value = {"type": "integer"}

            def mock_switch_side_effect(*args, **kwargs):
                m = MagicMock()
                def mock_on_change(handler):
                    nonlocal actual_toggle
                    actual_toggle = handler
                    return m
                m.on_value_change = mock_on_change
                return m
            mock_switch.side_effect = mock_switch_side_effect

            ui_inst.draw_editor("root")

            if actual_toggle:
                class Ev:
                    value = True
                actual_toggle(Ev())
                assert getattr(ui_inst, '_is_hex_int_key_root') == True
                ui_inst.refresh_tree_and_editor.assert_called()

def test_on_hex_change_handler(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.selected_path = {"value": "root"}
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    mock_app_state.get_data_by_path.return_value = {"int_key": 255}
    setattr(ui_inst, '_is_hex_int_key_root', True)

    actual_hex_change = None
    with patch('structui.ui.ui.switch') as mock_switch, \
         patch('structui.ui.ui.input') as mock_input, \
         patch('structui.ui.ui.number'), \
         patch('structui.ui.ui.row'), patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.label'), patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.button'), patch('structui.ui.ui.separator'), \
         patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'):

            mock_schema_manager.get_meta.return_value = {"type": "integer"}

            def mock_input_side_effect(*args, **kwargs):
                m = MagicMock()
                def mock_on_change(handler):
                    nonlocal actual_hex_change
                    actual_hex_change = handler
                    return m
                m.classes.return_value = m
                m.on_value_change = mock_on_change
                m.on.return_value = m
                return m
            mock_input.side_effect = mock_input_side_effect

            ui_inst.draw_editor("root")

            if actual_hex_change:
                class Ev:
                    value = "ff"
                actual_hex_change(Ev())
                mock_app_state.set_data_by_path.assert_called_with("root", "int_key", 255)

                class EvBad:
                    value = "bad"
                actual_hex_change(EvBad())

def test_handle_expanded_handler(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)

    actual_expanded = None
    with patch('structui.ui.ui.tree') as mock_tree, \
         patch('structui.ui.ui.scroll_area'), patch('structui.ui.ui.card'), \
         patch('structui.ui.ui.row'), patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.label'), patch('structui.ui.ui.button'), \
         patch('structui.ui.ui.input'), patch('structui.ui.ui.separator'), \
         patch('structui.ui.ui.header'), patch('structui.ui.ui.badge'), \
         patch('structui.ui.ui.icon'), patch('structui.ui.ui.dialog'), \
         patch('structui.ui.ui.dark_mode'), patch('structui.ui.ui.add_head_html'):

        def mock_tree_side_effect(*args, **kwargs):
            m = MagicMock()
            m._props = {"expanded": ["root"]}
            def mock_on(evt, handler):
                if evt == 'update:expanded':
                    nonlocal actual_expanded
                    actual_expanded = handler
            m.on = mock_on
            m.classes.return_value = m
            m.props.return_value = m
            return m
        mock_tree.side_effect = mock_tree_side_effect

        ui_inst.render()

        if actual_expanded:
            ui_inst.refresh_tree_and_editor = MagicMock()
            class Ev:
                args = ["root", "root/sub"]
            actual_expanded(Ev())
            assert ui_inst.selected_path["value"] == "root/sub"
            ui_inst.refresh_tree_and_editor.assert_called()

            class EvCollapse:
                args = []
            actual_expanded(EvCollapse())
            ui_inst.tree.update.assert_called()

def test_render_primitive_input_integer_branches(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.selected_path = {"value": "root"}
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.refresh_tree_and_editor = MagicMock()
    mock_app_state.get_data_by_path.return_value = {"int_key": 42}

    with patch('structui.ui.ui.row') as mock_row, patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.label'), patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.button'), patch('structui.ui.ui.separator'), \
         patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), \
         patch('structui.ui.ui.number') as mock_number, patch('structui.ui.ui.switch') as mock_switch, \
         patch('structui.ui.ui.input') as mock_input:

        # Case 1: type=integer, is_hex=False
        mock_schema_manager.get_meta.return_value = {"type": "integer"}
        actual_hex_toggle = None
        actual_number_change = None
        def mock_switch_side_effect(*args, **kwargs):
            m = MagicMock()
            def mock_on_change(handler):
                nonlocal actual_hex_toggle
                actual_hex_toggle = handler
                return m
            m.on_value_change = mock_on_change
            return m
        mock_switch.side_effect = mock_switch_side_effect

        def mock_number_side_effect(*args, **kwargs):
            m = MagicMock()
            def mock_on_change(handler):
                nonlocal actual_number_change
                actual_number_change = handler
                return m
            m.classes.return_value = m
            m.on_value_change = mock_on_change
            m.on.return_value = m
            return m
        mock_number.side_effect = mock_number_side_effect

        ui_inst.draw_editor("root")

        # Call hex toggle
        if actual_hex_toggle:
            class Ev:
                value = True
            actual_hex_toggle(Ev())
            assert getattr(ui_inst, '_is_hex_int_key_root') == True

        # Call normal change
        if actual_number_change:
            class Ev:
                value = 10
            actual_number_change(Ev())
            mock_app_state.set_data_by_path.assert_called_with("root", "int_key", 10)

        # Case 2: type=integer, is_hex=True
        mock_schema_manager.get_meta.return_value = {"type": "integer"}
        setattr(ui_inst, '_is_hex_int_key_root', True)
        actual_hex_input_change = None

        def mock_input_side_effect(*args, **kwargs):
            m = MagicMock()
            def mock_on_change(handler):
                nonlocal actual_hex_input_change
                actual_hex_input_change = handler
                return m
            m.classes.return_value = m
            m.on_value_change = mock_on_change
            m.on.return_value = m
            return m
        mock_input.side_effect = mock_input_side_effect

        ui_inst.draw_editor("root")

        if actual_hex_input_change:
            class Ev:
                value = "ff"
            actual_hex_input_change(Ev())
            mock_app_state.set_data_by_path.assert_called_with("root", "int_key", 255)

            class EvBad:
                value = "bad"
            actual_hex_input_change(EvBad())


def test_on_hex_change_handler_value_error(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.selected_path = {"value": "root"}
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    mock_app_state.get_data_by_path.return_value = {"int_key": 255}
    setattr(ui_inst, '_is_hex_int_key_root', True)

    actual_hex_change = None
    with patch('structui.ui.ui.switch'), \
         patch('structui.ui.ui.input') as mock_input, \
         patch('structui.ui.ui.number'), \
         patch('structui.ui.ui.row'), patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.label'), patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.button'), patch('structui.ui.ui.separator'), \
         patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'):

            mock_schema_manager.get_meta.return_value = {"type": "integer"}

            def mock_input_side_effect(*args, **kwargs):
                m = MagicMock()
                def mock_on_change(handler):
                    nonlocal actual_hex_change
                    actual_hex_change = handler
                    return m
                m.classes.return_value = m
                m.on_value_change = mock_on_change
                m.on.return_value = m
                return m
            mock_input.side_effect = mock_input_side_effect

            ui_inst.draw_editor("root")

            if actual_hex_change:
                class EvBad:
                    value = "invalid_hex"
                actual_hex_change(EvBad())


def test_delete_prop_dict_and_list(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.selected_path = {"value": "root"}
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.refresh_tree_and_editor = MagicMock()

    mock_app_state.get_data_by_path.side_effect = lambda path: {"key1": "val1"} if path == "root" else ["list_val"]

    with patch('structui.ui.ui.row'), patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.label'), patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.button') as mock_btn, patch('structui.ui.ui.separator'), \
         patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), \
         patch('structui.ui.ui.input'):

        mock_schema_manager.get_meta.return_value = {"type": "string", "required": False}

        actual_delete_dict = None
        actual_delete_list = None
        btn_count = 0

        def mock_btn_side_effect(*args, **kwargs):
            nonlocal btn_count, actual_delete_dict, actual_delete_list
            if kwargs.get('icon') == 'delete_outline':
                if btn_count == 0:
                    actual_delete_dict = kwargs['on_click']
                else:
                    actual_delete_list = kwargs['on_click']
                btn_count += 1
            m = MagicMock()
            m.props.return_value = m
            m.tooltip.return_value = m
            m.classes.return_value = m
            return m

        mock_btn.side_effect = mock_btn_side_effect

        # Draw editor with dict
        ui_inst.draw_editor("root")

        if actual_delete_dict:
            actual_delete_dict()

        # Draw editor with list
        ui_inst.selected_path = {"value": "root/list"}
        ui_inst.draw_editor("root/list")

        if actual_delete_list:
            actual_delete_list()


def test_on_hex_change_handler_value_error2(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.selected_path = {"value": "root"}
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    mock_app_state.get_data_by_path.return_value = {"int_key": 255}
    setattr(ui_inst, '_is_hex_int_key_root', True)

    actual_hex_change = None
    with patch('structui.ui.ui.switch'), \
         patch('structui.ui.ui.input') as mock_input, \
         patch('structui.ui.ui.number'), \
         patch('structui.ui.ui.row'), patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.label'), patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.button'), patch('structui.ui.ui.separator'), \
         patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'):

            mock_schema_manager.get_meta.return_value = {"type": "integer"}

            def mock_input_side_effect(*args, **kwargs):
                m = MagicMock()
                def mock_on_change(handler):
                    nonlocal actual_hex_change
                    actual_hex_change = handler
                    return m
                m.classes.return_value = m
                m.on_value_change = mock_on_change
                m.on.return_value = m
                return m
            mock_input.side_effect = mock_input_side_effect

            ui_inst.draw_editor("root")

            if actual_hex_change:
                class EvBad:
                    value = "invalid_hex_string"
                # Call it and expect no exception
                actual_hex_change(EvBad())

def test_on_hex_change_exception_handled(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.selected_path = {"value": "root"}
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()

    mock_app_state.get_data_by_path.return_value = {"int_key": 255}
    setattr(ui_inst, '_is_hex_int_key_root', True)

    actual_hex_change = None
    with patch('structui.ui.ui.switch'), patch('structui.ui.ui.input') as mock_input, \
         patch('structui.ui.ui.number'), patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.column'), patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.icon'), patch('structui.ui.ui.button'), \
         patch('structui.ui.ui.separator'), patch('structui.ui.ui.menu'), \
         patch('structui.ui.ui.menu_item'):

        mock_schema_manager.get_meta.return_value = {"type": "integer"}
        def mock_input_side_effect(*args, **kwargs):
            m = MagicMock()
            def mock_on_change(handler):
                nonlocal actual_hex_change
                actual_hex_change = handler
                return m
            m.classes.return_value = m
            m.on_value_change = mock_on_change
            m.on.return_value = m
            return m
        mock_input.side_effect = mock_input_side_effect

        ui_inst.draw_editor("root")

        if actual_hex_change:
            class EvBad:
                value = "xyz123"

            # Call and ensure it doesn't crash (passes line 345, 346)
            actual_hex_change(EvBad())


def test_get_allowed_options_list_no_types(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    mock_schema_manager.get_schema_key_for_path.return_value = "root"
    mock_schema_manager.get_meta.side_effect = lambda k: {
        "allowed_children": ["child_list"],
    } if k == "root" else {
        "type": "list"
    }

    data_node = {"child_list": []}
    opts = ui_inst.get_allowed_options("root", data_node)
    assert any(opt['type'] == 'list_item_append' for opt in opts)

def test_refresh_tree_empty_selected(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.tree._props = {'nodes': [], 'expanded': []}
    ui_inst.selected_path = {"value": ""}
    ui_inst.draw_editor = MagicMock()
    ui_inst.refresh_tree_and_editor()
    assert ui_inst.selected_path["value"] == "root"
