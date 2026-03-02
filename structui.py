import os
import glob
import yaml
import asyncio
import copy
from nicegui import ui

# ==========================================
# 1. SCHEMA DEFINITION & HELP TEXT METADATA
# ==========================================
def load_schema(filepath=".kashif_schema.yaml"):
    """Loads the schema definition from a separate YAML file."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading schema from {filepath}: {e}")
    else:
        print(f"Schema file {filepath} not found. Using empty schema.")
    return {}

SCHEMA_META = load_schema()

def get_default_val_for_type(type_str):
    """Returns a sensible default value based on the schema's type."""
    if type_str == 'boolean': return False
    if type_str in ['integer', 'number', 'float']: return 0
    if type_str in ['dict', 'container']: return {}
    if type_str == 'list': return []
    return ""

def prefill_required(schema_key):
    """Scans the schema and creates a dictionary containing all REQUIRED child properties pre-filled."""
    new_val = {}
    allowed = SCHEMA_META.get(schema_key, {}).get('allowed_children', [])
    for child_key in allowed:
        child_meta = SCHEMA_META.get(child_key, {})
        if child_meta.get('required', False):
            child_type = child_meta.get('type', 'string')
            if child_type in ['container', 'dict']:
                new_val[child_key] = prefill_required(child_key)
            else:
                new_val[child_key] = get_default_val_for_type(child_type)
    return new_val

def get_schema_key_for_path(path, root_data):
    """Resolves the schema key for a given path, handling polymorphic lists via list_item_types."""
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

        if p.endswith('.yaml') or p.endswith('.yml'):
            current_schema_key = os.path.splitext(p)[0]
        elif p.isdigit():
            if current_schema_key and current_schema_key in SCHEMA_META:
                meta = SCHEMA_META[current_schema_key]
                if 'list_item_types' in meta:
                    best_match = None
                    max_overlap = -1
                    if isinstance(curr_data, dict):
                        for t in meta['list_item_types']:
                            allowed = set(SCHEMA_META.get(t, {}).get('allowed_children', []))
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

def get_allowed_options(path, data_node, root_data):
    """Generates the 'Add' options dynamically based on Schema."""
    schema_key = get_schema_key_for_path(path, root_data)
            
    allowed_from_schema = []
    if schema_key and schema_key in SCHEMA_META:
        allowed_from_schema = SCHEMA_META[schema_key].get('allowed_children', [])
    
    allowed_options = []
    if isinstance(data_node, dict):
        for child in allowed_from_schema:
            if child not in data_node:
                allowed_options.append({'label': f"Add {child.replace('_', ' ').title()}", 'type': 'dict_key', 'key': child})
            else:
                child_meta = SCHEMA_META.get(child, {})
                if isinstance(data_node[child], list) and child_meta.get('type') in ['container', 'list']:
                    if 'list_item_types' in child_meta:
                        for item_type in child_meta['list_item_types']:
                            allowed_options.append({'label': f"Add New {item_type.replace('_', ' ').title()} to {child}", 'type': 'list_item_append', 'key': child, 'item_type': item_type})
                    else:
                        item_type = child_meta.get('list_item_type', child)
                        allowed_options.append({'label': f"Add New {item_type.replace('_', ' ').title()} to {child}", 'type': 'list_item_append', 'key': child, 'item_type': item_type})
        allowed_options.append({'label': "Add Custom File" if path == "root" else "Add Custom Key", 'type': 'custom_dict'})
        
    elif isinstance(data_node, list):
        if schema_key and schema_key in SCHEMA_META:
            meta = SCHEMA_META[schema_key]
            if 'list_item_types' in meta:
                for item_type in meta['list_item_types']:
                    allowed_options.append({'label': f"Add New {item_type.replace('_', ' ').title()}", 'type': 'list_item_typed', 'key': item_type})
            elif 'list_item_type' in meta:
                item_type = meta['list_item_type']
                allowed_options.append({'label': f"Add New {item_type.replace('_', ' ').upper()}", 'type': 'list_item_typed', 'key': item_type})
            else:
                allowed_options.append({'label': "Add New Item", 'type': 'list_item'})
        else:
            allowed_options.append({'label': "Add New Item", 'type': 'list_item'})
            
    return allowed_options

