import os
import pytest
from nicegui import ui
from structui.parser import YamlParser
from structui.schema import SchemaManager
from structui.state import AppState
from structui.ui import StructUI

def test_complex_fixtures_loading():
    schema_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'complex_schema.yaml')
    data_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'complex_data.yaml')

    assert os.path.exists(schema_path)
    assert os.path.exists(data_path)

    schema_manager = SchemaManager(schema_path)
    assert 'root' in schema_manager.schema_meta
    assert 'system_config' in schema_manager.schema_meta

    parser = YamlParser()
    data = parser.load(data_path)

    assert data is not None
    assert 'system_config' in data
    assert data['system_config']['hostname'] == 'primary-server-01'
    assert len(data['applications']) == 2

    # Test prefill required logic on a node
    prefilled = schema_manager.prefill_required('app_item')
    assert 'app_name' in prefilled
    assert prefilled['app_name'] == ''

    # Test getting item label
    label = schema_manager.get_item_label(data['applications'][0], 'root/applications/0', data, 'Default')
    assert label == 'web_gateway'

@pytest.mark.asyncio
async def test_complex_fixtures_headless_ui(tmp_path):
    schema_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'complex_schema.yaml')
    data_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'complex_data.yaml')

    sm = SchemaManager(schema_path)
    # AppState only takes data_dir and schema_manager
    state = AppState(str(tmp_path), schema_manager=sm)
    # Inject data into state for testing
    parser = YamlParser()
    data = parser.load(data_path)
    state.config_data = {'complex_data.yaml': data}
    state.commit()

    # Set up some dummy events
    class MockEvent:
        def __init__(self, value, sender=None):
            self.value = value
            self.sender = sender

    class MockSender:
        def __init__(self, value):
            self.value = value
            self.options = []

    # clear ui and build
    ui.clear()
    struct_ui = StructUI(state, sm)
    # We test building tree nodes as a headless ui build test
    nodes = struct_ui.build_tree_nodes(state.config_data)
    assert nodes is not None
    assert 'id' in nodes
    assert nodes['id'] == 'root'

    # verify state was loaded properly
    assert state.config_data['complex_data.yaml']['system_config']['hostname'] == 'primary-server-01'

    # Do a mock update via set_data_by_path
    state.set_data_by_path("root/complex_data.yaml/system_config", "hostname", "new-hostname")
    assert state.config_data['complex_data.yaml']['system_config']['hostname'] == 'new-hostname'

    # Do an add list item manual mock (as state doesn't have add_list_item)
    interfaces = state.get_data_by_path("root/complex_data.yaml/system_config/interfaces")
    new_item = sm.prefill_required('interface_item')
    interfaces.append(new_item)
    state.commit()

    # Verify a new item was added
    assert len(state.config_data['complex_data.yaml']['system_config']['interfaces']) == 3
    # Check that required fields were prefilled
    assert 'name' in state.config_data['complex_data.yaml']['system_config']['interfaces'][-1]
    assert state.config_data['complex_data.yaml']['system_config']['interfaces'][-1]['name'] == ''
