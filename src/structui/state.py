import os
import glob
import copy
from typing import Dict, Any, List
from .schema import SchemaManager
from .parser import get_parser

class AppState:
    """Manages raw config data, memory states, transactions, and undo/redo stacks."""
    
    def __init__(self, data_dir: str, schema_manager: SchemaManager):
        self.data_dir = data_dir
        self.schema_manager = schema_manager
        
        self.config_data: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.history_index: int = -1
        self.is_dirty: bool = False
        
        self.load_files()
        
    def load_files(self):
        """Loads all supported formatting files in the source directory."""
        self.config_data = {}
        files = glob.glob(os.path.join(self.data_dir, "*.yaml")) + \
                glob.glob(os.path.join(self.data_dir, "*.yml")) + \
                glob.glob(os.path.join(self.data_dir, "*.json"))
                
        for filepath in files:
            filename = os.path.basename(filepath)
            if filename == os.path.basename(self.schema_manager.schema_filepath):
                continue
                
            parser = get_parser(filepath)
            data = parser.load(filepath)
            
            if data is None:
                # Fill structure based on declared schema
                schema_key = os.path.splitext(filename)[0]
                file_type = self.schema_manager.get_meta(schema_key).get('type', 'dict')
                data = [] if file_type == 'list' else {}
                
            self.config_data[filename] = data
            
        self.history = [copy.deepcopy(self.config_data)]
        self.history_index = 0
        self.is_dirty = False

    def commit(self):
        """Saves a memory snapshot into the history stack."""
        self.history = self.history[:self.history_index + 1]
        self.history.append(copy.deepcopy(self.config_data))
        
        if len(self.history) > 100:
            self.history.pop(0)
        else:
            self.history_index += 1
        self.is_dirty = True

    def undo(self) -> bool:
        """Reverts local modification to a previous epoch."""
        if self.history_index > 0:
            self.history_index -= 1
            self.config_data = copy.deepcopy(self.history[self.history_index])
            self.is_dirty = True
            return True
        return False

    def redo(self) -> bool:
        """Restores a previous undo."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.config_data = copy.deepcopy(self.history[self.history_index])
            self.is_dirty = True
            return True
        return False

    def get_data_by_path(self, path: str) -> Any:
        """Returns the local data node associated with the UI tree path string."""
        if path == "root":
            return self.config_data
            
        keys = path.split('/')[1:]
        curr = self.config_data
        
        try:
            for key in keys:
                if curr is None: return None
                if isinstance(curr, list): 
                    curr = curr[int(key)]
                elif isinstance(curr, dict): 
                    curr = curr.get(key)
                else: 
                    return None
            return curr
        except (IndexError, ValueError, KeyError, AttributeError):
            return None

    def set_data_by_path(self, path: str, property_key: str, new_value: Any):
        """Mutates a targeted property value on the underlying tree."""
        curr = self.get_data_by_path(path)
        if isinstance(curr, dict):
            curr[property_key] = new_value
        elif isinstance(curr, list):
            curr[int(property_key)] = new_value
        self.is_dirty = True

    def save_all_to_disk(self):
        """Dispatches save operations to agnostic parsers and handles raw deletion tracking."""
        schema_base = os.path.basename(self.schema_manager.schema_filepath)
        existing_logical_files = [
            f for f in os.listdir(self.data_dir) 
            if f.endswith(('.yaml', '.yml', '.json')) and f != schema_base
        ]
        
        for filename, data in self.config_data.items():
            filepath = os.path.join(self.data_dir, filename)
            try:
                parser = get_parser(filepath)
                parser.save(filepath, data)
            except Exception as e:
                print(f"Error saving {filename}: {e}")
                
        for f in existing_logical_files:
            if f not in self.config_data:
                try:
                    os.remove(os.path.join(self.data_dir, f))
                except Exception as e:
                    print(f"Error removing {f}: {e}")
                    
        self.is_dirty = False
