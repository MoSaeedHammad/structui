import sys

with open("src/structui/ui.py", "r") as f:
    content = f.read()

# Add assertion right before clear()
content = content.replace("self.editor_scroll_area.clear()", "assert self.editor_scroll_area is not None\n        self.editor_scroll_area.clear()")

# Find "with self.editor_scroll_area:" and prepend assertion
content = content.replace("with self.editor_scroll_area:", "assert self.editor_scroll_area is not None\n            with self.editor_scroll_area:")

# Also handle get_meta argument issue
content = content.replace("self.schema_manager.get_meta(k)", "self.schema_manager.get_meta(str(k))")

with open("src/structui/ui.py", "w") as f:
    f.write(content)
