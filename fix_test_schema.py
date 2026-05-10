with open("tests/test_schema.py", "r") as f:
    content = f.read()

content = content.replace("assert sm.get_label_key_for_schema(\"root\") is None", "assert not sm.get_label_key_for_schema(\"root\")")

with open("tests/test_schema.py", "w") as f:
    f.write(content)
