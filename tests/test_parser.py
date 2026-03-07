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
