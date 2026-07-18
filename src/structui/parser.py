import os
import yaml  # type: ignore
import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .xml_parser import load_xml, save_xml

class HexInt(int):
    """Subclass of int to preserve hex formatting in YAML and UI representation."""
    def __str__(self) -> str:
        if self < 0:
            return f"0x{(self & 0xffffffffffffffff):x}"
        return f"0x{self:x}"
        
    def __repr__(self) -> str:
        return self.__str__()

def custom_int_constructor(loader, node):
    val_str = loader.construct_scalar(node)
    val = loader.construct_yaml_int(node)
    if '0x' in val_str or '0X' in val_str or '0x' in val_str.lower():
        return HexInt(val)
    return val

def hex_int_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:int', str(data))

class _StructUILoader(yaml.SafeLoader):
    """Scoped loader so HexInt parsing doesn't leak into other yaml.safe_load() callers in the process."""

class _StructUIDumper(yaml.Dumper):
    """Scoped dumper so HexInt formatting doesn't leak into other yaml.dump() callers in the process."""

_StructUILoader.add_constructor('tag:yaml.org,2002:int', custom_int_constructor)
_StructUIDumper.add_representer(HexInt, hex_int_representer)

class DataParser(ABC):
    """Abstract base class for format-agnostic configuration parsing."""
    
    @abstractmethod
    def load(self, filepath: str, schema: Optional[Dict[str, Any]] = None) -> Any:
        pass
        
    @abstractmethod
    def save(self, filepath: str, data: Any):
        pass

class YamlParser(DataParser):
    def load(self, filepath: str, schema: Optional[Dict[str, Any]] = None) -> Any:
        try:
            with open(filepath, 'r') as f:
                return yaml.load(f, Loader=_StructUILoader)
        except Exception as e:
            print(f"YAML Load Error ({filepath}): {e}")
            return None

    def save(self, filepath: str, data: Any):
        with open(filepath, 'w') as f:
            yaml.dump(data, f, Dumper=_StructUIDumper, default_flow_style=False, sort_keys=False)

class JsonParser(DataParser):
    def load(self, filepath: str, schema: Optional[Dict[str, Any]] = None) -> Any:
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"JSON Load Error ({filepath}): {e}")
            return None
            
    def save(self, filepath: str, data: Any):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

class XmlParser(DataParser):
    def load(self, filepath: str, schema: Optional[Dict[str, Any]] = None) -> Any:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return load_xml(content, schema)
        except ET.ParseError as e:
            raise ET.ParseError(f"Malformed XML in {os.path.basename(filepath)}: {str(e)}")
            
    def save(self, filepath: str, data: Any):
        save_xml(data, filepath)

def get_parser(filepath: str) -> DataParser:
    """Factory method to resolve the correct parser by file extension."""
    if filepath.endswith(('.yaml', '.yml')):
        return YamlParser()
    elif filepath.endswith('.json'):
        return JsonParser()
    elif filepath.endswith('.xml'):
        return XmlParser()
    return YamlParser()
