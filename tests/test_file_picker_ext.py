import pytest
from unittest.mock import patch, MagicMock

import sys

# Must match test_file_picker.py MockDialog setup
class MockDialog:
    def __init__(self, *args, **kwargs):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def submit(self, *args):
        pass
    def close(self):
        pass

mock_nicegui = MagicMock()
mock_nicegui.ui.dialog = MockDialog
sys.modules['nicegui'] = mock_nicegui

from structui.file_picker import LocalFilePicker

def test_file_picker_extensions(tmp_path):
    (tmp_path / "file1.txt").touch()
    (tmp_path / "file2.csv").touch()
    (tmp_path / "dir1").mkdir()

    picker = LocalFilePicker(directory=str(tmp_path), allowed_extensions=[".txt", "yaml"])

    # Let's see what picker is. We know picker.grid is whatever the __init__ assigned.
    # In LocalFilePicker it assigns `self.grid = ui.aggrid(...)` but we mocked `ui` from `nicegui`.
    # Actually wait. The mock_nicegui has `ui` which is a MagicMock.
    # That means `ui.aggrid` returns a MagicMock, and `.classes().on()` returns another.
    # The actual LocalFilePicker calls `self.update_grid()` at the end of `__init__`.
    # But because `self.grid.options` wasn't explicitly initialized in the mock, it might just be a MagicMock object, not a dict.

    # We can just manually assign and re-call it for the test logic
    picker.grid = MagicMock()
    picker.grid.options = {}
    picker.update_grid()

    assert len(picker.grid.options['rowData']) == 3
    paths = [r['path'] for r in picker.grid.options['rowData']]
    assert str(tmp_path / "file2.csv") not in paths
