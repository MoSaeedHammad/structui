import os
import pytest
from structui.schema import SchemaManager

@pytest.fixture
def mock_schema_file(tmp_path):
    schema_path = tmp_path / "schema.yaml"
    schema_path.write_text("""
root:
  type: dict
  allowed_children: [item1, item2, list1, nested_dict]
item1:
  type: string
  required: true
item2:
  type: boolean
  required: false
list1:
  type: list
  list_item_type: list_item
list_item:
  type: dict
  allowed_children: [name, value]
  label_key: name
nested_dict:
  type: dict
  required: true
  allowed_children: [item1]
name:
  type: string
value:
  type: integer
config:
  type: dict
  allowed_children: [item1, list1]
    """, encoding="utf-8")
    return str(schema_path)

def test_schema_manager_init(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    assert sm.schema_filepath == mock_schema_file
    assert "root" in sm.schema_meta

def test_schema_manager_missing_file(capsys):
    sm = SchemaManager("nonexistent.yaml")
    assert sm.schema_meta == {}
    captured = capsys.readouterr()
    assert "not found" in captured.out

def test_get_meta(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    assert sm.get_meta("root").get("type") == "dict"
    assert sm.get_meta("unknown") == {}

def test_get_default_val_for_type(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    assert sm.get_default_val_for_type("boolean") is False
    assert sm.get_default_val_for_type("integer") == 0
    assert sm.get_default_val_for_type("number") == 0
    assert sm.get_default_val_for_type("float") == 0
    assert sm.get_default_val_for_type("dict") == {}
    assert sm.get_default_val_for_type("container") == {}
    assert sm.get_default_val_for_type("list") == []
    assert sm.get_default_val_for_type("string") == ""

def test_prefill_required(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    prefilled = sm.prefill_required("root")
    # item1 and nested_dict are required, item2 is not
    assert "item1" in prefilled
    assert "item2" not in prefilled
    assert prefilled["item1"] == ""  # default string
    assert "nested_dict" in prefilled
    assert isinstance(prefilled["nested_dict"], dict)
    assert prefilled["nested_dict"].get("item1") == "" # Recurses into nested dict
    assert "list1" not in prefilled # not required

def test_get_schema_key_for_path(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    root_data = {
        "config.yaml": {
            "item1": "test",
            "list1": [
                {"name": "test_item", "value": 10}
            ]
        }
    }
    
    assert sm.get_schema_key_for_path("root", root_data) == "root"
    assert sm.get_schema_key_for_path("root/config.yaml", root_data) == "config"
    assert sm.get_schema_key_for_path("root/config.yaml/item1", root_data) == "item1"
    
    # list item test
    assert sm.get_schema_key_for_path("root/config.yaml/list1/0", root_data) == "list_item"
    
    # Missing/invalid paths
    assert sm.get_schema_key_for_path("root/config.yaml/list1/99", root_data) == "list_item"
    assert sm.get_schema_key_for_path("root/config.yaml/unknown", root_data) == "unknown"

def test_get_schema_key_for_path_list_item_types(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["list"] = {
        "type": "list",
        "list_item_types": ["type_a", "type_b"]
    }
    sm.schema_meta["type_a"] = {"allowed_children": ["prop_a", "common"]}
    sm.schema_meta["type_b"] = {"allowed_children": ["prop_b", "long_prop", "common"]}
    root_data = {
        "list.yaml": [
            {"prop_a": 1, "common": 2},
            {"prop_b": 1, "long_prop": 2, "common": 3}
        ]
    }
    
    assert sm.get_schema_key_for_path("root/list.yaml", root_data) == "list"
    assert sm.get_schema_key_for_path("root/list.yaml/0", root_data) == "type_a"
    assert sm.get_schema_key_for_path("root/list.yaml/1", root_data) == "type_b"

def test_get_label_key_for_schema(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    assert sm.get_label_key_for_schema("list_item") == "name"
    assert sm.get_label_key_for_schema("root") is None
    
    # add an item with is_label
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["special_label"]
    }
    sm.schema_meta["special_label"] = {
        "is_label": True
    }
    assert sm.get_label_key_for_schema("special_dict") == "special_label"

def test_get_item_label(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    root_data = {}
    
    # label_key from schema
    assert sm.get_item_label({"name": "TestName"}, "root/list1/0", root_data, "default") == "TestName"
    
    # fallback to 'name'
    assert sm.get_item_label({"some_name": "FallbackName"}, "root/unknown", root_data, "default") == "FallbackName"
    
    # fallback to first string
    assert sm.get_item_label({"val1": 10, "val2": "FirstStr"}, "root/unknown", root_data, "default") == "FirstStr"
    
    # fallback to default
    assert sm.get_item_label({"val1": 10}, "root/unknown", root_data, "default") == "default"
    
    # fallback to default if not dict
    assert sm.get_item_label("string_item", "root/unknown", root_data, "default") == "default"
