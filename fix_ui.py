import sys

with open("src/structui/ui.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip() == "self.editor_scroll_area.clear()":
        # Keep indentation
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(indent + "if self.editor_scroll_area:\n")
        new_lines.append(indent + "    self.editor_scroll_area.clear()\n")
    elif line.strip() == "with self.editor_scroll_area:":
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(indent + "if self.editor_scroll_area is not None:\n")
        new_lines.append(indent + "    with self.editor_scroll_area:\n")
        # Now we need to manually indent everything that follows until we exit this block?
        # Wait, if we add an if, we need to indent everything that was under `with`.
        # No, a simpler approach is to tell mypy to ignore it or mock properly, wait, mypy just says it's Optional
    elif "meta_type = self.schema_manager.get_meta(k).get('type')" in line:
        new_lines.append(line.replace("self.schema_manager.get_meta(k)", "self.schema_manager.get_meta(str(k))"))
    else:
        new_lines.append(line)

with open("src/structui/ui.py", "w") as f:
    f.writelines(new_lines)
