import sys
import pytest
from unittest.mock import patch
import structui.cli

def test_cli_main_block():
    with patch.object(sys, "argv", ["structui", "--dir", ".", "--schema", "s.yaml", "--port", "1234"]):
        with patch("structui.cli.run_app") as mock_run_app:
            with open(structui.cli.__file__) as f:
                code = compile(f.read(), structui.cli.__file__, "exec")
                namespace = {"__name__": "__main__", "__file__": structui.cli.__file__}

                # Mock run_app inside the namespace
                # wait, run_app is imported inside the code. We can mock it after import or mock in sys.modules

            with patch("structui.app.run_app") as mock_run_app2:
                exec(code, namespace)
                mock_run_app2.assert_called_once_with(data_dir=".", schema_filepath="s.yaml", port=1234)
