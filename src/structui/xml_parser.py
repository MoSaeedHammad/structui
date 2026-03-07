import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional

def _parse_element(element: ET.Element, current_schema: Optional[Dict[str, Any]]) -> Any:
    """Recursively parse an XML element into a dictionary/list/value."""
    has_children = len(list(element)) > 0
    has_attributes = len(element.attrib) > 0
    text_content = element.text.strip() if element.text and element.text.strip() else None
    
    if not has_children and not has_attributes:
        return text_content if text_content is not None else ""
        
    result = {}
    
    for k, v in element.attrib.items():
        result[f"@{k}"] = v
        
    if text_content:
        result["#text"] = text_content
        
    child_groups = {}
    for child in element:
        child_schema = None
        if current_schema and "schema" in current_schema and child.tag in current_schema["schema"]:
            child_schema = current_schema["schema"][child.tag]
            
        parsed_child = _parse_element(child, child_schema)
        
        if child.tag not in child_groups:
            child_groups[child.tag] = {"items": [], "schema": child_schema}
        child_groups[child.tag]["items"].append(parsed_child)
        
    for tag, group in child_groups.items():
        items = group["items"]
        sch = group["schema"]
        
        is_list = False
        if sch and sch.get("type") == "list":
            is_list = True
        elif len(items) > 1:
            is_list = True
            
        if is_list:
            result[tag] = items
        else:
            result[tag] = items[0]
            
    return result

def load_xml(xml_content: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Parse an XML string into a generic dictionary.
    Handles attributes by adding an '@' prefix.
    If a schema is provided, forces elements defined as arrays into lists.
    """
    root = ET.fromstring(xml_content)
    root_schema = None
    if schema and root.tag in schema:
        root_schema = schema[root.tag]
        
    parsed = _parse_element(root, root_schema)
    return {root.tag: parsed}

def _build_xml(element: ET.Element, data: Any):
    if isinstance(data, dict):
        for k, v in data.items():
            if k.startswith('@'):
                element.set(k[1:], str(v))
            elif k == '#text':
                element.text = str(v)
            else:
                if isinstance(v, list):
                    for item in v:
                        child = ET.SubElement(element, k)
                        _build_xml(child, item)
                else:
                    child = ET.SubElement(element, k)
                    _build_xml(child, v)
    elif isinstance(data, list):
        for item in data:
            _build_xml(element, item)
    else:
        element.text = str(data)

def dict_to_xml(data: Dict[str, Any], root_tag: str = "root") -> str:
    """
    Serialize a generic dictionary back into an XML string.
    Unrolls single-item lists into multiple sibling XML tags.
    Converts dictionary keys starting with '@' into XML attributes.
    """
    if data and len(data) == 1:
        root_tag = list(data.keys())[0]
        root_data = data[root_tag]
    else:
        root_data = data
        
    root = ET.Element(root_tag)
    _build_xml(root, root_data)
    
    return ET.tostring(root, encoding='unicode', method='xml')

def save_xml(data: Dict[str, Any], filepath: str, root_tag: str = "root") -> None:
    """
    Save a generic dictionary to a file as well-formed XML.
    """
    xml_str = dict_to_xml(data, root_tag)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" + xml_str)
