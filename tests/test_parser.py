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

def test_hex_int_loading_and_saving(tmp_path):
    from structui.parser import HexInt, YamlParser
    parser = YamlParser()
    test_file = tmp_path / "hex_test.yaml"
    
    # Write a YAML with hex values
    test_file.write_text("hex_val: 0x1A\nnormal_val: 26\nneg_hex_val: -0x10\n", encoding="utf-8")
    
    loaded = parser.load(str(test_file))
    assert isinstance(loaded["hex_val"], HexInt)
    assert loaded["hex_val"] == 26
    assert isinstance(loaded["normal_val"], int)
    assert not isinstance(loaded["normal_val"], HexInt)
    assert loaded["normal_val"] == 26
    assert isinstance(loaded["neg_hex_val"], HexInt)
    assert loaded["neg_hex_val"] == -16
    
    # Now save it back
    out_file = tmp_path / "hex_out.yaml"
    parser.save(str(out_file), loaded)
    
    saved_content = out_file.read_text(encoding="utf-8")
    assert "hex_val: 0x1a" in saved_content or "hex_val: 0x1A" in saved_content
    assert "normal_val: 26" in saved_content
    assert "neg_hex_val: 0xfffffffffffffff0" in saved_content
from structui.parser import HexInt

def test_hexint_repr():
    h1 = HexInt(26)
    assert repr(h1) == "0x1a"
    h2 = HexInt(-16)
    assert repr(h2) == "0xfffffffffffffff0"
