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

def test_run_app_with_exception():
    with patch('structui.app.SchemaManager') as mock_schema, \
         patch('structui.app.AppState', side_effect=Exception("Initialization Error")) as mock_state, \
         patch('structui.app.AppState') as mock_state_fallback, \
         patch('structui.app.StructUI') as mock_ui, \
         patch('structui.app.ui.run') as mock_ui_run, \
         patch('structui.app.ui.page'):
        
        # We need to make the fallback state creation work
        fallback_inst = MagicMock()
        mock_state_fallback.return_value = fallback_inst
        
        # Test how app handles the exception
        import structui.app
        # Mock structui.app.AppState to first fail, then succeed
        with patch.object(structui.app, 'AppState', side_effect=[Exception("Init Error"), fallback_inst]):
            run_app(data_dir="test_dir", schema_filepath="test_schema.yaml", port=8080, dark_mode=False)
            
        # The UI should be instantiated with the fallback
        mock_ui.assert_called_once_with(fallback_inst, mock_schema.return_value, False)
        assert fallback_inst.config_data == {}

def test_run_app_main_page_rendering():
    # Test lines 21-23: calling the rendered main_page directly
    with patch('structui.app.SchemaManager'), \
         patch('structui.app.StructUI') as mock_ui, \
         patch('structui.app.ui.run'):
         
        mock_page_decorator = MagicMock()
        with patch('structui.app.ui.page', return_value=mock_page_decorator) as mock_page:
            
            # This captures the decorated main_page function
            def mock_decorator_impl(func):
                func()
                return func
                
            mock_page.return_value = mock_decorator_impl
            
            # We must be careful not to trigger actual NiceGUI framework globals
            import structui.app
            mock_notify = MagicMock()
            mock_fallback = MagicMock()
            
            with patch.object(structui.app.ui, 'notify', mock_notify), \
                 patch.object(structui.app, 'AppState', side_effect=[Exception("Boot Error"), mock_fallback]):
                run_app()
                
                # Check render was called
                mock_ui.return_value.render.assert_called_once()
                # Check notify was called with the error
                mock_notify.assert_called_once()
                args, kwargs = mock_notify.call_args
                assert "Boot Error" in args[0]
                assert kwargs["type"] == "negative"
