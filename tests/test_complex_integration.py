import os
import shutil
from structui.schema import SchemaManager
from structui.state import AppState
from structui.parser import YamlParser

def test_complex_integration_flow(tmp_path):
    # Setup: copy data fixture to tmp_path
    fixtures_dir = os.path.join("tests", "fixtures")
    data_fixture = os.path.join(fixtures_dir, "data", "complex_data.yaml")
    schema_fixture = os.path.join(fixtures_dir, "complex_schema.yaml")

    tmp_data_file = tmp_path / "complex_data.yaml"
    shutil.copy(data_fixture, tmp_data_file)

    # Initialize Manager and State
    schema_manager = SchemaManager(schema_fixture)
    state = AppState(str(tmp_path), schema_manager)

    # Verify loaded data
    assert "complex_data.yaml" in state.config_data
    data = state.config_data["complex_data.yaml"]["data_item"]
    assert data["level1"]["level2"]["final_val"] == 100
    assert data["list_val"] == ["a", "b"]

    # Mutate data
    data["level1"]["level2"]["final_val"] = 200
    state.commit()
    state.save_all_to_disk()

    # Check written file
    parser = YamlParser()
    saved_data = parser.load(str(tmp_data_file))
    assert saved_data["data_item"]["level1"]["level2"]["final_val"] == 200