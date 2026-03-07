import pytest
import asyncio
from unittest.mock import patch, MagicMock
from pathlib import Path

# Create a mock base class that won't throw nicegui attribute errors
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

import sys
mock_nicegui = MagicMock()
mock_nicegui.ui.dialog = MockDialog
sys.modules['nicegui'] = mock_nicegui

# Unload to ensure it hits our mock
if 'structui.file_picker' in sys.modules:
    del sys.modules['structui.file_picker']

from structui.file_picker import LocalFilePicker

def test_file_picker_init(tmp_path):
    picker = LocalFilePicker(directory=str(tmp_path), show_hidden_files=True)
    assert str(picker.path) == str(tmp_path.resolve())
    assert picker.show_hidden_files is True

    # Test upper_limit=None
    picker_no_limit = LocalFilePicker(directory=str(tmp_path), upper_limit=None)
    assert picker_no_limit.upper_limit is None

def test_file_picker_update_grid(tmp_path):
    (tmp_path / "file1.txt").touch()
    (tmp_path / "dir1").mkdir()
    (tmp_path / ".hidden").touch()

    picker = LocalFilePicker(directory=str(tmp_path), show_hidden_files=False, upper_limit="C:\\")
    picker.grid = MagicMock()
    picker.grid.options = {}
    picker.update_grid()
    assert len(picker.grid.options['rowData']) == 3
    
    picker = LocalFilePicker(directory=str(tmp_path), show_hidden_files=True, upper_limit="C:\\")
    picker.grid = MagicMock()
    picker.grid.options = {}
    picker.update_grid()
    assert len(picker.grid.options['rowData']) == 4

    picker = LocalFilePicker(directory=str(tmp_path), dirs_only=True, upper_limit="C:\\")
    picker.grid = MagicMock()
    picker.grid.options = {}
    picker.update_grid()
    assert len(picker.grid.options['rowData']) == 2

def test_file_picker_double_click(tmp_path):
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    file1 = tmp_path / "file1.txt"
    file1.touch()

    picker = LocalFilePicker(directory=str(tmp_path))
    picker.grid = MagicMock()
    picker.grid.options = {}
    picker.submit = MagicMock()
    
    e = MagicMock()
    e.args = {'data': {'path': str(dir1)}}
    picker.handle_double_click(e)
    assert str(picker.path) == str(dir1)
    
    e.args = {'data': {'path': str(file1)}}
    picker.handle_double_click(e)
    picker.submit.assert_called_once_with([str(file1)])

@pytest.mark.asyncio
async def test_file_picker_handle_ok(tmp_path):
    picker = LocalFilePicker(directory=str(tmp_path))
    picker.grid = MagicMock()
    picker.grid.options = {}
    picker.submit = MagicMock()
    
    async def mock_get_rows(): return [{'path': 'file1.txt'}]
    picker.grid.get_selected_rows = mock_get_rows
    await picker._handle_ok()
    picker.submit.assert_called_with(['file1.txt'])
    
    picker.dirs_only = True
    picker.submit.reset_mock()
    async def mock_get_rows_empty(): return []
    picker.grid.get_selected_rows = mock_get_rows_empty
    await picker._handle_ok()
    picker.submit.assert_called_with([str(picker.path)])
    
    # Test TimeoutError
    picker.dirs_only = False
    picker.submit.reset_mock()
    async def mock_timeout(): raise TimeoutError()
    picker.grid.get_selected_rows = mock_timeout
    
    with patch.object(mock_nicegui.ui, 'notify') as mock_notify:
        await picker._handle_ok()
        mock_notify.assert_called_with('No file selected.')
        picker.submit.assert_not_called()

def test_file_picker_update_drive(tmp_path):
    picker = LocalFilePicker(directory=str(tmp_path))
    picker.grid = MagicMock()
    picker.drives_toggle = MagicMock()
    picker.drives_toggle.value = str(tmp_path)
    picker.update_grid = MagicMock()
    picker.update_drive()
    picker.update_grid.assert_called_once()
    assert str(picker.path) == str(tmp_path)
