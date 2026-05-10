import re

# Schema
with open("src/structui/schema.py", "r") as f: content = f.read()
content = content.replace("def get_label_key_for_schema(self, schema_key: str) -> str:", "def get_label_key_for_schema(self, schema_key: str) -> str | None:")
with open("src/structui/schema.py", "w") as f: f.write(content)

# State
with open("src/structui/state.py", "r") as f: content = f.read()
content = content.replace("self.config_data = self.parser.parse(file_path)", "self.config_data = self.parser.parse(file_path) or {}")
with open("src/structui/state.py", "w") as f: f.write(content)

# UI.py more specific typing casting
with open("src/structui/ui.py", "r") as f: content = f.read()
content = content.replace("self.selected_path: dict[str, str] = {\"value\": \"root\"}", "self.selected_path: dict[str, Any] = {\"value\": \"root\"}")
with open("src/structui/ui.py", "w") as f: f.write(content)
