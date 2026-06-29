import pytest
from unittest.mock import patch, MagicMock
from structui.schema import SchemaManager
from structui.state import AppState
from structui.ui import StructUI
import copy

def test_complex_schema_prefill():
    sm = SchemaManager("tests/fixtures/complex_schema.yaml")

    # Cascade and fill all required nested properties
    prefilled = sm.prefill_required("root")

    # root is not required and has no required children technically
    # Wait, the prefill_required starts from the key. If we prefill root, what happens?
    # Actually root doesn't have required: true. But if we ask to prefill it, it looks for allowed_children that have required: true
    # wait prefill_required checks if sm.get_meta(child_key).get("required", False) is True.
    # app_config is required: true
    assert "app_config" in prefilled
    assert isinstance(prefilled["app_config"], dict)

    # name, version, environment are required children of app_config
    assert "name" in prefilled["app_config"]
    assert "version" in prefilled["app_config"]
    assert "environment" in prefilled["app_config"]
    assert prefilled["app_config"]["name"] == ""
    assert prefilled["app_config"]["version"] == 0

    # debugging is not required
    assert "debugging" not in prefilled["app_config"]

def test_complex_app_state(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create initial file
    file1 = data_dir / "network.yaml"
    file1.write_text("""
interfaces:
  - if_name: eth0
    mac_address: 00:11:22:33:44:55
    speed: 1000
  - if_name: wlan0
    ssid: MyWiFi
    security: WPA2
""", encoding="utf-8")

    sm = SchemaManager("tests/fixtures/complex_schema.yaml")
    state = AppState(str(data_dir), sm)

    # Get polymorphic list items
    interfaces = state.get_data_by_path("root/network.yaml/interfaces")
    assert len(interfaces) == 2

    eth0 = state.get_data_by_path("root/network.yaml/interfaces/0")
    assert eth0["if_name"] == "eth0"

    wlan0 = state.get_data_by_path("root/network.yaml/interfaces/1")
    assert wlan0["ssid"] == "MyWiFi"

    # Track history accurately for nested modifications
    state.set_data_by_path("root/network.yaml/interfaces/1", "ssid", "NewWiFi")
    state.commit()

    assert state.get_data_by_path("root/network.yaml/interfaces/1/ssid") == "NewWiFi"

    state.undo()
    assert state.get_data_by_path("root/network.yaml/interfaces/1/ssid") == "MyWiFi"

def test_complex_ui_rendering():
    # Tests the UI component's build_tree_nodes logic
    sm = SchemaManager("tests/fixtures/complex_schema.yaml")
    state = MagicMock()
    state.data_dir = "/mock/dir"
    state.config_data = {
        "network.yaml": {
            "interfaces": [
                {"if_name": "eth0", "speed": 1000},
                {"if_name": "wlan0", "ssid": "MyWiFi"}
            ]
        }
    }

    def get_data_mock(path):
        if path == "root":
            return state.config_data
        parts = path.split("/")
        curr = state.config_data
        for p in parts[1:]:
            if isinstance(curr, dict) and p in curr:
                curr = curr[p]
            elif isinstance(curr, list) and p.isdigit() and int(p) < len(curr):
                curr = curr[int(p)]
            else:
                return None
        return curr

    state.get_data_by_path.side_effect = get_data_mock

    ui_inst = StructUI(state, sm)

    # build_tree_nodes takes (data, path)
    root_node = ui_inst.build_tree_nodes(state.config_data, "root")

    assert root_node["id"] == "root"

    # Check children of root
    root_children = root_node.get("children", [])
    assert len(root_children) == 1

    network_node = root_children[0]
    assert network_node["id"] == "root/network.yaml"

    # Check children of network.yaml (interfaces)
    network_children = network_node.get("children", [])
    assert len(network_children) == 1
    interfaces_node = network_children[0]
    assert interfaces_node["id"] == "root/network.yaml/interfaces"

    # Check children of interfaces (eth0, wlan0)
    list_items = interfaces_node.get("children", [])
    assert len(list_items) == 2
    assert list_items[0]["id"] == "root/network.yaml/interfaces/0"
    assert list_items[0]["label"] == "eth0"

    assert list_items[1]["id"] == "root/network.yaml/interfaces/1"
    assert list_items[1]["label"] == "wlan0"
