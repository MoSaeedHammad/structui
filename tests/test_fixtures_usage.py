import os
import pytest
from structui.schema import SchemaManager
from structui.state import AppState

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')

def test_complex_fixture_loading():
    schema_path = os.path.join(FIXTURES_DIR, 'complex_schema.yaml')
    data_path = os.path.join(FIXTURES_DIR, 'data', 'complex_data.yaml')

    # Load schema
    schema_manager = SchemaManager(schema_filepath=schema_path)

    # Assert schema metadata is loaded correctly
    assert schema_manager.get_meta('network_config').get('type') == 'dict'
    assert schema_manager.get_meta('interfaces').get('list_item_types') == ['ethernet', 'vlan', 'loopback']

    # Load app state
    app_state = AppState(data_dir=os.path.join(FIXTURES_DIR, 'data'), schema_manager=schema_manager)
    app_state.load_files()

    # The data loaded should contain the network config
    data = app_state.config_data.get('complex_data.yaml')
    assert data is not None
    assert 'network_config' in data

    # Test some paths
    assert data['network_config']['hostname'] == 'test-server-01'
    assert len(data['network_config']['interfaces']) == 3

def test_complex_fixture_operations(tmp_path):
    import shutil
    schema_path = os.path.join(FIXTURES_DIR, 'complex_schema.yaml')
    schema_manager = SchemaManager(schema_filepath=schema_path)

    # Copy data to tmp_path to avoid modifying tracked files
    data_dir = os.path.join(FIXTURES_DIR, 'data')
    for f in os.listdir(data_dir):
        shutil.copy(os.path.join(data_dir, f), tmp_path)

    app_state = AppState(data_dir=str(tmp_path), schema_manager=schema_manager)
    app_state.load_files()

    # Get data by path
    data_node = app_state.get_data_by_path('root/complex_data.yaml/network_config/interfaces/0/ethernet/name')
    assert data_node == 'eth0'

    # Modify data
    app_state.set_data_by_path('root/complex_data.yaml/network_config/interfaces/0/ethernet', 'name', 'eth1')
    app_state.commit()

    modified_node = app_state.get_data_by_path('root/complex_data.yaml/network_config/interfaces/0/ethernet/name')
    assert modified_node == 'eth1'
    assert app_state.is_dirty is True

    # Undo
    app_state.undo()
    assert app_state.get_data_by_path('root/complex_data.yaml/network_config/interfaces/0/ethernet/name') == 'eth0'