def get_all_node_ids(node):
    """Recursively grabs all node IDs to handle Expand All."""
    if not node: return []
    ids = [node['id']]
    for child in node.get('children', []):
        ids.extend(get_all_node_ids(child))
    return ids

# --- AGNOSTIC LABEL DETERMINATION HELPERS ---
def get_label_key_for_schema(schema_key):
    """Finds which property should be used as the display name for a container."""
    if schema_key and schema_key in SCHEMA_META:
        meta = SCHEMA_META[schema_key]
        if 'label_key' in meta:
            return meta['label_key']
        for child in meta.get('allowed_children', []):
            if child in SCHEMA_META and SCHEMA_META[child].get('is_label', False):
                return child
    return None

def get_item_label(item_data, item_path, root_data, default_label):
    """Agnostically determines the display label for a given object using the schema."""
    if not isinstance(item_data, dict):
        return default_label
        
    schema_key = get_schema_key_for_path(item_path, root_data)
    label_key = get_label_key_for_schema(schema_key)
    
    if label_key and label_key in item_data:
        return str(item_data[label_key])
        
    for k, v in item_data.items():
        if 'name' in str(k).lower() and isinstance(v, (str, int)):
            return str(v)
            
    for k, v in item_data.items():
        if isinstance(v, str):
            return v
            
    return default_label

