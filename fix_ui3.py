import sys

with open("src/structui/ui.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip() == "self.editor_scroll_area.clear()":
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(indent + "assert self.editor_scroll_area is not None\n")
        new_lines.append(line)
    elif line.strip() == "with self.editor_scroll_area:":
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(indent + "assert self.editor_scroll_area is not None\n")
        new_lines.append(line)
    elif "meta_type = self.schema_manager.get_meta(k).get('type')" in line:
        new_lines.append(line.replace("self.schema_manager.get_meta(k)", "self.schema_manager.get_meta(str(k))"))
    elif "def __init__(self, state: AppState, schema_manager: SchemaManager, dark_mode: bool = None):" in line:
        new_lines.append(line.replace("dark_mode: bool = None", "dark_mode: bool = False"))
    else:
        new_lines.append(line)

with open("src/structui/ui.py", "w") as f:
    f.writelines(new_lines)
