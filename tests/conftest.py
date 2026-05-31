import pytest
from unittest.mock import MagicMock
import sys

# Mock nicegui globally before any other imports
mock_nicegui = MagicMock()

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
    def open(self):
        pass

mock_nicegui.ui.dialog = MockDialog
sys.modules['nicegui'] = mock_nicegui
sys.modules['nicegui.events'] = MagicMock()

@pytest.fixture
def mock_app_state():
    mock = MagicMock()
    mock.data_dir = "/mock/dir"
    return mock

@pytest.fixture
def mock_schema_manager():
    mock = MagicMock()
    return mock
