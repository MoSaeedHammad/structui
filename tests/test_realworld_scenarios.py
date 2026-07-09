import pytest
import shutil
import os
from unittest.mock import MagicMock, patch
import sys

from structui.ui import StructUI
from structui.state import AppState
from structui.schema import SchemaManager
from structui.parser import HexInt

def test_complex_realworld_scenario(tmp_path):
    # Setup test paths in tmp_path to isolate IO
    schema_src = "tests/fixtures/complex_schema.yaml"
    data_src = "tests/fixtures/data/complex_data.yaml"

    schema_dest = tmp_path / "schema.yaml"
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    data_dest = data_dir / "complex_data.yaml"

    shutil.copy(schema_src, schema_dest)
    shutil.copy(data_src, data_dest)

    schema_manager = SchemaManager(str(schema_dest))
    state = AppState(str(data_dir), schema_manager)

    # Verify initial data load
    assert "complex_data.yaml" in state.config_data
    assert isinstance(state.config_data["complex_data.yaml"]["network"]["ecu"][0]["id_value"], HexInt)

    # Initialize UI
    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()

    # Test navigation to a deep node
    ui_inst.draw_editor("root/complex_data.yaml/network/ecu/0")

    # Modify a value
    state.set_data_by_path("root/complex_data.yaml/network/ecu/0", "port", 8081)

    # Verify the value was updated
    assert state.config_data["complex_data.yaml"]["network"]["ecu"][0]["port"] == 8081

    # Verify hex value preservation
    assert state.config_data["complex_data.yaml"]["network"]["ecu"][0]["id_value"] == 256
    assert isinstance(state.config_data["complex_data.yaml"]["network"]["ecu"][0]["id_value"], HexInt)

    # Add a new list item using the UI logic which updates the state
    with patch.object(ui_inst, 'draw_editor') as mock_draw:
        ui_inst.handle_add_node("root/complex_data.yaml/network/ecu", {'type': 'list_item'})

        assert len(state.config_data["complex_data.yaml"]["network"]["ecu"]) == 3
        # Test defaulting of missing required schema keys for the new list item
        new_item = state.config_data["complex_data.yaml"]["network"]["ecu"][2]
        assert new_item == {}

    # Commit changes
    state.commit()
    assert len(state.history) > 1

    # Save to disk
    state.save_all_to_disk()

    # Verify file saved
    assert data_dest.exists()

    # Verify that the saved data correctly reflects the update
    from structui.parser import get_parser
    parser = get_parser(str(data_dest))
    saved_data = parser.load(str(data_dest))
    assert saved_data["network"]["ecu"][0]["port"] == 8081
