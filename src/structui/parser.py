import os
import yaml
import json
from abc import ABC, abstractmethod
from typing import Dict, Any

class DataParser(ABC):
    """Abstract base class for format-agnostic configuration parsing."""
    
    @abstractmethod
    def load(self, filepath: str) -> Any:
        pass
        
    @abstractmethod
    def save(self, filepath: str, data: Any):
        pass

class YamlParser(DataParser):
    def load(self, filepath: str) -> Any:
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
    def load(self, filepath: str) -> Any:
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"JSON Load Error ({filepath}): {e}")
            return None
            
    def save(self, filepath: str, data: Any):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

def get_parser(filepath: str) -> DataParser:
    """Factory method to resolve the correct parser by file extension."""
    if filepath.endswith(('.yaml', '.yml')):
        return YamlParser()
    elif filepath.endswith('.json'):
        return JsonParser()
    # Easily extensible to XML, CSV, etc.
    return YamlParser()
