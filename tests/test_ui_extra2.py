import pytest
from unittest.mock import patch, MagicMock
from structui.ui import StructUI

def test_draw_editor_missing_lines(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.refresh_tree_and_editor = MagicMock()

    # Coverage for line 280-282 (add item logic for missing list item type)
    mock_app_state.get_data_by_path.return_value = []
    ui_inst.selected_path = {"value": "root"}

    with patch('structui.ui.ui') as mock_ui:
        add_cb = None
        def mock_btn(*args, **kwargs):
            nonlocal add_cb
            if kwargs.get('icon') == 'add':
                add_cb = kwargs.get('on_click')
            return MagicMock()
        mock_ui.button.side_effect = mock_btn

        # Draw editor to capture the add button callback
        mock_schema_manager.get_meta.return_value = {"type": "list"} # No list_item_type
        ui_inst.draw_editor("root")

        if add_cb:
            add_cb() # This should trigger the block where list_item_type defaults to "dict"
            # It appends to the list, let's check
            assert len(mock_app_state.get_data_by_path.return_value) == 1
