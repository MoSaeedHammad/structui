import re

with open("src/structui/ui.py", "r") as f:
    content = f.read()

# Fix self.editor_scroll_area errors where it complains None doesn't have clear
content = content.replace("self.editor_scroll_area.clear()", "if self.editor_scroll_area:\n            self.editor_scroll_area.clear()")
content = content.replace("with self.editor_scroll_area:", "if self.editor_scroll_area:\n            with self.editor_scroll_area:")

# Also handle get_meta argument issue
content = content.replace("meta_type = self.schema_manager.get_meta(k).get('type')", "meta_type = self.schema_manager.get_meta(str(k)).get('type')")

with open("src/structui/ui.py", "w") as f:
    f.write(content)
