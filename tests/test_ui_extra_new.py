import pytest
from unittest.mock import patch, MagicMock

import sys
mock_nicegui = MagicMock()
if 'nicegui' not in sys.modules:
    sys.modules['nicegui'] = mock_nicegui
else:
    sys.modules['nicegui'].ui = MagicMock()

from structui.ui import StructUI

@pytest.fixture
def mock_app_state():
    return MagicMock()

@pytest.fixture
def mock_schema_manager():
    return MagicMock()

def test_ui_hex_toggle_true(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.refresh_tree_and_editor = MagicMock()
    ui_inst.selected_path = {"value": "root"}

    with patch('structui.ui.ui') as mock_ui:
        mock_ui.row.return_value.__enter__.return_value = MagicMock()
        mock_ui.column.return_value.classes.return_value.__enter__.return_value = MagicMock()

        mock_schema_manager.get_schema_key_for_path.return_value = "key"

        # We need an integer that does NOT have meta.type == 'integer'
        # Looking at ui.py:
        # elif isinstance(v, float) or (isinstance(v, int) and type(v) is not bool and meta.get('type') != 'integer'):
        # Wait, if type != 'integer', it goes to ui.number.
        # So for the hex switch to appear, type MUST BE 'integer'!
        meta_dict = {
            "int_val": {"type": "integer"}
        }
        mock_schema_manager.get_meta.side_effect = lambda k: meta_dict.get(k, {})

        mock_app_state.get_data_by_path.return_value = {
            "int_val": 255
        }

        captured_cbs = {}

        def mock_switch(text, value=False):
            class M:
                def on_value_change(self, cb):
                    captured_cbs['switch'] = cb
                    return self
            return M()
        mock_ui.switch.side_effect = mock_switch

        def mock_input(*args, **kwargs):
            class M:
                def classes(self, c): return self
                def on_value_change(self, cb):
                    captured_cbs['input'] = cb
                    return self
                def on(self, ev, cb): pass
                def props(self, p): return self
            return M()
        mock_ui.input.side_effect = mock_input
        mock_ui.number.side_effect = mock_input

        def mock_button(*args, **kwargs):
            m = MagicMock()
            m.props.return_value.classes.return_value.tooltip.return_value = m
            m.props.return_value.tooltip.return_value = m
            return m
        mock_ui.button.side_effect = mock_button

        ui_inst.draw_editor("root")

        assert 'switch' in captured_cbs
        e = MagicMock()
        e.value = True
        captured_cbs['switch'](e)

        assert getattr(ui_inst, '_is_hex_int_val_root') is True

        ui_inst.draw_editor("root")

        assert 'input' in captured_cbs
        e.value = "FF"
        captured_cbs['input'](e)
        mock_app_state.set_data_by_path.assert_called_with("root", "int_val", 255)

        e.value = "XX"
        captured_cbs['input'](e)

@pytest.mark.asyncio
async def test_ui_pick_file(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.refresh_tree_and_editor = MagicMock()
    ui_inst.selected_path = {"value": "root"}

    with patch('structui.ui.ui') as mock_ui:
        mock_ui.row.return_value.__enter__.return_value = MagicMock()
        mock_ui.column.return_value.classes.return_value.__enter__.return_value = MagicMock()

        mock_schema_manager.get_schema_key_for_path.return_value = "key"
        mock_schema_manager.get_meta.return_value = {"type": "file"}
        mock_app_state.get_data_by_path.return_value = {"file_val": "file.txt"}

        captured_cbs = {}

        def mock_input(*args, **kwargs):
            class M:
                def classes(self, c): return self
                def on_value_change(self, cb): return self
                def on(self, ev, cb): pass
                def props(self, p): return self
            return M()
        mock_ui.input.side_effect = mock_input

        def mock_button(*args, **kwargs):
            if 'on_click' in kwargs and kwargs.get('icon') == 'folder_open':
                captured_cbs['btn'] = kwargs['on_click']
            m = MagicMock()
            m.props.return_value.classes.return_value.tooltip.return_value = m
            m.props.return_value.tooltip.return_value = m
            return m
        mock_ui.button.side_effect = mock_button

        ui_inst.draw_editor("root")

        assert 'btn' in captured_cbs

        with patch('structui.ui.LocalFilePicker', new_callable=MagicMock) as mock_picker:
            async def mock_picker_ret(*args, **kwargs):
                return ["/new/path.txt"]
            mock_picker.side_effect = mock_picker_ret

            await captured_cbs['btn']()
            mock_app_state.set_data_by_path.assert_called_with("root", "file_val", "/new/path.txt")
            mock_app_state.commit.assert_called()

def test_delete_prop(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.refresh_tree_and_editor = MagicMock()
    ui_inst.selected_path = {"value": "root"}

    with patch('structui.ui.ui') as mock_ui:
        mock_ui.row.return_value.__enter__.return_value = MagicMock()
        mock_ui.column.return_value.classes.return_value.__enter__.return_value = MagicMock()

        mock_schema_manager.get_schema_key_for_path.return_value = "key"
        mock_schema_manager.get_meta.return_value = {"type": "string", "required": False}
        mock_app_state.get_data_by_path.return_value = {"str_val": "str"}

        captured_cbs = {}

        def mock_input(*args, **kwargs):
            class M:
                def classes(self, c): return self
                def on_value_change(self, cb): return self
                def on(self, ev, cb): pass
                def props(self, p): return self
            return M()
        mock_ui.input.side_effect = mock_input

        def mock_button(*args, **kwargs):
            if 'on_click' in kwargs and kwargs.get('icon') == 'delete_outline':
                captured_cbs['delete'] = kwargs['on_click']
            m = MagicMock()
            m.props.return_value.classes.return_value.tooltip.return_value = m
            m.props.return_value.tooltip.return_value = m
            m.classes.return_value.tooltip.return_value = m
            return m
        mock_ui.button.side_effect = mock_button

        ui_inst.draw_editor("root")

        assert 'delete' in captured_cbs
        captured_cbs['delete']()
        mock_app_state.commit.assert_called()
