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
    
    with patch('structui.file_picker.ui.notify') as mock_notify:
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

def test_file_picker_add_drives_toggle(tmp_path):
    with patch('platform.system', return_value='Windows'):
        with patch.dict('sys.modules', {'win32api': MagicMock(GetLogicalDriveStrings=lambda: 'C:\\\000D:\\\000')}):
            picker = LocalFilePicker(directory=str(tmp_path))
            assert hasattr(picker, 'drives_toggle')

def test_file_picker_allowed_extensions(tmp_path):
    (tmp_path / "file1.txt").touch()
    (tmp_path / "file2.yaml").touch()
    (tmp_path / "file3.YAML").touch()
    (tmp_path / "dir1").mkdir()

    picker = LocalFilePicker(directory=str(tmp_path), allowed_extensions=['.yaml'])
    picker.grid = MagicMock()
    picker.grid.options = {}
    picker.update_grid()

    names = [row['name'] for row in picker.grid.options['rowData']]
    # Should include dir1, file2.yaml, file3.YAML, and ..
    assert any('file2.yaml' in n for n in names)
    assert any('file3.YAML' in n for n in names)
    assert any('dir1' in n for n in names)
    assert not any('file1.txt' in n for n in names)

    picker2 = LocalFilePicker(directory=str(tmp_path), allowed_extensions=['txt'])
    picker2.grid = MagicMock()
    picker2.grid.options = {}
    picker2.update_grid()
    names = [row['name'] for row in picker2.grid.options['rowData']]
    assert any('file1.txt' in n for n in names)
    assert not any('file2.yaml' in n for n in names)
