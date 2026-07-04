import pytest
from unittest.mock import MagicMock
from structui.schema import SchemaManager
from structui.state import AppState

def test_complex_schema_integration(tmp_path):
    schema_manager = SchemaManager("tests/fixtures/complex_schema.yaml")
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    app_state = AppState(str(data_dir), schema_manager)
    app_state.config_data = {
        "network.yaml": {
            "ecu_list": [
                {"id": "ECU_1", "active": True, "timeout": 100},
                {"id": "ECU_2", "active": False, "timeout": 200}
            ]
        },
        "diagnostics.yaml": {
            "mode": "normal",
            "errors": ["E_SYS", "E_NET"]
        }
    }

    # Test valid retrieval
    ecu_node = app_state.get_data_by_path("root/network.yaml/ecu_list/0")
    assert ecu_node["id"] == "ECU_1"

    # Test schema metadata for deeply nested node
    schema_key = schema_manager.get_schema_key_for_path("root/network.yaml/ecu_list/0", app_state.config_data)
    assert schema_key == "ecu"
    meta = schema_manager.get_meta(schema_key)
    assert "id" in meta.get("allowed_children")

def test_polymorphic_list_integration(tmp_path):
    schema_manager = SchemaManager("tests/fixtures/polymorphic_list.yaml")
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    app_state = AppState(str(data_dir), schema_manager)
    app_state.config_data = {
        "vehicles.yaml": [
            {"make": "Ford", "model": "Mustang", "doors": 2},
            {"make": "Volvo", "payload": 15000, "is_electric": True},
            {"make": "Honda", "cc": 600}
        ]
    }

    # Check type resolution of list items based on available properties
    # Car
    car_key = schema_manager.get_schema_key_for_path("root/vehicles.yaml/0", app_state.config_data)
    assert car_key == "car"

    # Truck
    truck_key = schema_manager.get_schema_key_for_path("root/vehicles.yaml/1", app_state.config_data)
    assert truck_key == "truck"

    # Motorcycle
    moto_key = schema_manager.get_schema_key_for_path("root/vehicles.yaml/2", app_state.config_data)
    assert moto_key == "motorcycle"

def test_strict_types_integration(tmp_path):
    schema_manager = SchemaManager("tests/fixtures/strict_types.yaml")
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    app_state = AppState(str(data_dir), schema_manager)
    app_state.config_data = {
        "config.yaml": {
            "my_bool": True,
            "my_int": 42,
            "my_float": 3.14,
            "my_string": "test",
            "my_enum": "opt1"
        }
    }

    # Test updating values
    app_state.set_data_by_path("root/config.yaml", "my_int", 100)
    assert app_state.get_data_by_path("root/config.yaml/my_int") == 100

    app_state.set_data_by_path("root/config.yaml", "my_bool", False)
    assert app_state.get_data_by_path("root/config.yaml/my_bool") == False
