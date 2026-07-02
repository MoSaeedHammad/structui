import os
import pytest
from structui.schema import SchemaManager

@pytest.fixture
def mock_schema_file():
    schema_path = os.path.join(os.path.dirname(__file__), "fixtures", "complex_schema.yaml")
    return schema_path

def test_schema_manager_init(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    assert sm.schema_filepath == mock_schema_file
    assert "container_A" in sm.schema_meta

def test_schema_manager_missing_file(capsys):
    sm = SchemaManager("nonexistent.yaml")
    assert sm.schema_meta == {}
    captured = capsys.readouterr()
    assert "not found" in captured.out

def test_get_meta(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    assert sm.get_meta("container_A").get("type") == "dict"
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
    prefilled = sm.prefill_required("container_A")
    # string_prop is required
    assert "string_prop" in prefilled
    assert "number_prop" not in prefilled # not required
    assert prefilled["string_prop"] == ""  # default string
    assert "child_list" not in prefilled # not required
    assert "nested_dict" not in prefilled # not required

def test_get_schema_key_for_path(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    root_data = {
        "container_A.yaml": {
            "string_prop": "hello",
            "number_prop": 42,
            "child_list": [
                {"id": "item1", "flag": True},
                {"name": "item2", "value": 100}
            ],
            "nested_dict": {
                "inner_string": "inner"
            }
        }
    }
    
    assert sm.get_schema_key_for_path("root", root_data) == "root"
    assert sm.get_schema_key_for_path("root/container_A.yaml", root_data) == "container_A"
    assert sm.get_schema_key_for_path("root/container_A.yaml/string_prop", root_data) == "string_prop"
    
    # Missing/invalid paths
    assert sm.get_schema_key_for_path("root/container_A.yaml/child_list/99", root_data) == "list_item_1" # default to first list type when out of bounds and missing data
    assert sm.get_schema_key_for_path("root/container_A.yaml/unknown", root_data) == "unknown"

def test_get_schema_key_for_path_list_item_types(mock_schema_file):
    sm = SchemaManager(mock_schema_file)

    root_data = {
        "container_A.yaml": {
            "child_list": [
                {"id": "item1", "flag": True},
                {"name": "item2", "value": 100}
            ]
        }
    }
    
    assert sm.get_schema_key_for_path("root/container_A.yaml/child_list", root_data) == "child_list"
    assert sm.get_schema_key_for_path("root/container_A.yaml/child_list/0", root_data) == "list_item_1"
    assert sm.get_schema_key_for_path("root/container_A.yaml/child_list/1", root_data) == "list_item_2"

def test_get_label_key_for_schema(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    assert sm.get_label_key_for_schema("list_item_1") == "id"
    assert sm.get_label_key_for_schema("list_item_2") == "name"
    assert not sm.get_label_key_for_schema("container_A")
    
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

    root_data = {
        "container_A.yaml": {
            "child_list": [
                {"id": "TestName", "flag": True},
            ]
        }
    }
    
    # label_key from schema
    assert sm.get_item_label({"id": "TestName"}, "root/container_A.yaml/child_list/0", root_data, "default") == "TestName"
    
    # fallback to 'name'
    assert sm.get_item_label({"some_name": "FallbackName"}, "root/unknown", root_data, "default") == "FallbackName"
    
    # fallback to first string
    assert sm.get_item_label({"val1": 10, "val2": "FirstStr"}, "root/unknown", root_data, "default") == "FirstStr"
    
    # fallback to default
    assert sm.get_item_label({"val1": 10}, "root/unknown", root_data, "default") == "default"
    
    # fallback to default if not dict
def test_schema_manager_recursive(tmp_path, capsys):
    schema_path = tmp_path / "recursive.yaml"
    # To trigger recursion in prefill_required, the child must be required
    schema_path.write_text("""
item1:
  type: dict
  allowed_children: [item1]
  required: true
    """, encoding="utf-8")
    sm = SchemaManager(str(schema_path))
    # We call to trigger recursion
    sm.prefill_required("item1")
    captured = capsys.readouterr()
    assert "recursive schema detected" in captured.out
from structui.schema import SchemaManager

def test_schema_missing():
    sm = SchemaManager("tests/test_data/non_existent.yaml")
    assert sm.get_meta("some_key") == {}

def test_schema_path_type(tmp_path):
    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text("some_file: {type: file}", encoding="utf-8")
    sm = SchemaManager(str(schema_file))
    assert sm.get_meta("some_file").get("type") == "path"

def test_schema_types(tmp_path):
    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text("""
some_cont: {type: container}
some_dict: {type: dict}
some_int: {type: integer}
some_float: {type: float}
some_num: {type: number}
some_path: {type: path}
some_file2: {type: file}
some_bool: {type: bool}
some_boolean: {type: boolean}
some_list: {type: list}
some_str: {type: string}
""", encoding="utf-8")
    sm = SchemaManager(str(schema_file))
    assert sm.get_meta("some_cont").get("type") == "dict"
    assert sm.get_meta("some_dict").get("type") == "dict"
    assert sm.get_meta("some_int").get("type") == "number"
    assert sm.get_meta("some_float").get("type") == "number"
    assert sm.get_meta("some_num").get("type") == "number"
    assert sm.get_meta("some_path").get("type") == "path"
    assert sm.get_meta("some_file2").get("type") == "path"
    assert sm.get_meta("some_bool").get("type") == "boolean"
    assert sm.get_meta("some_boolean").get("type") == "boolean"
    assert sm.get_meta("some_list").get("type") == "list"
    assert sm.get_meta("some_str").get("type") == "string"

def test_get_schema_key_for_path_list_item_types_fallback(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["list"] = {
        "type": "list",
        "list_item_types": ["type_a", "type_b"]
    }
    sm.schema_meta["type_a"] = {"allowed_children": ["prop_a"]}
    sm.schema_meta["type_b"] = {"allowed_children": ["prop_b"]}

    # Not a dict
    root_data = {
        "list.yaml": [
            "not a dict"
        ]
    }

    assert sm.get_schema_key_for_path("root/list.yaml/0", root_data) == "type_a" # fallback to first item

def test_get_label_key_for_schema_invalid(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    assert sm.get_label_key_for_schema(None) == ""
    assert sm.get_label_key_for_schema("nonexistent_schema_key") == ""

def test_get_schema_key_for_path_list_item_type_no_types(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["list"] = {
        "type": "list",
        "list_item_type": "type_a" # Not list_item_types
    }

    root_data = {
        "list.yaml": [
            {"prop_a": 1}
        ]
    }

    assert sm.get_schema_key_for_path("root/list.yaml/0", root_data) == "type_a"

def test_get_label_key_for_schema_allowed_children_is_label(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["special_label"]
    }
    sm.schema_meta["special_label"] = {
        "is_label": True
    }
    assert sm.get_label_key_for_schema("special_dict") == "special_label"

def test_get_label_key_for_schema_allowed_children_not_in_meta(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["missing_child"]
    }
    # missing_child is not in schema_meta, so it will return ''
    assert sm.get_label_key_for_schema("special_dict") == ""

def test_get_label_key_for_schema_allowed_children_is_label_false(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["false_child"]
    }
    sm.schema_meta["false_child"] = {
        "is_label": False
    }
    # missing_child is not in schema_meta, so it will return ''
    assert sm.get_label_key_for_schema("special_dict") == ""

def test_get_label_key_for_schema_invalid_schema_key(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    assert sm.get_label_key_for_schema("") == ""
    assert sm.get_label_key_for_schema(None) == ""

def test_get_label_key_for_schema_allowed_children_not_dict(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["special_child"]
    }
    sm.schema_meta["special_child"] = "not_a_dict"
    assert sm.get_label_key_for_schema("special_dict") == ""

def test_get_label_key_for_schema_allowed_children_is_label_not_hit(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["special_child_1", "special_child_2"]
    }
    sm.schema_meta["special_child_1"] = {
        "is_label": False
    }
    sm.schema_meta["special_child_2"] = {
        "is_label": False
    }
    # neither is true, falls through loop
    assert sm.get_label_key_for_schema("special_dict") == ""

def test_get_label_key_for_schema_allowed_children_is_label_not_in_meta(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["special_child_1", "special_child_2"]
    }
    # missing entirely
    assert sm.get_label_key_for_schema("special_dict") == ""

def test_get_label_key_for_schema_allowed_children_is_label_not_hit2(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": "not_a_list"
    }
    assert sm.get_label_key_for_schema("special_dict") == ""

def test_get_label_key_for_schema_allowed_children_is_label_not_hit3(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["special_child_1", "special_child_2"]
    }
    sm.schema_meta["special_child_1"] = {
        "not_is_label": False
    }
    sm.schema_meta["special_child_2"] = {
        "not_is_label": False
    }
    # neither has is_label key, falls through loop
    assert sm.get_label_key_for_schema("special_dict") == ""

def test_get_label_key_for_schema_allowed_children_is_label_not_hit4(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["special_child_1", "special_child_2"]
    }
    sm.schema_meta["special_child_1"] = {
        "is_label": False
    }
    sm.schema_meta["special_child_2"] = {
        "is_label": True
    }
    assert sm.get_label_key_for_schema("special_dict") == "special_child_2"

def test_get_label_key_for_schema_allowed_children_is_label_not_hit5(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": []
    }
    assert sm.get_label_key_for_schema("special_dict") == ""

def test_get_label_key_for_schema_allowed_children_is_label_not_hit6(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["special_child_1", "special_child_2"]
    }
    sm.schema_meta["special_child_1"] = "not_a_dict"
    sm.schema_meta["special_child_2"] = {
        "is_label": False
    }
    assert sm.get_label_key_for_schema("special_dict") == ""

def test_get_label_key_for_schema_allowed_children_is_label_not_hit7(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["special_child_1"]
    }
    sm.schema_meta["special_child_1"] = "not_a_dict"
    assert sm.get_label_key_for_schema("special_dict") == ""

def test_get_label_key_for_schema_allowed_children_is_label_not_hit8(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "allowed_children": ["special_child_1"]
    }
    sm.schema_meta["special_child_1"] = {
        "is_label": True
    }
    assert sm.get_label_key_for_schema("special_dict") == "special_child_1"

def test_get_label_key_for_schema_has_label_key(mock_schema_file):
    sm = SchemaManager(mock_schema_file)
    sm.schema_meta["special_dict"] = {
        "label_key": "my_custom_label"
    }
    assert sm.get_label_key_for_schema("special_dict") == "my_custom_label"
