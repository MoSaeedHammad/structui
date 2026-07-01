import os
import pytest
from structui.schema import SchemaManager
from structui.state import AppState

@pytest.fixture
def complex_schema_manager():
    schema_path = os.path.join(os.path.dirname(__file__), "fixtures", "complex_schema.yaml")
    return SchemaManager(schema_path)

@pytest.fixture
def complex_app_state(tmp_path, complex_schema_manager):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    file1 = data_dir / "container_A.yaml"
    with open(os.path.join(os.path.dirname(__file__), "fixtures", "complex_data.yaml"), "r") as f:
        file1.write_text(f.read(), encoding="utf-8")

    return AppState(str(data_dir), complex_schema_manager)

def test_complex_prefill(complex_schema_manager):
    # Test that prefilling a complex dictionary generates required properties correctly
    prefilled = complex_schema_manager.prefill_required("container_A")
    assert "string_prop" in prefilled
    assert prefilled["string_prop"] == ""
    assert "number_prop" not in prefilled # not required
    assert "child_list" not in prefilled # not required

def test_complex_schema_resolution(complex_schema_manager):
    # Test resolving polymorphism and depth in paths
    root_data = {
        "container_A.yaml": {
            "child_list": [
                {"id": "test_id", "flag": True},
                {"name": "test_name", "value": 42}
            ],
            "nested_dict": {
                "inner_string": "test_inner"
            }
        }
    }

    assert complex_schema_manager.get_schema_key_for_path("root/container_A.yaml", root_data) == "container_A"
    assert complex_schema_manager.get_schema_key_for_path("root/container_A.yaml/child_list", root_data) == "child_list"
    assert complex_schema_manager.get_schema_key_for_path("root/container_A.yaml/child_list/0", root_data) == "list_item_1"
    assert complex_schema_manager.get_schema_key_for_path("root/container_A.yaml/child_list/1", root_data) == "list_item_2"
    assert complex_schema_manager.get_schema_key_for_path("root/container_A.yaml/nested_dict", root_data) == "nested_dict"
    assert complex_schema_manager.get_schema_key_for_path("root/container_A.yaml/nested_dict/inner_string", root_data) == "inner_string"

def test_complex_state_deep_access(complex_app_state):
    # Test reading deeply nested values from state
    val = complex_app_state.get_data_by_path("root/container_A.yaml/container_A/nested_dict/inner_string")
    assert val == "inner"

    # Test mutating deeply nested values
    complex_app_state.set_data_by_path("root/container_A.yaml/container_A/nested_dict", "inner_string", "new_inner")
    assert complex_app_state.get_data_by_path("root/container_A.yaml/container_A/nested_dict/inner_string") == "new_inner"

    # Check dirty tracking with deeply nested modifications
    complex_app_state.commit()
    assert complex_app_state.is_dirty

    # Test list item properties
    val = complex_app_state.get_data_by_path("root/container_A.yaml/container_A/child_list/1/value")
    assert val == 100

def test_complex_label_resolution(complex_schema_manager):
    root_data = {
        "container_A.yaml": {
            "child_list": [
                {"id": "item1", "flag": True},
                {"name": "item2", "value": 100}
            ]
        }
    }
    # Test resolving dynamic labels for polymorphic list items
    label1 = complex_schema_manager.get_item_label({"id": "item1", "flag": True}, "root/container_A.yaml/child_list/0", root_data, "default")
    assert label1 == "item1"

    label2 = complex_schema_manager.get_item_label({"name": "item2", "value": 100}, "root/container_A.yaml/child_list/1", root_data, "default")
    assert label2 == "item2"
