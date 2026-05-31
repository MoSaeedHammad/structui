import sys
from unittest.mock import patch
from structui.cli import main

def test_cli_entry_point():
    with patch.object(sys, "argv", ["structui", "--dir", ".", "--schema", ".structui_schema.yaml", "--port", "8080"]):
        with patch("structui.cli.run_app") as mock_run_app:
            main()
            mock_run_app.assert_called_once_with(data_dir=".", schema_filepath=".structui_schema.yaml", port=8080)
