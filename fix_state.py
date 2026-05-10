with open("src/structui/state.py", "r") as f:
    content = f.read()

content = content.replace("        curr = self.config_data", "        curr: Any = self.config_data")

with open("src/structui/state.py", "w") as f:
    f.write(content)
