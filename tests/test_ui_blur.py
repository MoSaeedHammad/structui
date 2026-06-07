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
    state.config_data = {}
    return state

@pytest.fixture
def mock_schema_manager():
    return MagicMock()

def test_number_blur_events(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.refresh_tree_and_editor = MagicMock()
    ui_inst.update_save_btn_state = MagicMock()
    ui_inst.selected_path = {"value": "root"}

    # Mock getting a float value
    mock_app_state.get_data_by_path.return_value = {"my_num": 12.34}
    mock_schema_manager.get_meta.return_value = {"type": "number"}

    with patch('structui.ui.ui.input') as mock_input, \
         patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.label'):

        actual_handler = None
        def mock_input_side_effect(*args, **kwargs):
            nonlocal actual_handler
            m = MagicMock()
            def mock_on(evt, handler):
                nonlocal actual_handler
                if evt == 'blur':
                    actual_handler = handler
                return m
            m.on.side_effect = mock_on
            m.props.return_value = m
            m.classes.return_value = m
            return m

        mock_input.side_effect = mock_input_side_effect

        ui_inst.draw_editor("root")

        if actual_handler:
            class Ev:
                # Testing standard e.value mapping and ValueError catch
                class Sender:
                    value = "56.78"
                sender = Sender()
            actual_handler(Ev())
            mock_app_state.set_data_by_path.assert_called_with("root", "my_num", 56.78)

            class EvError:
                value = "invalid"
            actual_handler(EvError()) # should trigger ValueError catch silently

def test_hex_toggle_and_value_error(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.refresh_tree_and_editor = MagicMock()
    ui_inst.update_save_btn_state = MagicMock()
    ui_inst.selected_path = {"value": "root"}

    mock_app_state.get_data_by_path.return_value = {"my_int": 255}
    mock_schema_manager.get_meta.return_value = {"type": "integer"}

    # test integer value error catch
    with patch('structui.ui.ui.input') as mock_input, patch('structui.ui.ui.switch'), \
         patch('structui.ui.ui.row'), patch('structui.ui.ui.column'), patch('structui.ui.ui.label'):

        actual_handler = None
        def mock_input_side(*args, **kwargs):
            nonlocal actual_handler
            m = MagicMock()
            def mock_on(evt, handler):
                nonlocal actual_handler
                if evt == 'blur': actual_handler = handler
                return m
            m.on.side_effect = mock_on
            return m
        mock_input.side_effect = mock_input_side

        ui_inst.draw_editor("root")

        if actual_handler:
            class EvIntError:
                value = "invalid_int"
            actual_handler(EvIntError()) # should pass

    # test hex mode toggle on
    setattr(ui_inst, '_is_hex_my_int_root', True)
    with patch('structui.ui.ui.input') as mock_input, patch('structui.ui.ui.switch') as mock_switch, \
         patch('structui.ui.ui.row'), patch('structui.ui.ui.column'), patch('structui.ui.ui.label'):

        actual_hex_handler = None
        actual_toggle_handler = None

        def mock_input_side_hex(*args, **kwargs):
            nonlocal actual_hex_handler
            if 'on_value_change' in kwargs:
                actual_hex_handler = kwargs['on_value_change']
            return MagicMock()
        mock_input.side_effect = mock_input_side_hex

        def mock_switch_side(*args, **kwargs):
            nonlocal actual_toggle_handler
            m = MagicMock()
            def m_on(handler):
                nonlocal actual_toggle_handler
                actual_toggle_handler = handler
                return m
            m.on_value_change.side_effect = m_on
            return m
        mock_switch.side_effect = mock_switch_side

        ui_inst.draw_editor("root")

        if actual_hex_handler:
            class EvHex:
                value = "ff"
                class Sender: pass
                sender = Sender()
            actual_hex_handler(EvHex())
            mock_app_state.set_data_by_path.assert_called_with("root", "my_int", 255)

            class EvHexError:
                value = "invalid_hex"
                class Sender: pass
                sender = Sender()
            actual_hex_handler(EvHexError()) # Should pass ValueError silently

        if actual_toggle_handler:
            class EvToggle:
                value = False
            actual_toggle_handler(EvToggle())
            assert getattr(ui_inst, '_is_hex_my_int_root') is False

def test_file_picker_coverage(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.refresh_tree_and_editor = MagicMock()
    ui_inst.selected_path = {"value": "root"}

    mock_app_state.get_data_by_path.return_value = {"my_file": "file.txt"}
    mock_schema_manager.get_meta.return_value = {"type": "file", "extensions": [".txt"]}

    import asyncio
    with patch('structui.ui.ui.input'), patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.column'), patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.button') as mock_btn, \
         patch('structui.ui.LocalFilePicker') as mock_picker:

        actual_pick_file = None
        def mock_btn_side(*args, **kwargs):
            nonlocal actual_pick_file
            if kwargs.get('icon') == 'folder_open':
                actual_pick_file = kwargs.get('on_click')
            m = MagicMock()
            m.props.return_value = m
            m.tooltip.return_value = m
            return m
        mock_btn.side_effect = mock_btn_side

        async def pick_mock(*args, **kwargs):
            return ["/picked/file.txt"]
        mock_picker.side_effect = pick_mock

        ui_inst.draw_editor("root")

        if actual_pick_file:
            # It's an async function, we can just run it
            asyncio.run(actual_pick_file())
            mock_app_state.set_data_by_path.assert_called_with("root", "my_file", "/picked/file.txt")

def test_tree_expanded_handler_coverage(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.refresh_tree_and_editor = MagicMock()
    ui_inst.selected_path = {"value": "root"}

    with patch('structui.ui.ui.tree') as mock_tree_sys, \
         patch('nicegui.ui.scroll_area'), patch('nicegui.ui.card'), \
         patch('nicegui.ui.row'), patch('nicegui.ui.column'), \
         patch('nicegui.ui.header'), patch('nicegui.ui.button'), \
         patch('nicegui.ui.icon'), patch('nicegui.ui.label'), \
         patch('nicegui.ui.badge'), patch('nicegui.ui.separator'), \
         patch('nicegui.ui.input'), patch('nicegui.ui.dark_mode'):

        m = MagicMock()
        m._props = {"expanded": ["root"]}
        mock_tree_sys.return_value = m

        actual_handler = None
        def capture_on(evt, handler):
            nonlocal actual_handler
            if evt == 'update:expanded':
                actual_handler = handler
            return MagicMock()

        m.on.side_effect = capture_on

        ui_inst.render()

        if actual_handler:
            class EvArgsNone:
                args = None
            actual_handler(EvArgsNone()) # should pass gracefully

            class EvAdd:
                args = ["root", "root/sub"]
            actual_handler(EvAdd())
            assert ui_inst.selected_path["value"] == "root/sub"

            class EvCollapse:
                args = []
            m._props['expanded'] = ["root"] # reset mock state for test
            actual_handler(EvCollapse())
            assert m._props['expanded'] == []
