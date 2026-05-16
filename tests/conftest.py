import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_app_state():
    mock = MagicMock()
    mock.data_dir = "/mock/dir"
    return mock

@pytest.fixture
def mock_schema_manager():
    mock = MagicMock()
    return mock
