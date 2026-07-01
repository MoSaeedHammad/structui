import pytest
import re
from unittest.mock import patch, MagicMock
from structui.ui import StructUI

@pytest.fixture
def mock_app_state():
    state = MagicMock()
    state.config_data = {
        "connections.yaml": [
            {
                "interfaces": [
                    {"itf_name": "eth0"},
                    {"itf_name": "wlan0"}
                ]
            }
        ],
        "routing.yaml": {
            "default_interface": "eth0"
        }
    }
    
    from structui.state import evaluate_dynamic_path, clean_dynamic_options
    state.evaluate_dynamic_path.side_effect = evaluate_dynamic_path
    state.clean_dynamic_options.side_effect = clean_dynamic_options
    return state

@pytest.fixture
def mock_schema_manager():
    manager = MagicMock()
    return manager

def test_draw_editor_dynamic_select(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()
    
    mock_schema_manager.get_meta.side_effect = lambda k: {
        "type": "string",
        "options": "connections[*].interfaces[*].itf_name"
    } if k == "default_interface" else {}
    
    mock_app_state.get_data_by_path.side_effect = lambda path: {
        "root/routing.yaml": {"default_interface": "eth0"}
    }.get(path, None)
    
    with patch('structui.ui.ui.select') as mock_select, \
         patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.column'):
             
        ui_inst.draw_editor("root/routing.yaml")
        
        mock_select.assert_called_once()
        args, kwargs = mock_select.call_args
        assert "eth0" in args[0]
        assert "wlan0" in args[0]

def test_draw_editor_invalid_path_syntax(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()
    
    mock_schema_manager.get_meta.side_effect = lambda k: {
        "type": "string",
        "options": "connections[invalid]"
    } if k == "default_interface" else {}
    
    mock_app_state.get_data_by_path.side_effect = lambda path: {
        "root/routing.yaml": {"default_interface": "eth0"}
    }.get(path, None)
    
    with patch('structui.ui.ui.select') as mock_select, \
         patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.label') as mock_label, \
         patch('structui.ui.ui.column'):
             
        ui_inst.draw_editor("root/routing.yaml")
        
        any_warning = any("Invalid path syntax" in str(arg[0]) for arg, _ in mock_label.call_args_list)
        assert any_warning


def test_ui_reactivity_on_mutation(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()
    
    mock_schema_manager.get_meta.side_effect = lambda k: {
        "type": "string",
        "options": "connections[*].interfaces[*].itf_name"
    } if k == "default_interface" else {}
    
    # Initial data
    mock_app_state.get_data_by_path.side_effect = lambda path: {
        "root/routing.yaml": {"default_interface": "eth0"}
    }.get(path, None)
    
    with patch('structui.ui.ui.select') as mock_select, \
         patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.column'):
             
        # Render first time
        ui_inst.draw_editor("root/routing.yaml")
        mock_select.assert_called_once()
        args, kwargs = mock_select.call_args
        assert "eth0" in args[0]
        assert "wlan0" in args[0]
        assert "new_itf" not in args[0]
        
        # Mutate the source data (add a new interface)
        mock_app_state.config_data["connections.yaml"][0]["interfaces"].append({"itf_name": "new_itf"})
        
        # Reset mock_select call tracking
        mock_select.reset_mock()
        
        # Render second time (re-evaluation)
        ui_inst.draw_editor("root/routing.yaml")
        mock_select.assert_called_once()
        args, kwargs = mock_select.call_args
        assert "eth0" in args[0]
        assert "wlan0" in args[0]
        assert "new_itf" in args[0] # New interface must be present!


def test_performance_evaluation_1000_items():
    import time
    from structui.state import evaluate_dynamic_path, clean_dynamic_options
    
    # Create 1,000 items
    interfaces = [{"itf_name": f"eth{i}"} for i in range(1000)]
    data = {
        "connections": [
            {"interfaces": interfaces}
        ]
    }
    
    start_time = time.perf_counter()
    raw_resolved = evaluate_dynamic_path(data, "connections[*].interfaces[*].itf_name")
    cleaned = clean_dynamic_options(raw_resolved)
    end_time = time.perf_counter()
    
    elapsed_ms = (end_time - start_time) * 1000
    assert len(cleaned) == 1000
    assert elapsed_ms < 200 # Must be under 200ms


def test_draw_editor_value_deleted_validation(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()
    
    mock_schema_manager.get_meta.side_effect = lambda k: {
        "type": "string",
        "options": "connections[*].interfaces[*].itf_name"
    } if k == "default_interface" else {}
    
    mock_app_state.get_data_by_path.side_effect = lambda path: {
        "root/routing.yaml": {"default_interface": "deleted_itf"}
    }.get(path, None)
    
    with patch('structui.ui.ui.select') as mock_select, \
         patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.column'):
             
        ui_inst.draw_editor("root/routing.yaml")
        
        assert f"root/routing.yaml/default_interface" in ui_inst.validation_errors
        
        mock_select.assert_called_once()
        args, kwargs = mock_select.call_args
        assert "deleted_itf" in args[0]
        assert "validation" in kwargs
        val_fn = kwargs["validation"]["Value deleted from reference"]
        assert val_fn(None) is False


def test_draw_editor_path_evaluation_exception(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()
    
    mock_schema_manager.get_meta.side_effect = lambda k: {
        "type": "string",
        "options": "connections[*].interfaces[*].itf_name"
    } if k == "default_interface" else {}
    
    mock_app_state.get_data_by_path.side_effect = lambda path: {
        "root/routing.yaml": {"default_interface": "eth0"}
    }.get(path, None)
    
    with patch('structui.ui.ui.select') as mock_select, \
         patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.label') as mock_label, \
         patch('structui.ui.ui.column'), \
         patch('structui.ui.evaluate_dynamic_path', side_effect=Exception("Eval error")):
             
        ui_inst.draw_editor("root/routing.yaml")
        
        any_failed_label = any("Path evaluation failed" in str(arg[0]) for arg, _ in mock_label.call_args_list)
        assert any_failed_label


def test_draw_editor_value_empty(mock_app_state, mock_schema_manager):
    ui_inst = StructUI(mock_app_state, mock_schema_manager)
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()
    
    mock_schema_manager.get_meta.side_effect = lambda k: {
        "type": "string",
        "options": "connections[*].interfaces[*].itf_name"
    } if k == "default_interface" else {}
    
    mock_app_state.get_data_by_path.side_effect = lambda path: {
        "root/routing.yaml": {"default_interface": ""}
    }.get(path, None)
    
    with patch('structui.ui.ui.select') as mock_select, \
         patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.column'):
             
        ui_inst.draw_editor("root/routing.yaml")
        
        assert f"root/routing.yaml/default_interface" not in ui_inst.validation_errors


