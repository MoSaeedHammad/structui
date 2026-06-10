import sys
import os
import pytest
import subprocess
from unittest.mock import patch, MagicMock
from structui.cli import main
from structui import cli

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

def test_cli_entry_point():
    with patch.object(sys, "argv", ["structui", "--dir", ".", "--schema", ".structui_schema.yaml", "--port", "8080"]):
        with patch("structui.cli.run_app") as mock_run_app:
            main()
            mock_run_app.assert_called_once_with(data_dir=".", schema_filepath=".structui_schema.yaml", port=8080)

def test_cli_main_direct():
    with patch.object(sys, 'argv', ['structui', '--port', '9090']), patch('structui.cli.run_app') as mock_run:
        cli.__name__ = '__main__'
        cli.main()
        mock_run.assert_called_once_with(data_dir='.', schema_filepath='.structui_schema.yaml', port=9090)

def test_cli_execution():
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    result = subprocess.run([sys.executable, "-m", "structui.cli", "--help"], env=env, capture_output=True, text=True)
    assert result.returncode == 0
    assert "StructUI Configuration Editor" in result.stdout
