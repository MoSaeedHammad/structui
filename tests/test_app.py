import pytest
from unittest.mock import patch, MagicMock
from structui.app import run_app

def test_run_app():
    with patch('structui.app.SchemaManager') as mock_schema, \
         patch('structui.app.AppState') as mock_state, \
         patch('structui.app.StructUI') as mock_ui, \
         patch('structui.app.ui.run') as mock_ui_run, \
         patch('structui.app.ui.page'):
        
        run_app(data_dir="test_dir", schema_filepath="test_schema.yaml", port=8081, dark_mode=True)
        
        mock_schema.assert_called_once_with("test_schema.yaml")
        mock_state.assert_called_once_with("test_dir", mock_schema.return_value)
        mock_ui.assert_called_once_with(mock_state.return_value, mock_schema.return_value, True)
        mock_ui_run.assert_called_once_with(port=8081, title="StructUI Editor", reload=False)
