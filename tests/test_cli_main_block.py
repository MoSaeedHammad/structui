import sys
import pytest
from unittest.mock import patch
import structui.cli

def test_cli_main_block():
    with patch.object(sys, "argv", ["structui", "--dir", ".", "--schema", "s.yaml", "--port", "1234"]):
        with patch("structui.app.run_app") as mock_run_app:
            import runpy
            runpy.run_path(structui.cli.__file__, run_name="__main__")
            mock_run_app.assert_called_once_with(data_dir=".", schema_filepath="s.yaml", port=1234)
