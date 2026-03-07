import os
import yaml
import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .xml_parser import load_xml, save_xml

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
                return yaml.safe_load(f)
        except Exception as e:
            print(f"YAML Load Error ({filepath}): {e}")
            return None
            
    def save(self, filepath: str, data: Any):
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

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