# ==========================================
# 2. DATA LOADING & STATE MANAGEMENT
# ==========================================
class ConfigApp:
    def __init__(self):
        self.config_data = {}
        self.history = []
        self.history_index = -1
        self.load_yaml_files()
        
    def load_yaml_files(self):
        """Loads all .yml and .yaml files in the current directory."""
        self.config_data = {}
        yaml_files = glob.glob("*.yaml") + glob.glob("*.yml")
        for file in yaml_files:
            if file == ".kashif_schema.yaml":
                continue
            try:
                with open(file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data is None:
                        schema_key = os.path.splitext(file)[0]
                        file_type = SCHEMA_META.get(schema_key, {}).get('type', 'dict')
                        data = [] if file_type == 'list' else {}
                    self.config_data[file] = data
            except Exception as e:
                print(f"Error loading {file}: {e}")
                
        # Initialize History state
        self.history = [copy.deepcopy(self.config_data)]
        self.history_index = 0

    def commit(self):
        """Saves a snapshot of current data into the history stack for undo support."""
        # Truncate any 'redo' paths if a new edit is made from a past state
        self.history = self.history[:self.history_index + 1]
        
        self.history.append(copy.deepcopy(self.config_data))
        
        # Limit history stack memory footprint
        if len(self.history) > 100:
            self.history.pop(0)
        else:
            self.history_index += 1

    def undo(self):
        """Reverts the state to the previous history snapshot."""
        if self.history_index > 0:
            self.history_index -= 1
            self.config_data = copy.deepcopy(self.history[self.history_index])
            return True
        return False

    def redo(self):
        """Re-applies the previously reverted history snapshot."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.config_data = copy.deepcopy(self.history[self.history_index])
            return True
        return False

    def build_tree_nodes(self, data, path="root", name="Configurations"):
        """Recursively builds the tree structure for NiceGUI."""
        node = {'id': path, 'label': name}
        children = []
        
        node['allowed'] = get_allowed_options(path, data, self.config_data)
        
        # Determine if this container has primitive properties to edit
        has_prims = False
        
        if isinstance(data, dict):
            for k, v in data.items():
                if not isinstance(v, (dict, list)):
                    has_prims = True
                elif isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v):
                    if SCHEMA_META.get(str(k), {}).get('type') not in ['container', 'list']:
                        has_prims = True
                        
                if isinstance(v, (dict, list)):
                    if isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v):
                        if SCHEMA_META.get(str(k), {}).get('type') not in ['container', 'list']:
                            continue
                    children.append(self.build_tree_nodes(v, f"{path}/{k}", str(k)))
        elif isinstance(data, list):
            for i, v in enumerate(data):
                if isinstance(v, (dict, list)):
                    label = get_item_label(v, f"{path}/{i}", self.config_data, f"[{i}]")
                    children.append(self.build_tree_nodes(v, f"{path}/{i}", label))
                    
        # Apply visual distinctions based on content type
        if has_prims:
            node['icon'] = 'settings'
            node['color'] = 'blue-8'
        else:
            node['icon'] = 'folder'
            node['color'] = 'primary'
            
        if not children and not has_prims:
            node['icon'] = 'folder_open'
            node['color'] = 'grey-5'
                    
        if children:
            node['children'] = children
            
        return node

    def get_data_by_path(self, path):
        if path == "root":
            return self.config_data
            
        keys = path.split('/')[1:]
        curr = self.config_data
        
        try:
            for key in keys:
                if curr is None: return None
                if isinstance(curr, list): curr = curr[int(key)]
                elif isinstance(curr, dict): curr = curr.get(key)
                else: return None
            return curr
        except (IndexError, ValueError, KeyError, AttributeError):
            return None

    def set_data_by_path(self, path, property_key, new_value):
        curr = self.get_data_by_path(path)
        if isinstance(curr, dict):
            curr[property_key] = new_value
        elif isinstance(curr, list):
            curr[int(property_key)] = new_value

# ==========================================
# 3. UI GENERATION
# ==========================================
app_state = ConfigApp()

@ui.page('/')
def main_page():
    dark_mode = ui.dark_mode()
    
    ui.add_head_html('''
        <style>
            body.body--light { background-color: #f8fafc; }
            body.body--dark { background-color: #0f172a; }
            .q-tree__node-header { width: 100%; }
        </style>
    ''')
    
    selected_path = {"value": "root"}
    tree = None
    
    def refresh_tree_and_editor():
        """Refreshes everything and guarantees expansion states and selections are preserved."""
        if tree is not None:
            new_nodes = [app_state.build_tree_nodes(app_state.config_data)]
            curr_expanded = set(tree._props.get('expanded', []))
            
            if selected_path["value"]:
                parts = selected_path["value"].split('/')
                for i in range(1, len(parts) + 1):
                    curr_expanded.add("/".join(parts[:i]))
            
            tree._props['nodes'] = new_nodes
            tree._props['expanded'] = list(curr_expanded)
            
            if selected_path["value"]:
                tree._props['selected'] = selected_path["value"]
                
            tree.update()
            
        if not selected_path["value"]:
            selected_path["value"] = "root"
            
        draw_editor(selected_path["value"])

    def perform_add_action(path, opt):
        """Core logic to handle schema-based item additions."""
        data_node = app_state.get_data_by_path(path)
        
        def expand_node(target_path):
            if tree is not None:
                expanded = set(tree._props.get('expanded', []))
                parts = target_path.split('/')
                for i in range(1, len(parts) + 1):
                    expanded.add("/".join(parts[:i]))
                tree._props['expanded'] = list(expanded)
        
        if opt['type'] == 'dict_key':
            key = opt['key']
            schema_lookup_key = key.replace('.yaml', '').replace('.yml', '') if path == "root" else key
            schema_type = SCHEMA_META.get(schema_lookup_key, {}).get('type', 'string')
            
            if schema_type in ['container', 'dict']: data_node[key] = prefill_required(schema_lookup_key)
            elif schema_type == 'list': data_node[key] = []
            else: data_node[key] = get_default_val_for_type(schema_type)
                
            app_state.commit()
            ui.notify(f"Added {key}", type='positive')
            expand_node(path)
            refresh_tree_and_editor()
            
        elif opt['type'] == 'list_item_typed':
            item_type = opt['key']
            data_node.append(prefill_required(item_type))
            app_state.commit()
            ui.notify(f"Added new {item_type}", type='positive')
            expand_node(path)
            refresh_tree_and_editor()
            
        elif opt['type'] == 'list_item_append':
            list_key = opt['key']
            item_type = opt.get('item_type', list_key)
            data_node[list_key].append(prefill_required(item_type))
            app_state.commit()
            ui.notify(f"Added new {item_type} to {list_key}", type='positive')
            expand_node(f"{path}/{list_key}")
            refresh_tree_and_editor()
            
        elif opt['type'] == 'list_item':
            list_key = path.split('/')[-1]
            data_node.append(prefill_required(list_key))
            app_state.commit()
            ui.notify("Added new list item", type='positive')
            expand_node(path)
            refresh_tree_and_editor()
            
        elif opt['type'] == 'custom_dict':
            with ui.dialog() as dialog, ui.card().classes('dark:bg-slate-800'):
                is_root = (path == "root")
                ui.label("Add Custom File" if is_root else "Add Custom Key").classes('text-lg font-bold dark:text-white')
                new_key = ui.input('Filename (e.g. connections.yaml)' if is_root else 'Key Name').classes('w-full')
                new_type = ui.select({'str': 'String', 'int': 'Integer', 'bool': 'Boolean', 'dict': 'Container (Dict)', 'list': 'List'}, value='list' if is_root else 'str', label='Type').classes('w-full')
                
                def on_add():
                    k = new_key.value
                    if not k: return
                    if is_root and not (k.endswith('.yaml') or k.endswith('.yml')):
                        k += '.yaml'
                    if k in data_node: return
                    
                    t = new_type.value
                    if t == 'dict':
                        schema_lookup_key = k.replace('.yaml', '').replace('.yml', '') if is_root else k
                        data_node[k] = prefill_required(schema_lookup_key)
                    else: 
                        data_node[k] = get_default_val_for_type('string' if t=='str' else 'integer' if t=='int' else 'boolean' if t=='bool' else 'list')
                    
                    app_state.commit()
                    expand_node(path)
                    refresh_tree_and_editor()
                    dialog.close()
                    
                ui.button('Add', on_click=on_add).classes('w-full mt-4')
            dialog.open()

    def handle_tree_select(e):
        """Handles selection tracking and expands/collapses folders dynamically upon clicking."""
        if e.value is None:
            # Re-clicked existing node -> Toggle expansion only
            if selected_path["value"] and tree is not None:
                expanded = set(tree._props.get('expanded', []))
                if selected_path["value"] in expanded:
                    expanded.remove(selected_path["value"])
                else:
                    expanded.add(selected_path["value"])
                tree._props['expanded'] = list(expanded)
                tree._props['selected'] = selected_path["value"]
                tree.update()
            return
            
        # Clicked a new node -> Select and Toggle expansion
        selected_path["value"] = e.value
        if tree is not None:
            expanded = set(tree._props.get('expanded', []))
            if e.value in expanded:
                expanded.remove(e.value)
            else:
                expanded.add(e.value)
            tree._props['expanded'] = list(expanded)
            tree._props['selected'] = e.value
            tree.update()
            
        draw_editor(e.value)

    def update_footer(prop_key=None):
        footer_pane.clear()
        with footer_pane:
            if not prop_key:
                ui.label("Help & Metadata").classes('text-lg font-bold text-gray-700 dark:text-gray-300')
                ui.label("Select a property in the editor to see its description and type.").classes('text-gray-500 dark:text-gray-400 italic')
                return
                
            meta = SCHEMA_META.get(prop_key, {"type": "unknown", "desc": "No description available for this property."})
            with ui.row().classes('items-center gap-2 mb-2'):
                ui.icon('info', size='sm', color='primary')
                ui.label(prop_key).classes('text-lg font-bold text-blue-800 dark:text-blue-300 font-mono')
                ui.badge(meta.get('type', 'unknown'), color='blue-200').classes('text-blue-900 ml-2')
                
                is_req = meta.get('required', False)
                req_text = "Required" if is_req else "Optional"
                req_color = "red-100 text-red-800" if is_req else "green-100 text-green-800"
                ui.badge(req_text).classes(f'ml-2 {req_color} font-bold border border-current')
            ui.markdown(meta.get('desc', 'No description provided.')).classes('text-gray-700 dark:text-gray-300 text-md ml-8')
            
    def delete_item(node, key):
        """Robust bound function to handle property deletions without closure conflicts."""
        ui.notify('Property deleted', type='negative') # Fired before UI rebuilds
        if isinstance(node, dict):
            node.pop(key, None)
        elif isinstance(node, list):
            node.pop(key)
        app_state.commit()
        refresh_tree_and_editor()

    def draw_editor(path):
        if not path:
            path = "root"
            
        selected_path["value"] = path
        editor_scroll_area.clear()
        update_footer(None)

        data_node = app_state.get_data_by_path(path)
        if data_node is None:
            with editor_scroll_area:
                ui.label("This node no longer exists or was deleted.").classes('text-red-500 mt-10 text-lg font-bold')
            return 

        with editor_scroll_area:
            # --- 1. INTERACTIVE BREADCRUMBS ---
            parts = path.split('/')
            with ui.row().classes('items-center gap-2 mb-6 w-full flex-wrap'):
                current_path = []
                for i, p in enumerate(parts):
                    current_path.append(p)
                    full_path = "/".join(current_path)
                    
                    def make_breadcrumb_nav(nav_p=full_path):
                        return lambda e: (selected_path.update({"value": nav_p}), refresh_tree_and_editor())
                    
                    label_text = "Root" if p == "root" else p
                    ui.label(label_text).classes('text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 cursor-pointer font-bold text-lg hover:underline transition-all').on('click', make_breadcrumb_nav(full_path))
                    
                    if i < len(parts) - 1:
                        ui.icon('chevron_right', color='gray').classes('text-gray-400')
            
            # Action Row (Search, Locate & Delete parent)
            with ui.row().classes('w-full items-center justify-between mb-4 pb-2 border-b border-gray-200 dark:border-slate-700'):
                with ui.row().classes('items-center gap-2'):
                    prop_search = ui.input('Search properties...').classes('w-64').props('dense rounded outlined')
                    
                    async def locate_in_tree():
                        """Expands parents if collapsed, then scrolls the UI to the node."""
                        if tree is not None and selected_path["value"]:
                            expanded = set(tree._props.get('expanded', []))
                            parts = selected_path["value"].split('/')
                            # Force parent folders open
                            for i in range(1, len(parts)):
                                expanded.add("/".join(parts[:i]))
                            tree._props['expanded'] = list(expanded)
                            tree._props['selected'] = selected_path["value"]
                            tree.update()
                            
                        # SetTimeout ensures Vue paints the DOM expansions before attempting to search for the element
                        ui.run_javascript("setTimeout(() => { const el = document.querySelector('.q-tree__node--selected'); if(el) el.scrollIntoView({behavior: 'smooth', block: 'center'}); }, 300);")
                        ui.notify('Located in tree', color='blue')
                        
                    ui.button(icon='my_location', on_click=locate_in_tree).props('flat round').tooltip('Locate in Tree')
                
                if path != "root":
                    def delete_current_container():
                        ui.notify('Node deleted', type='negative') # MUST be fired before UI rebuilds to prevent slot deletion errors
                        parent_path = "/".join(path.split('/')[:-1])
                        node_key = path.split('/')[-1]
                        parent_node = app_state.get_data_by_path(parent_path)
                        
                        if isinstance(parent_node, dict): del parent_node[node_key]
                        elif isinstance(parent_node, list): parent_node.pop(int(node_key))
                            
                        app_state.commit()
                        selected_path["value"] = parent_path
                        refresh_tree_and_editor()

                    ui.button(icon='delete', color='red-500', on_click=delete_current_container).props('flat round').tooltip('Delete this entire container')
            
            # --- 2. PRIMITIVE PROPERTIES EDITOR ---
            props_container = ui.column().classes('w-full gap-4')
            
            def filter_properties(e):
                search_term = e.value.lower()
                for el in props_container.default_slot.children:
                    try:
                        prop_name = el.default_slot.children[1]._props.get('label', el.default_slot.children[1]._props.get('text', '')).lower()
                        if search_term in prop_name: el.classes(remove='hidden')
                        else: el.classes(add='hidden')
                    except Exception: pass 
            prop_search.on_value_change(filter_properties)
            
            def render_primitive_input(k, v):
                def make_on_change(prop_key=k):
                    def handler(e):
                        app_state.set_data_by_path(selected_path["value"], str(prop_key), e.value)
                        app_state.commit() # Save history snapshot
                        
                        # --- AGNOSTIC TREE LABEL AUTO-UPDATE ---
                        schema_key = get_schema_key_for_path(selected_path["value"], app_state.config_data)
                        label_key = get_label_key_for_schema(schema_key)
                        
                        is_label_update = False
                        if label_key:
                            is_label_update = (str(prop_key) == label_key)
                        else:
                            is_label_update = ('name' in str(prop_key).lower())
                            
                        if is_label_update and tree is not None:
                            curr_expanded = tree._props.get('expanded', [])
                            tree._props['nodes'] = [app_state.build_tree_nodes(app_state.config_data)]
                            tree._props['expanded'] = curr_expanded
                            tree.update()
                            
                    return handler
                    
                def make_on_focus(prop_key=k):
                    return lambda _: update_footer(str(prop_key))

                meta = SCHEMA_META.get(str(k), {})
                label_text = f"{k} *" if meta.get('required', False) else str(k)

                options = meta.get('options')
                if options:
                    safe_options = list(options)
                    safe_val = v
                    if safe_val not in safe_options:
                        if not safe_val and safe_options:
                            safe_val = safe_options[0]
                            app_state.set_data_by_path(selected_path["value"], str(k), safe_val)
                            app_state.commit()
                        else:
                            safe_options.append(safe_val)
                            
                    inp = ui.select(safe_options, value=safe_val, label=label_text).classes('flex-grow').on_value_change(make_on_change())
                    inp.on('focus', make_on_focus())
                    inp.on('click', make_on_focus())
                elif isinstance(v, bool):
                    inp = ui.switch(text=label_text, value=v).on_value_change(make_on_change())
                    inp.on('focus', make_on_focus())
                    inp.on('click', make_on_focus()) 
                elif isinstance(v, (int, float)):
                    inp = ui.number(label=label_text, value=v).classes('flex-grow').on_value_change(make_on_change())
                    inp.on('focus', make_on_focus())
                else:
                    inp = ui.input(label=label_text, value=str(v)).classes('flex-grow').on_value_change(make_on_change())
                    inp.on('focus', make_on_focus())

            with props_container:
                has_primitives = False
                
                if isinstance(data_node, dict):
                    for k, v in data_node.items():
                        if not isinstance(v, (dict, list)):
                            has_primitives = True
                            is_req = SCHEMA_META.get(str(k), {}).get('required', False)
                            
                            with ui.row().classes('w-full items-center gap-2'):
                                if is_req:
                                    ui.icon('lock', size='sm').classes('text-gray-300 w-8 flex justify-center p-0 m-0')
                                else:
                                    ui.button(icon='remove_circle', color='red-400', on_click=lambda _, n=data_node, key=k: delete_item(n, key)).props('flat round size=sm').classes('w-8 p-0 m-0')
                                    
                                render_primitive_input(k, v)
                        
                        elif isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v):
                            if SCHEMA_META.get(str(k), {}).get('type') in ['container', 'list']:
                                continue
                            has_primitives = True
                            is_req = SCHEMA_META.get(str(k), {}).get('required', False)
                            
                            with ui.row().classes('w-full items-center gap-2'):
                                if is_req:
                                    ui.icon('lock', size='sm').classes('text-gray-300 w-8 flex justify-center p-0 m-0')
                                else:
                                    ui.button(icon='remove_circle', color='red-400', on_click=lambda _, n=data_node, key=k: delete_item(n, key)).props('flat round size=sm').classes('w-8 p-0 m-0')
                                
                                str_val = ", ".join(map(str, v))
                                def make_list_change(prop_key=k):
                                    def _handle(e):
                                        val_list = [x.strip() for x in e.value.split(',') if x.strip()]
                                        parsed_list = []
                                        for x in val_list:
                                            if x.lstrip('-').isdigit(): parsed_list.append(int(x))
                                            else:
                                                try: parsed_list.append(float(x))
                                                except ValueError: parsed_list.append(x)
                                        app_state.set_data_by_path(selected_path["value"], str(prop_key), parsed_list)
                                        app_state.commit()
                                        
                                        # Agnostic CSV label update logic
                                        schema_key = get_schema_key_for_path(selected_path["value"], app_state.config_data)
                                        label_key = get_label_key_for_schema(schema_key)
                                        is_label_update = (str(prop_key) == label_key) if label_key else ('name' in str(prop_key).lower())
                                        
                                        if is_label_update and tree is not None:
                                            curr_expanded = tree._props.get('expanded', [])
                                            tree._props['nodes'] = [app_state.build_tree_nodes(app_state.config_data)]
                                            tree._props['expanded'] = curr_expanded
                                            tree.update()
                                            
                                    return _handle
                                    
                                def make_on_focus(prop_key=k): return lambda _: update_footer(str(prop_key))
                                    
                                label_text = f"{k} (CSV) *" if is_req else f"{k} (CSV)"
                                inp = ui.input(label=label_text, value=str_val).classes('flex-grow').on_value_change(make_list_change())
                                inp.on('focus', make_on_focus())
                                
                elif isinstance(data_node, list):
                    for i, v in enumerate(data_node):
                        if not isinstance(v, (dict, list)):
                            has_primitives = True
                            with ui.row().classes('w-full items-center gap-2'):
                                ui.button(icon='remove_circle', color='red-400', on_click=lambda _, n=data_node, idx=i: delete_item(n, idx)).props('flat round size=sm').classes('w-8 p-0 m-0')
                                render_primitive_input(i, v)
                
                if not has_primitives:
                    ui.label("This node contains no primitive properties directly.").classes('text-gray-400 italic mt-2')

            # --- 3. UNIFIED ADD BUTTON ---
            ui.separator().classes('my-6')
            with ui.row().classes('w-full justify-start items-center gap-4'):
                with ui.button('Add Property / Node', icon='add', color='primary'):
                    with ui.menu() as add_menu:
                        opts = get_allowed_options(path, data_node, app_state.config_data)
                        if not opts or (len(opts) == 1 and opts[0]['type'] == 'custom_dict' and not isinstance(data_node, dict)):
                            ui.menu_item('No additions allowed', auto_close=True).classes('text-gray-400 italic')
                        else:
                            for opt in opts:
                                def make_menu_click(o=opt):
                                    return lambda: perform_add_action(path, o)
                                
                                icon_name = 'add'
                                if opt['type'] == 'list_item': icon_name = 'add_circle'
                                elif opt['type'] == 'list_item_typed': icon_name = 'playlist_add'
                                elif opt['type'] == 'list_item_append': icon_name = 'library_add'
                                elif opt['type'] == 'custom_dict': icon_name = 'post_add'
                                
                                with ui.menu_item(on_click=make_menu_click(), auto_close=True).classes('flex items-center gap-2'):
                                    ui.icon(icon_name, color='positive', size='sm')
                                    ui.label(opt['label'])

            # --- 4. SUB-CONTAINERS FOLDER VIEW ---
            sub_containers = []
            if isinstance(data_node, dict):
                for k, v in data_node.items():
                    is_primitive_list = isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v)
                    if isinstance(v, dict) or (isinstance(v, list) and not is_primitive_list) or (isinstance(v, list) and len(v)==0 and SCHEMA_META.get(str(k), {}).get('type') in ['container', 'list']):
                        sub_containers.append((k, f"{path}/{k}"))
            elif isinstance(data_node, list):
                for i, v in enumerate(data_node):
                    if isinstance(v, (dict, list)):
                        label = get_item_label(v, f"{path}/{i}", app_state.config_data, f"Item [{i}]")
                        sub_containers.append((label, f"{path}/{i}"))
                        
            if sub_containers:
                ui.separator().classes('my-6')
                ui.label("Sub-Containers").classes('text-xl font-bold text-slate-800 dark:text-slate-200 mb-4')
                with ui.row().classes('w-full gap-4 flex-wrap'):
                    for label, child_path in sub_containers:
                        def make_child_nav(nav_p=child_path):
                            return lambda e: (selected_path.update({"value": nav_p}), refresh_tree_and_editor())
                        
                        with ui.card().tight().classes('cursor-pointer hover:bg-blue-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-600 dark:bg-slate-800 shadow-sm transition-colors w-48').on('click', make_child_nav(child_path)):
                            with ui.row().classes('items-center p-3 gap-3 w-full'):
                                ui.icon('folder', color='primary', size='sm')
                                ui.label(str(label)).classes('font-bold text-slate-700 dark:text-slate-300 truncate w-32')

    # --- UI LAYOUT ---
    with ui.header().classes('bg-slate-800 text-white shadow-md p-4 flex justify-between items-center'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('settings_input_component', size='md')
            ui.label('Configuration Schema Editor').classes('text-xl font-bold tracking-wide')
        
        with ui.row().classes('gap-2 items-center'):
            def toggle_dark():
                dark_mode.value = not dark_mode.value
                theme_btn.props(f'icon={"light_mode" if dark_mode.value else "dark_mode"}')

            theme_btn = ui.button(icon='dark_mode', on_click=toggle_dark).props('flat round color=white').tooltip('Toggle Night Mode')
            ui.separator().props('vertical color=gray-500').classes('mx-2')

            def perform_undo():
                if app_state.undo():
                    refresh_tree_and_editor()
                    ui.notify('Undo successful', type='info')
                else:
                    ui.notify('Nothing to undo', type='warning')

            def perform_redo():
                if app_state.redo():
                    refresh_tree_and_editor()
                    ui.notify('Redo successful', type='info')
                else:
                    ui.notify('Nothing to redo', type='warning')
                    
            ui.button(icon='undo', color='slate-600', on_click=perform_undo).props('flat round').tooltip('Undo Edit')
            ui.button(icon='redo', color='slate-600', on_click=perform_redo).props('flat round').tooltip('Redo Edit')
            
            ui.separator().props('vertical')
            
            def load_files():
                app_state.load_yaml_files()
                global SCHEMA_META
                SCHEMA_META.clear()
                SCHEMA_META.update(load_schema())
                refresh_tree_and_editor()
                ui.notify('Reloaded from disk', color='blue')

            def save_files():
                existing_files = [f for f in glob.glob("*.yaml") + glob.glob("*.yml") if f != ".kashif_schema.yaml"]
                
                for filename, data in app_state.config_data.items():
                    if filename == ".kashif_schema.yaml": continue
                    try:
                        with open(filename, 'w') as f:
                            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                    except Exception as e:
                        ui.notify(f'Error saving {filename}: {e}', color='red')
                
                # Delete files tracking physical removal
                for f in existing_files:
                    if f not in app_state.config_data:
                        try:
                            os.remove(f)
                            ui.notify(f'Deleted {f} from disk', color='orange')
                        except Exception as e:
                            ui.notify(f'Error deleting {f}: {e}', color='red')
                
                ui.notify('Saved successfully', color='green')
                        
            ui.button('Reload files', icon='refresh', color='blue-600', on_click=load_files)
            ui.button('Save to Disk', icon='save', color='green-600', on_click=save_files)

    with ui.splitter(value=30).classes('w-full h-[calc(100vh-80px)]') as splitter:
        with splitter.before:
            with ui.column().classes('p-4 w-full h-full border-r border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900'):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label("Configuration Nodes").classes('text-lg font-bold text-slate-700 dark:text-slate-300')
                    with ui.row().classes('gap-1'):
                        def expand_all():
                            if tree is not None:
                                nodes = app_state.build_tree_nodes(app_state.config_data)
                                tree._props['expanded'].clear()
                                tree._props['expanded'].extend(get_all_node_ids(nodes[0]))
                                tree.update()
                                
                        def collapse_all():
                            if tree is not None:
                                tree._props['expanded'].clear()
                                tree.update()
                                
                        ui.button(icon='unfold_more', on_click=expand_all).props('flat round size=sm bg-slate-100').tooltip('Expand All')
                        ui.button(icon='unfold_less', on_click=collapse_all).props('flat round size=sm bg-slate-100').tooltip('Collapse All')
                
                tree_filter = ui.input('Filter nodes...').classes('w-full mb-4').props('clearable dense outlined')
                
                initial_nodes = [app_state.build_tree_nodes(app_state.config_data)]
                tree = ui.tree(initial_nodes, label_key='label', on_select=handle_tree_select).classes('w-full text-md')
                tree._props['selected'] = 'root'
                
                # Simplified Tree Header without buttons
                tree.add_slot('default-header', '''
                    <div class="row items-center w-full">
                        <q-icon :name="props.node.icon" size="sm" class="q-mr-sm" :color="props.node.color" />
                        <span class="text-subtitle2">{{ props.node.label }}</span>
                    </div>
                ''')
                
                def apply_tree_filter(e):
                    tree._props['filter'] = e.value
                    tree.update()
                tree_filter.on_value_change(apply_tree_filter)

        with splitter.after:
            with ui.column().classes('w-full h-full bg-slate-50 dark:bg-slate-800 justify-between'):
                with ui.column().classes('p-8 w-full h-full overflow-y-auto'):
                    editor_scroll_area = ui.column().classes('w-full max-w-4xl')
                
                with ui.card().tight().classes('w-full h-40 border-t border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]'):
                    footer_pane = ui.column().classes('p-6 w-full h-full')
                    update_footer(None)

    # Automatically load the root node on startup
    draw_editor("root")

ui.run(title="Config Visualizer", port=8080, dark=False)
