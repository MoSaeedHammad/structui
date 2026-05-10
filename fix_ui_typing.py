with open("src/structui/ui.py", "r") as f:
    content = f.read()

content = content.replace("node = {'id': path, 'label': name}", "node: Dict[str, Any] = {'id': path, 'label': name}")
content = content.replace("children = []", "children: list[Dict[str, Any]] = []")

with open("src/structui/ui.py", "w") as f:
    f.write(content)
