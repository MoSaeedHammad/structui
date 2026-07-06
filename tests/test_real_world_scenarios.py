import os
import pytest
from unittest.mock import patch, MagicMock

from structui.schema import SchemaManager
from structui.state import AppState
from structui.ui import StructUI

@pytest.fixture
def mock_schema_path():
    return os.path.join("tests", "fixtures", "test_schema.yaml")

@pytest.fixture
def mock_data_dir(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    import shutil
    shutil.copy(os.path.join("tests", "fixtures", "data", "config.yaml"), str(data_dir / "config.yaml"))

    return str(data_dir)

def test_full_scenario(mock_schema_path, mock_data_dir):
    schema_manager = SchemaManager(mock_schema_path)
    state = AppState(mock_data_dir, schema_manager)

    assert "config.yaml" in state.config_data

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    # Load initial state
    assert state.config_data["config.yaml"]["core_config"]["app_name"] == "TestApp"

    # Simulate UI interaction to change theme
    ui_inst.selected_path = {"value": "root/config.yaml/user_settings/theme"}

    mock_select_callbacks = {}
    with patch('structui.ui.ui.select') as mock_select, patch('structui.ui.ui.row'), patch('structui.ui.ui.icon'), patch('structui.ui.ui.label'), patch('structui.ui.ui.card'), patch('structui.ui.ui.button'), patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), patch('structui.ui.ui.column'), patch('structui.ui.ui.separator'), patch('structui.ui.ui.switch'):
        def select_side_effect(*args, **kwargs):
            mock_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_select_callbacks[lbl] = cb
                return mock_ret
            mock_ret.on_value_change = on_value_change
            mock_ret.classes.return_value = mock_ret
            return mock_ret
        mock_select.side_effect = select_side_effect

        ui_inst.draw_editor("root/config.yaml/user_settings")

    cb = mock_select_callbacks.get('theme')
    assert cb is not None

    e = MagicMock()
    e.value = "light"
    cb(e)

    assert state.config_data["config.yaml"]["user_settings"]["theme"] == "light"
    assert state.is_dirty

    # Trigger save
    state.save_all_to_disk()
    assert not state.is_dirty
