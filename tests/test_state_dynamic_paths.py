import pytest
from structui.state import evaluate_dynamic_path, clean_dynamic_options

def test_evaluate_dynamic_path_simple():
    data = {
        "connections": {
            "interface": {
                "name": "eth0"
            }
        }
    }
    res = evaluate_dynamic_path(data, "connections.interface.name")
    assert res == ["eth0"]

def test_evaluate_dynamic_path_wildcard():
    data = {
        "connections": [
            {
                "interfaces": [
                    {"itf_name": "eth0"},
                    {"itf_name": "wlan0"}
                ]
            },
            {
                "interfaces": [
                    {"itf_name": "eth1"},
                    {"itf_name": "eth0"} # duplicate
                ]
            }
        ]
    }
    res = evaluate_dynamic_path(data, "connections[*].interfaces[*].itf_name")
    assert res == ["eth0", "wlan0", "eth1", "eth0"]

def test_clean_dynamic_options():
    raw = ["eth0", None, "", "wlan0", "eth0", "eth1"]
    res = clean_dynamic_options(raw)
    assert res == ["eth0", "wlan0", "eth1"]

def test_evaluate_dynamic_path_missing_keys():
    data = {
        "connections": []
    }
    res = evaluate_dynamic_path(data, "connections[*].interfaces[*].itf_name")
    assert res == []
    
    data2 = {}
    res2 = evaluate_dynamic_path(data2, "connections[*].interfaces[*].itf_name")
    assert res2 == []
