import sys
from unittest.mock import MagicMock, patch

# Force mock nicegui BEFORE any other imports load it
mock_ui = MagicMock()
mock_app = MagicMock()
mock_nicegui = MagicMock(ui=mock_ui, app=mock_app)
sys.modules['nicegui'] = mock_nicegui
sys.modules['nicegui.events'] = MagicMock()

import pytest

@pytest.fixture
def mock_app_state():
    mock = MagicMock()
    mock.data_dir = "/mock/dir"
    return mock

@pytest.fixture
def mock_schema_manager():
    mock = MagicMock()
    return mock
