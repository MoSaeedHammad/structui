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


def test_delete_current_container_isolated():
    from structui.ui import StructUI
    from unittest.mock import MagicMock, patch

    mock_app_state = MagicMock()
    mock_schema_manager = MagicMock()
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.refresh_tree_and_editor = MagicMock()

    parent_list = [{"a": 1}]
    mock_app_state.get_data_by_path.return_value = parent_list
    ui_inst.selected_path = {"value": "root/0"}

    with patch('structui.ui.ui.row'), patch('structui.ui.ui.button') as mock_btn, patch('structui.ui.ui.column'):
        del_cb = None
        def mock_btn_side( *args, **kwargs):
            nonlocal del_cb
            if kwargs.get('icon') == 'delete':
                del_cb = kwargs.get('on_click')
            return MagicMock()
        mock_btn.side_effect = mock_btn_side
        ui_inst.draw_editor("root/0")

        if del_cb:
            del_cb()

        assert len(parent_list) == 0
