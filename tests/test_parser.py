import os
import pytest
import yaml
import json
from structui.parser import YamlParser, JsonParser, get_parser

def test_get_parser():
    assert isinstance(get_parser("config.yaml"), YamlParser)
    assert isinstance(get_parser("config.yml"), YamlParser)
    assert isinstance(get_parser("config.json"), JsonParser)
    assert isinstance(get_parser("config.unknown"), YamlParser)

def test_yaml_parser(tmp_path):
    parser = YamlParser()
    test_file = tmp_path / "test.yaml"
    data = {"key": "value", "list": [1, 2, 3]}
    
    # Test Save
    parser.save(str(test_file), data)
    assert test_file.exists()
    
    # Test Load
    loaded = parser.load(str(test_file))
    assert loaded == data

def test_yaml_parser_load_error(tmp_path, capsys):
    parser = YamlParser()
    test_file = tmp_path / "invalid.yaml"
    test_file.write_text("invalid: yaml: :", encoding="utf-8")
    
    loaded = parser.load(str(test_file))
    assert loaded is None
    captured = capsys.readouterr()
    assert "YAML Load Error" in captured.out

def test_json_parser(tmp_path):
    parser = JsonParser()
    test_file = tmp_path / "test.json"
    data = {"key": "value", "list": [1, 2, 3]}
    
    # Test Save
    parser.save(str(test_file), data)
    assert test_file.exists()
    
    # Test Load
    loaded = parser.load(str(test_file))
    assert loaded == data

def test_json_parser_load_error(tmp_path, capsys):
    parser = JsonParser()
    test_file = tmp_path / "invalid.json"
    test_file.write_text("{invalid json}", encoding="utf-8")
    
    loaded = parser.load(str(test_file))
    assert loaded is None
    captured = capsys.readouterr()
    assert "JSON Load Error" in captured.out

def test_xml_parser(tmp_path):
    parser = get_parser("config.xml")
    assert type(parser).__name__ == "XmlParser"
    test_file = tmp_path / "test.xml"
    data = {"config": {"key": "value"}}
    
    # Test Save
    parser.save(str(test_file), data)
    assert test_file.exists()
    
    # Test Load
    loaded = parser.load(str(test_file))
    assert loaded == data

def test_xml_parser_load_error(tmp_path):
    parser = get_parser("config.xml")
    test_file = tmp_path / "invalid.xml"
    test_file.write_text("<invalid><xml>", encoding="utf-8")
    
    with pytest.raises(Exception) as e:
        parser.load(str(test_file))
    assert "Malformed XML" in str(e.value)

def test_abstract_parser_coverage():
    from structui.parser import DataParser
    
    class DummyParser(DataParser):
        def load(self, filepath, schema=None):
            return super().load(filepath, schema)
        def save(self, filepath, data):
            return super().save(filepath, data)
            
    p = DummyParser()
    assert p.load("file.txt") is None
    assert p.save("file.txt", {}) is None
