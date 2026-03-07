import os
import pytest
from unittest.mock import patch
from structui.state import AppState
from structui.schema import SchemaManager

@pytest.fixture
def mock_schema_manager(tmp_path):
    schema_path = tmp_path / "schema.yaml"
    schema_path.write_text("""
root:
  type: dict
  allowed_children: [setting1, list1]
setting1:
  type: string
list1:
  type: list
empty_root:
  type: list
    """, encoding="utf-8")
    return SchemaManager(str(schema_path))

@pytest.fixture
def mock_data_dir(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    file1 = data_dir / "config.yaml"
    file1.write_text("setting1: test_val\nlist1:\n  - a\n  - b", encoding="utf-8")
    
    file2 = data_dir / "empty_root.json"
    file2.write_text("", encoding="utf-8")
    
    return str(data_dir)

def test_app_state_load(mock_data_dir, mock_schema_manager):
    state = AppState(mock_data_dir, mock_schema_manager)
    assert "config.yaml" in state.config_data
    assert state.config_data["config.yaml"]["setting1"] == "test_val"
    assert "empty_root.json" in state.config_data
    assert isinstance(state.config_data["empty_root.json"], list) # default type instantiated based on schema mapping if JSON failed to parse empty
    assert len(state.history) == 1
    assert state.history_index == 0
    assert not state.is_dirty

def test_app_state_get_set_data(mock_data_dir, mock_schema_manager):
    state = AppState(mock_data_dir, mock_schema_manager)
    
    root = state.get_data_by_path("root")
    assert "config.yaml" in root
    
    val = state.get_data_by_path("root/config.yaml/setting1")
    assert val == "test_val"
    
    state.set_data_by_path("root/config.yaml", "setting1", "new_val")
    assert state.get_data_by_path("root/config.yaml/setting1") == "new_val"
    assert not state.is_dirty  # is_dirty is evaluated against commits
    
    val_list = state.get_data_by_path("root/config.yaml/list1/0")
    assert val_list == "a"
    
    state.set_data_by_path("root/config.yaml/list1", "0", "c")
    assert state.get_data_by_path("root/config.yaml/list1/0") == "c"

    assert state.get_data_by_path("root/invalid/path") is None
    assert state.get_data_by_path("root/config.yaml/setting1/invalid") is None
    assert state.get_data_by_path("root/config.yaml/list1/99") is None

def test_app_state_commit_undo_redo(mock_data_dir, mock_schema_manager):
    state = AppState(mock_data_dir, mock_schema_manager)
    
    state.set_data_by_path("root/config.yaml", "setting1", "val1")
    state.commit()
    
    state.set_data_by_path("root/config.yaml", "setting1", "val2")
    state.commit()
    
    assert state.get_data_by_path("root/config.yaml/setting1") == "val2"
    
    assert state.undo()
    assert state.get_data_by_path("root/config.yaml/setting1") == "val1"
    
    assert state.undo()
    assert state.get_data_by_path("root/config.yaml/setting1") == "test_val"
    
    assert not state.undo()
    
    assert state.redo()
    assert state.get_data_by_path("root/config.yaml/setting1") == "val1"
    
    assert state.redo()
    assert state.get_data_by_path("root/config.yaml/setting1") == "val2"
    
    assert not state.redo()

def test_app_state_save(mock_data_dir, mock_schema_manager):
    state = AppState(mock_data_dir, mock_schema_manager)
    state.set_data_by_path("root/config.yaml", "setting1", "saved_val")
    state.commit()
    
    state.save_all_to_disk()
    assert not state.is_dirty
    assert state.last_saved_index == state.history_index
    
    state2 = AppState(mock_data_dir, mock_schema_manager)
    assert state2.get_data_by_path("root/config.yaml/setting1") == "saved_val"

def test_app_state_save_error(mock_data_dir, mock_schema_manager, capsys):
    state = AppState(mock_data_dir, mock_schema_manager)
    
    with patch('structui.state.get_parser', side_effect=Exception("Save Error")):
        state.save_all_to_disk()
        
    captured = capsys.readouterr()
    assert "Error saving" in captured.out

def test_app_state_history_limit(mock_data_dir, mock_schema_manager):
    state = AppState(mock_data_dir, mock_schema_manager)
    
    for i in range(105):
        state.set_data_by_path("root/config.yaml", "setting1", f"val{i}")
        state.commit()
        
    assert len(state.history) == 100
    assert state.history_index == 99

def test_app_state_schema_exclusion(mock_data_dir, mock_schema_manager):
    # Coverage for line 34: skip loading the schema file itself
    schema_path = os.path.join(mock_data_dir, "schema.yaml")
    with open(schema_path, "w") as f:
        f.write("test: true")
    
    mock_schema_manager.schema_filepath = schema_path
    state = AppState(mock_data_dir, mock_schema_manager)
    assert "schema.yaml" not in state.config_data

def test_app_state_history_pop_saved_index(mock_data_dir, mock_schema_manager):
    # Coverage for line 60: decrementing last_saved_index when history pops
    state = AppState(mock_data_dir, mock_schema_manager)
    state.last_saved_index = 5
    
    for i in range(105):
        state.set_data_by_path("root/config.yaml", "setting1", f"v{i}")
        state.commit()
        
    # last_saved_index gets shifted down to -1 as those states fall off the tail
    assert state.last_saved_index == -1

def test_app_state_remove_error(mock_data_dir, mock_schema_manager, capsys):
    # Coverage for lines 133-136: os.remove exception handling during save
    state = AppState(mock_data_dir, mock_schema_manager)
    # create a dummy file to be removed
    dummy = os.path.join(mock_data_dir, "dummy.yaml")
    with open(dummy, "w") as f:
        f.write("a: 1")
    
    with patch('os.remove', side_effect=Exception("Permission Denied")):
        state.save_all_to_disk()
    
    captured = capsys.readouterr()
    assert "Error removing dummy.yaml" in captured.out
