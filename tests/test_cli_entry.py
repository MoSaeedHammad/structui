import subprocess
import sys
import os

def test_cli_entrypoint():
    # Test that running the module as a script works (covers the if __name__ block)
    # We use -c to just import and check if it runs without crashing immediately
    # or we can use a mock approach, but since we want to cover the __main__ block,
    # we run it as a subprocess with --help to avoid running the full app.
    process = subprocess.Popen(
        [sys.executable, "-m", "structui.cli", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    assert process.returncode == 0
    assert "StructUI Configuration Editor" in stdout
