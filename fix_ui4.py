import sys
import re

with open("src/structui/ui.py", "r") as f:
    content = f.read()

# Instead of blindly replacing which caused syntax errors because of my previous messy sed commands that were partially reverted?
# Let's just do it cleanly via regex
content = re.sub(r'(\s+)self\.editor_scroll_area\.clear\(\)', r'\1assert self.editor_scroll_area is not None\n\1self.editor_scroll_area.clear()', content)
content = re.sub(r'(\s+)with self\.editor_scroll_area:', r'\1assert self.editor_scroll_area is not None\n\1with self.editor_scroll_area:', content)
content = content.replace("meta_type = self.schema_manager.get_meta(k).get('type')", "meta_type = self.schema_manager.get_meta(str(k)).get('type')")
content = content.replace("def __init__(self, state: AppState, schema_manager: SchemaManager, dark_mode: bool = None):", "def __init__(self, state: AppState, schema_manager: SchemaManager, dark_mode: bool = False):")


with open("src/structui/ui.py", "w") as f:
    f.write(content)
