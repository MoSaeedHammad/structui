import os
import sys
from nicegui import app, ui
from typing import Dict, Any, List
from .state import AppState
from .schema import SchemaManager
from .file_picker import LocalFilePicker

class StructUI:
    """The central view abstraction for managing the hierarchical NiceGUI visualization."""

    def __init__(self, state: AppState, schema_manager: SchemaManager, dark_mode: bool = None):
        self.state = state
        self.schema_manager = schema_manager
        
        self.selected_path = {"value": "root"}
        self.tree = None
        self.editor_scroll_area = None
        self.footer_pane = None
        self.dark_mode = None
        self.initial_dark_mode = dark_mode
        self.save_btn = None

    def get_allowed_options(self, path: str, data_node: Any) -> List[Dict[str, str]]:
        schema_key = self.schema_manager.get_schema_key_for_path(path, self.state.config_data)
        meta = self.schema_manager.get_meta(schema_key) if schema_key else {}
        allowed_from_schema = meta.get('allowed_children', [])
        allowed_options = []
        
        if isinstance(data_node, dict):
            for child in allowed_from_schema:
                if child not in data_node:
                    allowed_options.append({'label': f"Add {child.replace('_', ' ').title()}", 'type': 'dict_key', 'key': child})
                else:
                    child_meta = self.schema_manager.get_meta(child)
                    if isinstance(data_node[child], list) and child_meta.get('type') in ['container', 'list']:
                        if 'list_item_types' in child_meta:
                            for item_type in child_meta['list_item_types']:
                                allowed_options.append({'label': f"Add New {item_type.replace('_', ' ').title()} to {child}", 'type': 'list_item_append', 'key': child, 'item_type': item_type})
                        else:
                            item_type = child_meta.get('list_item_type', child)
                            allowed_options.append({'label': f"Add New {item_type.replace('_', ' ').title()} to {child}", 'type': 'list_item_append', 'key': child, 'item_type': item_type})
                            
            if not meta.get('restrict_custom_keys', False):
                allowed_options.append({'label': "Add Custom File" if path == "root" else "Add Custom Key", 'type': 'custom_dict'})
            
        elif isinstance(data_node, list):
            meta = self.schema_manager.get_meta(schema_key) if schema_key else {}
            if 'list_item_types' in meta:
                for item_type in meta['list_item_types']:
                    allowed_options.append({'label': f"Add New {item_type.replace('_', ' ').title()}", 'type': 'list_item_typed', 'key': item_type})
            elif 'list_item_type' in meta:
                item_type = meta['list_item_type']
                allowed_options.append({'label': f"Add New {item_type.replace('_', ' ').upper()}", 'type': 'list_item_typed', 'key': item_type})
            else:
                allowed_options.append({'label': "Add New Item", 'type': 'list_item'})
                
        return allowed_options

    def build_tree_nodes(self, data: Any, path: str = "root", name: str = "Configurations") -> Dict[str, Any]:
        node = {'id': path, 'label': name}
        children = []
        node['allowed'] = self.get_allowed_options(path, data)
        has_prims = False
        
        if isinstance(data, dict):
            for k, v in data.items():
                if not isinstance(v, (dict, list)):
                    has_prims = True
                elif isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v):
                    if self.schema_manager.get_meta(str(k)).get('type') not in ['container', 'list']:
                        has_prims = True
                        
                if isinstance(v, (dict, list)):
                    if isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v):
                        if self.schema_manager.get_meta(str(k)).get('type') not in ['container', 'list']:
                            continue
                    children.append(self.build_tree_nodes(v, f"{path}/{k}", str(k)))
        elif isinstance(data, list):
            for i, v in enumerate(data):
                if isinstance(v, (dict, list)):
                    label = self.schema_manager.get_item_label(v, f"{path}/{i}", self.state.config_data, f"[{i}]")
                    children.append(self.build_tree_nodes(v, f"{path}/{i}", label))
                    
        if children and has_prims:
            node['icon'], node['color'] = 'folder_special', 'purple'
        elif children and not has_prims:
            node['icon'], node['color'] = 'folder', 'primary'
        elif not children and has_prims:
            node['icon'], node['color'] = 'settings', 'blue-8'
        else:
            node['icon'], node['color'] = 'folder_open', 'grey-5'
                    
        if children:
            node['children'] = children
            
        return node

    def refresh_tree_and_editor(self):
        if self.tree is not None:
            new_nodes = [self.build_tree_nodes(self.state.config_data)]
            curr_expanded = set(self.tree._props.get('expanded', []))
            
            if self.selected_path["value"]:
                parts = self.selected_path["value"].split('/')
                for i in range(1, len(parts) + 1):
                    curr_expanded.add("/".join(parts[:i]))
            
            self.tree._props['nodes'] = new_nodes
            self.tree._props['expanded'] = list(curr_expanded)
            
            if self.selected_path["value"]:
                self.tree._props['selected'] = self.selected_path["value"]
                
            self.tree.update()
            
        if not self.selected_path["value"]:
            self.selected_path["value"] = "root"
            
        self.update_save_btn_state()

        self.draw_editor(self.selected_path["value"])

    def update_save_btn_state(self):
        if getattr(self, 'save_btn', None):
            if getattr(self.state, 'is_dirty', False):
                self.save_btn._props['color'] = 'warning'
                self.save_btn.tooltip('Unsaved Changes Available!')
            else:
                self.save_btn._props['color'] = 'primary'
                self.save_btn.tooltip('Save Configurations')
            self.save_btn.update()

        self.draw_editor(self.selected_path["value"])

    def update_footer(self, prop_key=None):
        self.footer_pane.clear()
        with self.footer_pane:
            if not prop_key:
                ui.label("Help & Metadata").classes('text-lg font-bold text-gray-700 dark:text-gray-300')
                ui.label("Select a property in the editor to see its description and type.").classes('text-gray-500 dark:text-gray-400 italic')
                return
                
            meta = self.schema_manager.get_meta(prop_key)
            if not meta:
                meta = {"type": "unknown", "desc": "No description available for this property."}
                
            with ui.row().classes('items-center gap-2 mb-2'):
                ui.icon('info', size='sm', color='primary')
                ui.label(prop_key).classes('text-lg font-bold text-blue-800 dark:text-blue-300 font-mono')
                ui.badge(meta.get('type', 'unknown'), color='blue-200').classes('text-blue-900 ml-2')
                
                is_req = meta.get('required', False)
                req_color = "red-100 text-red-800" if is_req else "green-100 text-green-800"
                ui.badge("Required" if is_req else "Optional").classes(f'ml-2 {req_color} font-bold border border-current')
            ui.markdown(meta.get('desc', 'No description provided.')).classes('text-gray-700 dark:text-gray-300 text-md ml-8')

    def handle_add_node(self, path: str, option: Dict[str, str]):
        data_node = self.state.get_data_by_path(path)
        opt_type = option['type']
        
        if opt_type == 'dict_key':
            if isinstance(data_node, dict):
                k = option.get('key')
                meta_type = self.schema_manager.get_meta(k).get('type')
                if meta_type == 'list':
                    data_node[k] = []
                elif meta_type in ['container', 'dict']:
                    data_node[k] = {}
                elif meta_type == 'bool':
                    data_node[k] = False
                elif meta_type in ['int', 'number', 'float']:
                    data_node[k] = 0
                else:
                    data_node[k] = ""
        elif opt_type == 'custom_dict':
            if isinstance(data_node, dict):
                with ui.dialog() as dialog, ui.card().classes('min-w-[300px]'):
                    def perform_add(dyn_key, dyn_type):
                        if dyn_key:
                            if dyn_type == 'dict': data_node[dyn_key] = {}
                            elif dyn_type == 'list': data_node[dyn_key] = []
                            elif dyn_type == 'string': data_node[dyn_key] = ""
                            elif dyn_type == 'integer': data_node[dyn_key] = 0
                            elif dyn_type == 'boolean': data_node[dyn_key] = False
                        dialog.close()
                        self.state.commit()
                        self.refresh_tree_and_editor()
                    ui.label('Enter new key name:').classes('font-bold')
                    inp = ui.input().classes('w-full')
                    ui.label('Select Type:').classes('font-bold mt-2')
                    type_sel = ui.select(['string', 'integer', 'boolean', 'list', 'dict'], value='string').classes('w-full')
                    ui.button('Add', on_click=lambda: perform_add(inp.value, type_sel.value)).classes('mt-4 w-full')
                dialog.open()
                return
        elif opt_type in ['list_item', 'list_item_typed']:
            if isinstance(data_node, list):
                data_node.append({})
        elif opt_type == 'list_item_append':
            if isinstance(data_node, dict):
                list_key = option.get('key')
                if list_key in data_node and isinstance(data_node[list_key], list):
                    data_node[list_key].append({})
                    
        self.state.commit()
        self.refresh_tree_and_editor()

    def draw_editor(self, path: str):
        if not path:
            path = "root"
        self.selected_path["value"] = path
        self.editor_scroll_area.clear()
        self.update_footer(None)

        data_node = self.state.get_data_by_path(path)
        if data_node is None:
            with self.editor_scroll_area:
                ui.label("This node no longer exists or was deleted.").classes('text-red-500 mt-10 text-lg font-bold')
            return 

        with self.editor_scroll_area:
            # INTERACTIVE BREADCRUMBS
            parts = path.split('/')
            with ui.row().classes('items-center gap-2 mb-6 w-full flex-wrap'):
                current_path = []
                for i, p in enumerate(parts):
                    current_path.append(p)
                    full_path = "/".join(current_path)
                    
                    def make_breadcrumb_nav(nav_p=full_path):
                        return lambda e: (self.selected_path.update({"value": nav_p}), self.refresh_tree_and_editor())
                    
                    ui.label("Root" if p == "root" else p).classes('text-blue-600 dark:text-blue-400 hover:text-blue-800 cursor-pointer font-bold text-lg hover:underline').on('click', make_breadcrumb_nav())
                    if i < len(parts) - 1:
                        ui.icon('chevron_right', color='gray').classes('text-gray-400')
            
            # EDITOR HEADER
            with ui.row().classes('w-full items-center justify-between mb-4 pb-2 border-b border-gray-200 dark:border-slate-700'):
                with ui.row().classes('items-center bg-slate-50 dark:bg-slate-900 gap-2'):
                    prop_search = ui.input('Search properties...').classes('w-64').props('dense rounded outlined')
                    
                    def locate_in_tree(p=path):
                        if self.tree:
                            parts = p.split('/')
                            paths_to_expand = ['/'.join(parts[:i+1]) for i in range(len(parts))]
                            self.tree.expand(paths_to_expand)
                            ui.notify('Located in tree', color='blue')

                    ui.button(icon='my_location', on_click=locate_in_tree).props('flat round').classes('text-slate-600 dark:text-slate-400').tooltip('Locate in Tree')
                    
                    with ui.button(icon='add').props('flat round').classes('text-blue-500').tooltip('Add Property / Node'):
                        with ui.menu() as add_menu:
                            opts = self.get_allowed_options(path, data_node)
                            if not opts:
                                ui.menu_item('No actions available').classes('text-gray-400')
                            for opt in opts:
                                def make_add_callback(o=opt):
                                    return lambda: self.handle_add_node(path, o)
                                ui.menu_item(opt['label'], auto_close=True, on_click=make_add_callback()).classes('flex items-center gap-2')
                                
                    if path != "root":
                        def delete_current_container():
                            parent_path = "/".join(path.split('/')[:-1])
                            node_key = path.split('/')[-1]
                            parent_node = self.state.get_data_by_path(parent_path)
                            if isinstance(parent_node, dict): parent_node.pop(node_key, None)
                            elif isinstance(parent_node, list): parent_node.pop(int(node_key))
                            self.state.commit()
                            self.selected_path["value"] = parent_path
                            self.refresh_tree_and_editor()

                        ui.button(icon='delete', on_click=delete_current_container).props('flat round').classes('text-red-500').tooltip('Delete this entire container')
            
            # PRIMITIVES EDITOR
            props_container = ui.column().classes('w-full gap-4')
            
            def render_primitive_input(k, v, parent_node):
                def make_on_change(prop_key=k):
                    def handler(e):
                        self.state.set_data_by_path(self.selected_path["value"], str(prop_key), e.value)
                        self.state.commit()
                        self.update_save_btn_state()
                    return handler
                    
                meta = self.schema_manager.get_meta(str(k))
                is_required = meta.get('required', False)
                label_text = f"{k} *" if is_required else str(k)
                options = meta.get('options')
                
                with ui.row().classes('items-center flex-grow flex-nowrap gap-2 w-full'):
                    if options:
                        safe_options = list(options)
                        if v not in safe_options: safe_options.append(v)
                        inp = ui.select(safe_options, value=v, label=label_text).classes('flex-grow').on_value_change(make_on_change())
                    elif isinstance(v, bool):
                        inp = ui.switch(text=label_text, value=v).on_value_change(make_on_change())
                    elif isinstance(v, (int, float)):
                        inp = ui.number(label=label_text, value=v).classes('flex-grow').on_value_change(make_on_change())
                    else:
                        inp = ui.input(label=label_text, value=str(v)).classes('flex-grow').on_value_change(make_on_change())
                        
                    inp.on('focus', lambda _: self.update_footer(str(k)))
                    
                    if not is_required:
                        def delete_prop(pk=k, pd=parent_node):
                            if isinstance(pd, dict) and pk in pd: pd.pop(pk, None)
                            elif isinstance(pd, list) and int(pk) < len(pd): pd.pop(int(pk))
                            self.state.commit()
                            self.refresh_tree_and_editor()
                        ui.button(icon='delete_outline', color='red-400', on_click=delete_prop).props('flat round size=sm').tooltip('Remove Property').classes('mt-2')
                
            with props_container:
                has_primitives = False
                if isinstance(data_node, dict):
                    for k, v in data_node.items():
                        if not isinstance(v, (dict, list)):
                            has_primitives = True
                            with ui.row().classes('w-full items-center gap-2'):
                                is_req = self.schema_manager.get_meta(str(k)).get('required', False)
                                ui.icon('lock', size='sm').classes('text-gray-400 w-8') if is_req else ui.icon('edit', size='sm').classes('text-blue-400 w-8')
                                render_primitive_input(k, v, data_node)
                elif isinstance(data_node, list):
                    for i, v in enumerate(data_node):
                        if not isinstance(v, (dict, list)):
                            has_primitives = True
                            with ui.row().classes('w-full items-center gap-2'):
                                ui.icon('edit', size='sm').classes('text-blue-400 w-8')
                                render_primitive_input(i, v, data_node)
                                
                if not has_primitives:
                    ui.label("This node contains no primitive properties directly.").classes('text-gray-400 italic mt-2')
            
            # SUB-CONTAINERS FOLDERS
            sub_containers = []
            if isinstance(data_node, dict):
                for k, v in data_node.items():
                    if isinstance(v, dict) or (isinstance(v, list) and not (isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v))):
                        sub_containers.append((k, f"{path}/{k}"))
            elif isinstance(data_node, list):
                for i, v in enumerate(data_node):
                    if isinstance(v, (dict, list)):
                        item_label = self.schema_manager.get_item_label(v, f"{path}/{i}", self.state.config_data, f"Item [{i}]")
                        sub_containers.append((item_label, f"{path}/{i}"))
                        
            if sub_containers:
                ui.separator().classes('my-6')
                ui.label("Sub-Containers").classes('text-xl font-bold text-slate-800 dark:text-slate-200 mb-4')
                with ui.row().classes('w-full gap-4 flex-wrap'):
                    for label, child_path in sub_containers:
                        with ui.card().tight().classes('cursor-pointer hover:bg-blue-50 border border-gray-200 dark:bg-slate-800 shadow-sm w-48').on('click', lambda _, cp=child_path: (self.selected_path.update({"value": cp}), self.refresh_tree_and_editor())):
                            with ui.row().classes('items-center p-3 gap-3 w-full'):
                                ui.icon('folder', color='primary', size='sm')
                                ui.label(str(label)).classes('font-bold text-slate-700 dark:text-slate-300 truncate w-32')

    def render(self):
        self.dark_mode = ui.dark_mode(value=self.initial_dark_mode)
        ui.add_head_html('''
            <style>
                body.body--light { background-color: #f8fafc; }
                body.body--dark { background-color: #0f172a; }
                .q-tree__node-header { width: 100%; }
                
                body.body--dark .q-tree { color: #e2e8f0 !important; }
                body.body--dark .q-field__native, body.body--dark .q-field__label { color: #e2e8f0 !important; }
                body.body--dark .q-card { background-color: #1e293b !important; border-color: #334155 !important; color: #e2e8f0 !important; }
                body.body--dark .bg-slate-50 { background-color: #0f172a !important; border-color: #334155 !important; }
            </style>
        ''')
        
        with ui.header().classes('bg-slate-800 text-white shadow-md p-4 flex justify-between items-center'):
            with ui.row().classes('items-center gap-3 w-1/2 overflow-hidden'):
                ui.button(icon='home', color='primary', on_click=lambda: ui.navigate.to('/')).props('round flex-shrink-0').tooltip('Return to Home')
                ui.icon('settings_input_component', size='md')
                ui.label('StructUI Editor').classes('text-xl font-bold tracking-wide')
                ui.badge().classes('text-xs ml-4 py-1 px-2 font-mono truncate max-w-sm').bind_text_from(self.state, 'data_dir', backward=lambda d: f"Workspace: {d}" if d else "No Workspace Loaded")
            
            with ui.row().classes('gap-2 items-center'):
                ui.button(icon='dark_mode', on_click=lambda: self.dark_mode.set_value(not self.dark_mode.value)).props('flat round color=white')
                ui.separator().props('vertical color=gray-500').classes('mx-2')
                
                # Load Configuration / Schema Buttons
                async def pick_config_dir():
                    result = await LocalFilePicker(directory=self.state.data_dir, dirs_only=True, upper_limit=None, show_hidden_files=True)
                    if result:
                        self.state.data_dir = result[0]
                        self.state.load_files()
                        self.selected_path["value"] = "root"
                        self.refresh_tree_and_editor()
                        ui.notify(f'Loaded Configs from {self.state.data_dir}', color='blue')

                async def pick_schema_file():
                    result = await LocalFilePicker(directory=os.path.dirname(os.path.abspath(self.schema_manager.schema_filepath)), multiple=False, upper_limit=None, show_hidden_files=True)
                    if result:
                        self.schema_manager.schema_filepath = result[0]
                        self.schema_manager._load_schema()
                        self.refresh_tree_and_editor()
                        ui.notify(f'Loaded Schema from {os.path.basename(self.schema_manager.schema_filepath)}', color='blue')

                ui.button('Load Configs', icon='folder_open', color='slate-600', on_click=pick_config_dir).props('outline').tooltip("Select configuration directory to load")
                ui.button('Load Schema', icon='schema', color='slate-600', on_click=pick_schema_file).props('outline').tooltip("Select schema file to load")
                
                ui.separator().props('vertical color=gray-500').classes('mx-2')
                
                # Exit Dialog
                with ui.dialog() as exit_dialog, ui.card():
                    ui.label('Are you sure you want to exit?').classes('text-lg font-bold mb-4')
                    with ui.row().classes('w-full justify-between mt-2'):
                        ui.button('Cancel', color='gray', on_click=exit_dialog.close).props('outline')
                        with ui.row().classes('gap-2'):
                            ui.button('Exit without Saving', color='red', on_click=lambda: (ui.notify('Exiting...', type='warning'), ui.run_javascript('window.close()'), app.shutdown())).props('outline')
                            ui.button('Save and Exit', color='green', on_click=lambda: (self.state.save_all_to_disk(), ui.notify('Saved! Exiting...', color='green'), ui.run_javascript('window.close()'), app.shutdown()))

                ui.button(icon='undo', color='slate-600', on_click=lambda: self.refresh_tree_and_editor() if self.state.undo() else ui.notify('Nothing to undo', type='warning')).props('flat round')
                ui.button(icon='redo', color='slate-600', on_click=lambda: self.refresh_tree_and_editor() if self.state.redo() else ui.notify('Nothing to redo', type='warning')).props('flat round')
                ui.separator().props('vertical')
                self.save_btn = ui.button(icon='save', color='primary', on_click=lambda: (self.state.save_all_to_disk(), ui.notify('Saved Configurations', color='green'), self.refresh_tree_and_editor())).props('round')
                self.save_btn.tooltip('Save Configurations')
                ui.button(icon='power_settings_new', color='red-500', on_click=exit_dialog.open).props('flat round').tooltip('Exit Application')
        
        with ui.row().classes('w-full h-[calc(100vh-80px)] overflow-hidden p-4 gap-4 flex-nowrap'):
            with ui.column().classes('w-1/3 min-w-[300px] h-full gap-4'):
                with ui.card().classes('w-full h-full p-0 shadow-md border border-gray-200 dark:border-slate-700 dark:bg-slate-800 flex flex-col'):
                    with ui.row().classes('w-full p-4 border-b border-gray-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 justify-between items-center'):
                        ui.label("Configuration Tree").classes('font-bold text-slate-700 dark:text-slate-300 tracking-wide uppercase text-sm')
                        with ui.row().classes('gap-1 items-center'):
                            tree_search = ui.input('Search...').classes('w-48').props('dense rounded outlined clearable')
                            ui.button(icon='unfold_less', on_click=lambda: self.tree.collapse() if self.tree else None).props('flat round size=sm').classes('text-slate-500').tooltip('Collapse All')
                            ui.button(icon='unfold_more', on_click=lambda: self.tree.expand() if self.tree else None).props('flat round size=sm').classes('text-slate-500').tooltip('Expand All')
                        
                    with ui.scroll_area().classes('w-full bg-slate-50 dark:bg-slate-900 flex-grow p-4 pt-2'):
                        self.tree = ui.tree([self.build_tree_nodes(self.state.config_data)], label_key='label', on_select=lambda e: (self.selected_path.update({"value": e.value}), self.refresh_tree_and_editor()) if e.value else None).classes('w-full custom-tree font-medium text-slate-700 dark:text-slate-300')
                        if self.tree:
                            self.tree._props['selected'] = self.selected_path["value"]
                            self.tree.props('control-color=primary node-key=id')
                            tree_search.on_value_change(lambda e: (self.tree._props.update({'filter': e.value}), self.tree.update()) if self.tree else None)
                            self.tree.expand()
                            
                            def handle_expanded(e):
                                if getattr(e, 'args', None) is not None:
                                    old_expanded = set(self.tree._props.get('expanded', []))
                                    new_expanded = set(e.args)
                                    added = new_expanded - old_expanded
                                    if added:
                                        target = list(added)[0]
                                        self.selected_path["value"] = target
                                        self.refresh_tree_and_editor()
                                    else:
                                        self.tree._props['expanded'] = list(new_expanded)
                                        self.tree.update()

                            self.tree.on('update:expanded', handle_expanded)
                        
            with ui.column().classes('w-2/3 flex-grow bg-slate-50 dark:bg-slate-900 h-full gap-4'):
                with ui.card().classes('w-full h-3/4 shadow-md border border-gray-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 flex flex-col p-6 pt-4'):
                    ui.label("Properties Editor").classes('font-bold text-slate-700 dark:text-slate-300 tracking-wide uppercase text-sm mb-2')
                    self.editor_scroll_area = ui.scroll_area().classes('w-full flex-grow')
                
                with ui.card().classes('w-full h-1/4 shadow-md border border-gray-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 p-4'):
                    self.footer_pane = ui.column().classes('w-full')
        
        self.refresh_tree_and_editor()
