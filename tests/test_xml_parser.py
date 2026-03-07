import pytest
from xml.etree.ElementTree import ParseError
from structui.xml_parser import load_xml, dict_to_xml, save_xml

def test_load_xml_basic():
    # T004: Unit test for strictly well-formed XML parsing without lists
    xml_content = '''<?xml version="1.0"?>
    <config>
        <setting1>value1</setting1>
        <setting2 attr="test">value2</setting2>
        <parent>
            <child1>c1</child1>
            <child2>c2</child2>
        </parent>
    </config>
    '''
    expected = {
        "config": {
            "setting1": "value1",
            "setting2": {
                "@attr": "test",
                "#text": "value2"
            },
            "parent": {
                "child1": "c1",
                "child2": "c2"
            }
        }
    }
    assert load_xml(xml_content) == expected

def test_load_xml_with_schema_array():
    # T005: Unit test for XML parsing with single elements strictly mapped to single-item arrays based on schema
    xml_content = '''<?xml version="1.0"?>
    <config>
        <items>
            <item>1</item>
        </items>
    </config>
    '''
    # Mock schema mimicking structui generic structure (Cerberus/JSON Schema style)
    schema = {
        "config": {
            "type": "dict",
            "schema": {
                "items": {
                    "type": "dict",
                    "schema": {
                        "item": {
                            "type": "list"
                        }
                    }
                }
            }
        }
    }
    
    expected = {
        "config": {
            "items": {
                "item": ["1"]
            }
        }
    }
    assert load_xml(xml_content, schema=schema) == expected

def test_load_xml_malformed():
    # T006: Unit test for handling malformed XML elegantly
    xml_content = '''<?xml version="1.0"?><config><unclosed>'''
    with pytest.raises(ParseError):
        load_xml(xml_content)

def test_dict_to_xml_basic():
    # T012: Unit test for serializing unified dictionary back to XML strings
    data = {
        "config": {
            "setting1": "value1",
            "parent": {
                "child1": "c1"
            }
        }
    }
    expected_xml = "<config><setting1>value1</setting1><parent><child1>c1</child1></parent></config>"
    assert dict_to_xml(data) == expected_xml

def test_dict_to_xml_lists():
    # T013: Unit test for expanding Lists back to sibling tags during XML serialization
    data = {
        "config": {
            "items": {
                "item": ["1", "2"]
            }
        }
    }
    expected_xml = "<config><items><item>1</item><item>2</item></items></config>"
    assert dict_to_xml(data) == expected_xml

def test_dict_to_xml_attributes():
    # T014: Unit test for stripping `@` prefixes off dictionary keys and restoring them as XML properties
    # Mixed content with attributes
    data = {
        "config": {
            "setting2": {
                "@attr": "test",
                "#text": "value2"
            }
        }
    }
    expected_xml = '<config><setting2 attr="test">value2</setting2></config>'
    assert dict_to_xml(data) == expected_xml

