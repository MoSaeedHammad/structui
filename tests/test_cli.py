import sys
import pytest
from unittest.mock import patch
from structui.cli import main

def test_cli_main_success():
    with patch('sys.argv', ['structui', '--dir', '.', '--schema', 'schema.yaml', '--port', '8081']), \
         patch('structui.cli.run_app') as mock_run_app:
        main()
        mock_run_app.assert_called_once_with(data_dir='.', schema_filepath='schema.yaml', port=8081)

def test_cli_main_exception(capsys):
    with patch('sys.argv', ['structui', '--port', '8080']), \
         patch('structui.cli.run_app', side_effect=Exception("Test Error")), \
         pytest.raises(SystemExit) as pytest_wrapped_e:
        main()
        
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    
    captured = capsys.readouterr()
    assert "Error starting StructUI: Test Error" in captured.err
