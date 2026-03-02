import os
from typing import Dict, Any
from .parser import get_parser

class SchemaManager:
    """Handles schema metadata parsing, defaults resolution, and validation logic."""
    
    def __init__(self, schema_filepath: str):
        self.schema_filepath = schema_filepath
        self.schema_meta: Dict[str, Any] = {}
        self._load_schema()
        
    def _load_schema(self):
        if os.path.exists(self.schema_filepath):
            parser = get_parser(self.schema_filepath)
            loaded_schema = parser.load(self.schema_filepath)
            self.schema_meta = loaded_schema if loaded_schema is not None else {}
        else:
            print(f"Schema file {self.schema_filepath} not found. Using empty schema.")

    def get_meta(self, key: str) -> Dict[str, Any]:
        """Safely fetch metadata for a property key."""
        return self.schema_meta.get(key, {})

    def get_default_val_for_type(self, type_str: str) -> Any:
        """Returns a sensible default value based on the given schema type."""
        if type_str == 'boolean': return False
        if type_str in ['integer', 'number', 'float']: return 0
        if type_str in ['dict', 'container']: return {}
        if type_str == 'list': return []
        return ""

    def prefill_required(self, schema_key: str) -> Dict[str, Any]:
        """Scans the schema and creates a dictionary containing all REQUIRED child properties pre-filled."""
        new_val = {}
        allowed = self.get_meta(schema_key).get('allowed_children', [])
        for child_key in allowed:
            child_meta = self.get_meta(child_key)
            if child_meta.get('required', False):
                child_type = child_meta.get('type', 'string')
                if child_type in ['container', 'dict']:
                    new_val[child_key] = self.prefill_required(child_key)
                else:
                    new_val[child_key] = self.get_default_val_for_type(child_type)
        return new_val

    def get_schema_key_for_path(self, path: str, root_data: Any) -> str:
        """Resolves the active schema definition key for a data path location."""
        if path == "root":
            return "root"
        parts = path.split('/')[1:]
        current_schema_key = None
        curr_data = root_data
        
        for p in parts:
            if curr_data is not None:
                if isinstance(curr_data, list) and p.isdigit():
                    try: curr_data = curr_data[int(p)]
                    except IndexError: curr_data = None
                elif isinstance(curr_data, dict):
                    curr_data = curr_data.get(p)
                else:
                    curr_data = None

            if p.endswith(('.yaml', '.yml', '.json')):
                current_schema_key = os.path.splitext(p)[0]
            elif p.isdigit():
                if current_schema_key and current_schema_key in self.schema_meta:
                    meta = self.get_meta(current_schema_key)
                    if 'list_item_types' in meta:
                        best_match = None
                        max_overlap = -1
                        if isinstance(curr_data, dict):
                            for t in meta['list_item_types']:
                                allowed = set(self.get_meta(t).get('allowed_children', []))
                                overlap = len(allowed.intersection(curr_data.keys()))
                                if overlap > max_overlap:
                                    max_overlap = overlap
                                    best_match = t
                        current_schema_key = best_match if best_match else meta['list_item_types'][0]
                    else:
                        current_schema_key = meta.get('list_item_type', current_schema_key)
            else:
                current_schema_key = p
        return current_schema_key

    def get_label_key_for_schema(self, schema_key: str) -> str:
        """Finds which sub-property should be dynamically used as the naming label for UI containers."""
        if schema_key and schema_key in self.schema_meta:
            meta = self.get_meta(schema_key)
            if 'label_key' in meta:
                return meta['label_key']
            for child in meta.get('allowed_children', []):
                if child in self.schema_meta and self.schema_meta[child].get('is_label', False):
                    return child
        return None

    def get_item_label(self, item_data: Any, item_path: str, root_data: Any, default_label: str) -> str:
        """Agnostically determines the display label for an object via schema rules."""
        if not isinstance(item_data, dict):
            return default_label
            
        schema_key = self.get_schema_key_for_path(item_path, root_data)
        label_key = self.get_label_key_for_schema(schema_key)
        
        if label_key and label_key in item_data:
            return str(item_data[label_key])
            
        for k, v in item_data.items():
            if 'name' in str(k).lower() and isinstance(v, (str, int)):
                return str(v)
                
        for k, v in item_data.items():
            if isinstance(v, str):
                return v
                
        return default_label
