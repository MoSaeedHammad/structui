import re

# File picker
with open("src/structui/file_picker.py", "r") as f: content = f.read()
content = content.replace("upper_limit: Optional[str] = ...,", "upper_limit: Optional[str] = None,")
with open("src/structui/file_picker.py", "w") as f: f.write(content)

# XML Parser
with open("src/structui/xml_parser.py", "r") as f: content = f.read()
content = content.replace("child_groups = {}", "child_groups: dict = {}")
with open("src/structui/xml_parser.py", "w") as f: f.write(content)

# Schema
with open("src/structui/schema.py", "r") as f: content = f.read()
content = content.replace("return default", "return default or ''")
content = content.replace("return None", "return ''")
with open("src/structui/schema.py", "w") as f: f.write(content)

# State
with open("src/structui/state.py", "r") as f: content = f.read()
content = content.replace("self.config_data = self.parser.parse(file_path)", "self.config_data = self.parser.parse(file_path) or {}")
with open("src/structui/state.py", "w") as f: f.write(content)

# UI.py more specific typing casting
with open("src/structui/ui.py", "r") as f: content = f.read()
content = content.replace("self.selected_path = {\"value\": \"root\"}", "self.selected_path: dict[str, str] = {\"value\": \"root\"}")
content = content.replace("return options", "return options  # type: ignore")
with open("src/structui/ui.py", "w") as f: f.write(content)
