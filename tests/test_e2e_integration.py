import os
import json
import pytest
from unittest.mock import patch

@pytest.fixture
def e2e_env(tmp_path):
    # Setup temporary directory structure for E2E
    schema_path = tmp_path / "schema.yaml"
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_path = config_dir / "app_config.json"

    # Write realistic schema
    schema_path.write_text("""
root:
  type: dict
  allowed_children: [app_config.json]
app_config.json:
  type: dict
  allowed_children: [server, database, features]
server:
  type: dict
  allowed_children: [port, host, enable_ssl]
port:
  type: integer
  required: true
host:
  type: string
  required: true
enable_ssl:
  type: boolean
database:
  type: dict
  allowed_children: [uri, timeout]
uri:
  type: string
  required: true
timeout:
  type: integer
features:
  type: list
  list_item_type: string
    """)

    # Write initial config
    initial_config = {
        "server": {
            "port": 8080,
            "host": "localhost",
            "enable_ssl": False
        },
        "database": {
            "uri": "postgres://user:pass@db:5432/main",
            "timeout": 30
        },
        "features": ["auth", "logging"]
    }
    config_path.write_text(json.dumps(initial_config))

    return {
        "dir": str(config_dir),
        "schema": str(schema_path),
        "config_file": str(config_path)
    }

def test_full_e2e_integration(e2e_env):
    # Important imports to verify real instantiation
    from structui.schema import SchemaManager
    from structui.state import AppState
    from structui.ui import StructUI

    # 1. Instantiate Core Components
    schema_manager = SchemaManager(e2e_env["schema"])
    app_state = AppState(e2e_env["dir"], schema_manager)

    # Verify initial load
    assert "app_config.json" in app_state.config_data
    assert app_state.config_data["app_config.json"]["server"]["port"] == 8080
    assert not app_state.is_dirty

    # 2. Simulate Headless UI Modifications
    from unittest.mock import MagicMock
    with patch("structui.ui.ui"):
        # UI Instantiation
        ui_editor = StructUI(app_state, schema_manager)
        ui_editor.editor_scroll_area = MagicMock()
        ui_editor.footer_pane = MagicMock()

        # Action 1: Modify deeply nested properties via State handler mechanism (this is how the UI does it)
        # The UI maps inputs to `set_data_by_path` internally, so we simulate that
        app_state.set_data_by_path("root/app_config.json/server", "port", 9090)
        app_state.set_data_by_path("root/app_config.json/server", "enable_ssl", True)
        app_state.set_data_by_path("root/app_config.json/database", "timeout", 60)

        # Action 2: Add an item to a list via the UI method
        ui_editor.handle_add_node("root/app_config.json", {
            "type": "list_item_append",
            "key": "features",
            "item_type": "string"
        })

        # Get index of newly added list item (which should be at index 2 since 2 existed previously)
        app_state.set_data_by_path("root/app_config.json/features", "2", "metrics")

        # Verify internal state changes
        assert app_state.is_dirty
        assert app_state.config_data["app_config.json"]["server"]["port"] == 9090
        assert app_state.config_data["app_config.json"]["server"]["enable_ssl"] is True
        assert app_state.config_data["app_config.json"]["database"]["timeout"] == 60
        assert "metrics" in app_state.config_data["app_config.json"]["features"]

        # Action 3: Trigger Save via direct method
        app_state.save_all_to_disk()

    # 3. Verify Persistence on Disk
    assert not app_state.is_dirty
    with open(e2e_env["config_file"], "r") as f:
        persisted_data = json.load(f)

    assert persisted_data["server"]["port"] == 9090
    assert persisted_data["server"]["enable_ssl"] is True
    assert persisted_data["database"]["timeout"] == 60
    assert "metrics" in persisted_data["features"]
    assert "auth" in persisted_data["features"]
