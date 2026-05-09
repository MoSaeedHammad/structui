import pytest
from unittest.mock import patch, MagicMock
from structui.app import run_app

def test_run_app():
    with patch('structui.app.SchemaManager') as mock_schema, \
         patch('structui.app.AppState') as mock_state, \
         patch('structui.app.StructUI') as mock_ui, \
         patch('structui.app.ui') as mock_ui_module:
        
        run_app(data_dir="test_dir", schema_filepath="test_schema.yaml", port=8081, dark_mode=True)
        
        mock_schema.assert_called_once_with("test_schema.yaml")
        mock_state.assert_called_once_with("test_dir", mock_schema.return_value)
        mock_ui.assert_called_once_with(mock_state.return_value, mock_schema.return_value, True)
        mock_ui_module.run.assert_called_once_with(port=8081, title="StructUI Editor", reload=False)

def test_run_app_with_exception():
    with patch('structui.app.SchemaManager') as mock_schema, \
         patch('structui.app.AppState', side_effect=Exception("Initialization Error")) as mock_state, \
         patch('structui.app.AppState') as mock_state_fallback, \
         patch('structui.app.StructUI') as mock_ui, \
         patch('structui.app.ui') as mock_ui_module:
        
        # We need to make the fallback state creation work
        fallback_inst = MagicMock()
        mock_state_fallback.return_value = fallback_inst
        
        import structui.app
        with patch.object(structui.app, 'AppState', side_effect=[Exception("Init Error"), fallback_inst]):
            run_app(data_dir="test_dir", schema_filepath="test_schema.yaml", port=8080, dark_mode=False)
            
        mock_ui.assert_called_once_with(fallback_inst, mock_schema.return_value, False)

def test_run_app_main_page_rendering():
    with patch('structui.app.SchemaManager'), \
         patch('structui.app.StructUI') as mock_ui, \
         patch('structui.app.ui') as mock_ui_module:
         
        def mock_decorator_impl(func):
            func()
            return func
            
        mock_ui_module.page.return_value = mock_decorator_impl

        import structui.app
        mock_fallback = MagicMock()

        with patch.object(structui.app, 'AppState', side_effect=[Exception("Boot Error"), mock_fallback]):
            run_app()
            
            mock_ui.return_value.render.assert_called_once()
            mock_ui_module.notify.assert_called_once()
            args, kwargs = mock_ui_module.notify.call_args
            assert "Boot Error" in args[0]
            assert kwargs["type"] == "negative"
