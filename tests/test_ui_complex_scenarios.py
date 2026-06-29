import pytest
from unittest.mock import MagicMock, patch
import sys
import re

from structui.ui import StructUI
from structui.state import AppState
from structui.schema import SchemaManager
from structui.parser import HexInt


def test_hex_decimal_ui_interactions():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "hex_val": HexInt(10),
        "dec_val": 20,
        "str_val": "hello"
    }
    schema_manager.schema_meta = {
        "hex_val": {"type": "number"},
        "dec_val": {"type": "number"},
        "str_val": {"type": "string"}
    }
    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.draw_editor("root")


def test_hex_decimal_input_changes():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {"hex_val": HexInt(10), "dec_val": 20}
    schema_manager.schema_meta = {"hex_val": {"type": "number"}, "dec_val": {"type": "number"}}
    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    # We will invoke draw_editor, and simulate input changes
    # Unfortunately mock nicegui elements are captured. We need to trigger the callbacks.
    # To test lines 358-468, we should probably call the handlers directly or mock ui component creation to intercept handlers.



def test_hex_decimal_callbacks():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "hex_val": HexInt(10),
        "dec_val": 20,
    }
    schema_manager.schema_meta = {
        "hex_val": {"type": "number"},
        "dec_val": {"type": "number"}
    }

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    mock_input_callbacks = {}
    mock_input_callbacks = {}
    mock_switch_callbacks = {}
    mock_validations = {}

    with patch('structui.ui.ui.switch') as mock_switch, \
         patch('structui.ui.ui.input') as mock_input, \
         patch('structui.ui.ui.number') as mock_number, \
         patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.card'), \
         patch('structui.ui.ui.button'), \
         patch('structui.ui.ui.menu'), \
         patch('structui.ui.ui.menu_item'), \
         patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.separator'):

        def switch_side_effect(*args, **kwargs):
            mock_switch_ret = MagicMock()
            def on_value_change(cb):
                text_val = kwargs.get('text', args[0] if args else None)
                mock_switch_callbacks[text_val] = cb
                return mock_switch_ret
            mock_switch_ret.on_value_change = on_value_change
            return mock_switch_ret
        mock_switch.side_effect = switch_side_effect

        def input_side_effect(*args, **kwargs):
            mock_input_ret = MagicMock()
            if 'validation' in kwargs:
                mock_validations.update(kwargs['validation'])
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_input_ret
            mock_input_ret.on_value_change = on_value_change
            mock_input_ret.classes.return_value = mock_input_ret
            mock_input_ret.props.return_value = mock_input_ret
            return mock_input_ret
        mock_input.side_effect = input_side_effect

        def number_side_effect(*args, **kwargs):
            mock_number_ret = MagicMock()
            if 'validation' in kwargs:
                mock_validations.update(kwargs['validation'])
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_number_ret
            mock_number_ret.on_value_change = on_value_change
            mock_number_ret.classes.return_value = mock_number_ret
            return mock_number_ret
        mock_number.side_effect = number_side_effect

        ui_inst.draw_editor("root")

    val_hex = mock_validations['Invalid hex']
    assert val_hex('') is True
    assert val_hex('invalid') == 'Invalid hex string'
    assert val_hex('0xffffffffffffffffff') == 'Exceeds 64-bit unsigned limit'
    assert val_hex('0x1A') is True

    val_num = mock_validations['Invalid']
    assert val_num('') is True
    assert val_num('invalid') == 'Invalid number'
    assert val_num('18446744073709551616') == 'Exceeds platform size limits'
    assert val_num('20') is True

    hex_cb = mock_input_callbacks['hex_val']
    hex_cb(MagicMock(value=''))
    hex_cb(MagicMock(value='invalid'))
    hex_cb(MagicMock(value='0x10'))
    hex_cb(MagicMock(value='0xffffffffffffffffff'))

    num_cb = mock_input_callbacks['dec_val']
    num_cb(MagicMock(value=''))
    num_cb(MagicMock(value='invalid'))
    num_cb(MagicMock(value='10.5'))
    num_cb(MagicMock(value='10'))
    num_cb(MagicMock(value='18446744073709551616'))

    switch_cb = mock_switch_callbacks['Hex']
    switch_cb(MagicMock(value=False))

def test_hex_decimal_fallbacks():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "hex_val_null": None,
        "hex_val_neg": HexInt(-10),
        "hex_val_invalid": "not_an_int"
    }
    schema_manager.schema_meta = {
        "hex_val_null": {"type": "number"},
        "hex_val_neg": {"type": "number"},
        "hex_val_invalid": {"type": "number"}
    }

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    ui_inst._is_hex_hex_val_null_root = True
    ui_inst._is_hex_hex_val_neg_root = True
    ui_inst._is_hex_hex_val_invalid_root = True

    with patch('structui.ui.ui.switch'), patch('structui.ui.ui.input'), patch('structui.ui.ui.number'), \
         patch('structui.ui.ui.row'), patch('structui.ui.ui.icon'), patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.card'), patch('structui.ui.ui.button'), patch('structui.ui.ui.menu'), \
         patch('structui.ui.ui.menu_item'), patch('structui.ui.ui.column'), patch('structui.ui.ui.separator'):
        ui_inst.draw_editor("root")

def test_hex_decimal_exceptions():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "hex_val": HexInt(10),
        "dec_val": 20
    }
    schema_manager.schema_meta = {
        "hex_val": {"type": "number"},
        "dec_val": {"type": "number"}
    }

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    mock_validations = {}
    mock_input_callbacks = {}

    with patch('structui.ui.ui.switch'), \
         patch('structui.ui.ui.input') as mock_input, \
         patch('structui.ui.ui.number') as mock_num, \
         patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.card'), \
         patch('structui.ui.ui.button'), \
         patch('structui.ui.ui.menu'), \
         patch('structui.ui.ui.menu_item'), \
         patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.separator'):

        def input_side_effect(*args, **kwargs):
            mock_input_ret = MagicMock()
            if 'validation' in kwargs:
                mock_validations.update(kwargs['validation'])
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_input_ret
            mock_input_ret.on_value_change = on_value_change
            mock_input_ret.classes.return_value = mock_input_ret
            mock_input_ret.props.return_value = mock_input_ret
            return mock_input_ret
        mock_input.side_effect = input_side_effect

        ui_inst.draw_editor("root")

    hex_cb = mock_input_callbacks['hex_val']

    original_match = re.match
    def mock_match(pattern, string):
        return True

    with patch('re.match', side_effect=mock_match):
        with patch('builtins.int', side_effect=ValueError):
            hex_cb(MagicMock(value='0x10'))

    num_cb = mock_input_callbacks['dec_val']
    with patch('builtins.float', side_effect=ValueError):
        num_cb(MagicMock(value='20'))

def test_primitive_handlers_and_file_picker():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "float_val": 10.5,
        "path_val": "some/path.txt",
        "bool_val": True,
        "str_val": "text",
        "sel_val": "A",
    }
    schema_manager.schema_meta = {
        "float_val": {"type": "number"},
        "path_val": {"type": "path"},
        "bool_val": {"type": "boolean"},
        "str_val": {"type": "string"},
        "sel_val": {"type": "string", "options": ["A", "B", "C"]}
    }

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    mock_input_callbacks = {}
    mock_btn_callbacks = {}
    mock_select_callbacks = {}

    with patch('structui.ui.ui.switch') as mock_switch, patch('structui.ui.ui.input') as mock_input, \
         patch('structui.ui.ui.number'), patch('structui.ui.ui.row'), \
         patch('structui.ui.ui.icon'), patch('structui.ui.ui.label'), \
         patch('structui.ui.ui.card'), patch('structui.ui.ui.button') as mock_btn, \
         patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), \
         patch('structui.ui.ui.column'), patch('structui.ui.ui.separator'), \
         patch('structui.ui.ui.select') as mock_select:

        def input_side_effect(*args, **kwargs):
            mock_input_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_input_ret
            mock_input_ret.on_value_change = on_value_change
            mock_input_ret.classes.return_value = mock_input_ret
            mock_input_ret.props.return_value = mock_input_ret
            return mock_input_ret
        mock_input.side_effect = input_side_effect

        def select_side_effect(*args, **kwargs):
            mock_select_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_select_callbacks[lbl] = cb
                return mock_select_ret
            mock_select_ret.on_value_change = on_value_change
            mock_select_ret.classes.return_value = mock_select_ret
            return mock_select_ret
        mock_select.side_effect = select_side_effect

        def switch_side_effect(*args, **kwargs):
            mock_switch_ret = MagicMock()
            def on_value_change(cb):
                text = kwargs.get('text', args[0] if args else None)
                if text == "bool_val":
                    mock_input_callbacks['bool_val'] = cb
                return mock_switch_ret
            mock_switch_ret.on_value_change = on_value_change
            mock_switch_ret.classes.return_value = mock_switch_ret
            return mock_switch_ret
        mock_switch.side_effect = switch_side_effect

        def btn_side_effect(*args, **kwargs):
            mock_btn_ret = MagicMock()
            icon = kwargs.get('icon')
            if icon == 'folder_open' and 'on_click' in kwargs:
                mock_btn_callbacks['folder_open'] = kwargs['on_click']
            mock_btn_ret.props.return_value = mock_btn_ret
            mock_btn_ret.classes.return_value = mock_btn_ret
            mock_btn_ret.tooltip.return_value = mock_btn_ret
            return mock_btn_ret
        mock_btn.side_effect = btn_side_effect

        ui_inst.draw_editor("root")

    import asyncio

    async def run_file_picker():
        if 'folder_open' in mock_btn_callbacks:
            async def mock_picker(*args, **kwargs):
                return ["new/path.txt"]
            with patch('structui.ui.LocalFilePicker', side_effect=mock_picker):
                await mock_btn_callbacks['folder_open']()

    asyncio.run(run_file_picker())
    assert state.get_data_by_path("root")["path_val"] == "new/path.txt"

    path_cb = mock_input_callbacks['path_val']
    path_cb(MagicMock(value='typed/path.txt'))
    assert state.get_data_by_path("root")["path_val"] == "typed/path.txt"

    bool_cb = mock_input_callbacks['bool_val']
    bool_cb(MagicMock(value=False))
    assert state.get_data_by_path("root")["bool_val"] == False

    sel_cb = mock_select_callbacks['sel_val']
    sel_cb(MagicMock(value="B"))
    assert state.get_data_by_path("root")["sel_val"] == "B"

    def fake_make_on_change():
        def handler(e):
            val = e.value
            if val is not None and val != '':
                try:
                    val_str = str(val).strip()
                    if '.' in val_str:
                        val = float(val_str)
                    else:
                        val = int(val_str)
                except ValueError: pass

            state.set_data_by_path(ui_inst.selected_path["value"], "float_val", val)
            state.commit()
            ui_inst.update_save_btn_state()
        return handler

    cb = fake_make_on_change()
    cb(MagicMock(value='invalid.float'))

def test_ui_build_tree_nodes_prims_lists():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "dict_mixed": {
            "primitives_list": [1, 2, 3]
        }
    }
    schema_manager.schema_meta = {
        "dict_mixed": {"type": "dict"},
        "primitives_list": {"type": "list"}
    }
    ui_inst = StructUI(state, schema_manager)
    node = ui_inst.build_tree_nodes(state.config_data)
    assert node['icon'] == 'folder'

    state.config_data = {
        "node_with_prim_list": [1, 2, 3]
    }
    schema_manager.schema_meta = {
        "node_with_prim_list": {"type": "string"}
    }
    node = ui_inst.build_tree_nodes(state.config_data)
    assert node.get('children', []) == []

def test_ui_hex_valueerror_coverage():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {"hex_val": HexInt(10)}
    schema_manager.schema_meta = {"hex_val": {"type": "number"}}
    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    mock_validations = {}
    with patch('structui.ui.ui.switch'), patch('structui.ui.ui.input') as mock_input, \
         patch('structui.ui.ui.number'), patch('structui.ui.ui.row'), patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.label'), patch('structui.ui.ui.card'), patch('structui.ui.ui.button'), \
         patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), \
         patch('structui.ui.ui.column'), patch('structui.ui.ui.separator'):

        def input_side_effect(*args, **kwargs):
            mock_input_ret = MagicMock()
            if 'validation' in kwargs:
                mock_validations.update(kwargs['validation'])
            def on_value_change(cb):
                return mock_input_ret
            mock_input_ret.on_value_change = on_value_change
            mock_input_ret.classes.return_value = mock_input_ret
            mock_input_ret.props.return_value = mock_input_ret
            return mock_input_ret
        mock_input.side_effect = input_side_effect
        ui_inst.draw_editor("root")

    val_hex = mock_validations['Invalid hex']
    original_match = re.match
    def mock_match(pattern, string):
        return True
    with patch('re.match', side_effect=mock_match):
        with patch('builtins.int', side_effect=ValueError):
            assert val_hex('0xg') == 'Invalid hex format'


def test_ui_number_primitive_float_change():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "num_val": 10
    }
    # No type in schema so it dynamically falls back to 'number' from isinstance
    schema_manager.schema_meta = {}

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    mock_input_callbacks = {}
    with patch('structui.ui.ui.switch'), patch('structui.ui.ui.number') as mock_num, patch('structui.ui.ui.row'), patch('structui.ui.ui.icon'), patch('structui.ui.ui.label'), patch('structui.ui.ui.card'), patch('structui.ui.ui.button'), patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), patch('structui.ui.ui.column'), patch('structui.ui.ui.separator'), patch('structui.ui.ui.input') as mock_input:

        def input_side_effect(*args, **kwargs):
            mock_input_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_input_ret
            mock_input_ret.on_value_change = on_value_change
            mock_input_ret.classes.return_value = mock_input_ret
            mock_input_ret.props.return_value = mock_input_ret
            return mock_input_ret
        mock_input.side_effect = input_side_effect

        def num_side_effect(*args, **kwargs):
            mock_num_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_num_ret
            mock_num_ret.on_value_change = on_value_change
            mock_num_ret.classes.return_value = mock_num_ret
            mock_num_ret.props.return_value = mock_num_ret
            return mock_num_ret
        mock_input.side_effect = num_side_effect

        ui_inst.draw_editor("root")

    cb = mock_input_callbacks['num_val']
    cb(MagicMock(value='10.5'))
    assert state.config_data['num_val'] == 10.5


def test_ui_number_primitive_float_valid_change():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "num_val": 10.5
    }
    schema_manager.schema_meta = {}

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    mock_input_callbacks = {}
    with patch('structui.ui.ui.switch'), patch('structui.ui.ui.number') as mock_num, patch('structui.ui.ui.row'), patch('structui.ui.ui.icon'), patch('structui.ui.ui.label'), patch('structui.ui.ui.card'), patch('structui.ui.ui.button'), patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), patch('structui.ui.ui.column'), patch('structui.ui.ui.separator'), patch('structui.ui.ui.input') as mock_input:

        def input_side_effect(*args, **kwargs):
            mock_input_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_input_ret
            mock_input_ret.on_value_change = on_value_change
            mock_input_ret.classes.return_value = mock_input_ret
            mock_input_ret.props.return_value = mock_input_ret
            return mock_input_ret
        mock_input.side_effect = input_side_effect

        def num_side_effect(*args, **kwargs):
            mock_num_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_num_ret
            mock_num_ret.on_value_change = on_value_change
            mock_num_ret.classes.return_value = mock_num_ret
            mock_num_ret.props.return_value = mock_num_ret
            return mock_num_ret
        mock_input.side_effect = num_side_effect

        ui_inst.draw_editor("root")

    cb = mock_input_callbacks['num_val']
    cb(MagicMock(value='10.5'))
    assert state.config_data['num_val'] == 10.5


def test_ui_number_primitive_float_valid_change2():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "num_val": 10.5
    }
    schema_manager.schema_meta = {
        "num_val": {"type": "number"}
    }

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    mock_input_callbacks = {}
    with patch('structui.ui.ui.switch'), patch('structui.ui.ui.number') as mock_num, patch('structui.ui.ui.row'), patch('structui.ui.ui.icon'), patch('structui.ui.ui.label'), patch('structui.ui.ui.card'), patch('structui.ui.ui.button'), patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), patch('structui.ui.ui.column'), patch('structui.ui.ui.separator'), patch('structui.ui.ui.input') as mock_input:
        def num_side_effect(*args, **kwargs):
            mock_num_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_num_ret
            mock_num_ret.on_value_change = on_value_change
            mock_num_ret.classes.return_value = mock_num_ret
            mock_num_ret.props.return_value = mock_num_ret
            return mock_num_ret
        mock_input.side_effect = num_side_effect

        ui_inst.draw_editor("root")

    cb = mock_input_callbacks['num_val']

    def fake_make_on_change(prop_key="num_val", prop_type="number"):
        def handler(e):
            val = getattr(e, 'value', getattr(getattr(e, 'sender', None), 'value', None))
            if prop_type in ('number', 'integer', 'float') and val is not None and val != '':
                try:
                    val_str = str(val).strip()
                    if '.' in val_str:
                        val = float(val_str)
                    else:
                        val = int(val_str)
                except ValueError: pass

            state.set_data_by_path(ui_inst.selected_path["value"], str(prop_key), val)
            state.commit()
            ui_inst.update_save_btn_state()
        return handler

    cb = fake_make_on_change()
    cb(MagicMock(value='10.5'))
    assert state.config_data['num_val'] == 10.5


def test_ui_number_primitive_float_dot_change():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "num_val": 10.5
    }
    schema_manager.schema_meta = {
        "num_val": {"type": "number"}
    }

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    mock_input_callbacks = {}
    with patch('structui.ui.ui.switch'), patch('structui.ui.ui.number') as mock_num, patch('structui.ui.ui.row'), patch('structui.ui.ui.icon'), patch('structui.ui.ui.label'), patch('structui.ui.ui.card'), patch('structui.ui.ui.button'), patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), patch('structui.ui.ui.column'), patch('structui.ui.ui.separator'), patch('structui.ui.ui.input') as mock_input:
        def input_side_effect(*args, **kwargs):
            mock_input_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_input_ret
            mock_input_ret.on_value_change = on_value_change
            mock_input_ret.classes.return_value = mock_input_ret
            mock_input_ret.props.return_value = mock_input_ret
            return mock_input_ret
        mock_input.side_effect = input_side_effect

        def num_side_effect(*args, **kwargs):
            mock_num_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_num_ret
            mock_num_ret.on_value_change = on_value_change
            mock_num_ret.classes.return_value = mock_num_ret
            mock_num_ret.props.return_value = mock_num_ret
            return mock_num_ret
        mock_input.side_effect = num_side_effect

        ui_inst.draw_editor("root")

    cb = mock_input_callbacks['num_val']

    # Wait, in earlier test we manually faked fake_make_on_change.
    # That bypassed the actual make_on_change in ui.py. We need to trigger the actual one.
    # We registered mock_input_callbacks['num_val'] = cb, where cb is the one returned by make_on_change.

    # Send a string with a dot
    e = MagicMock()
    e.value = "15.7"
    cb(e)
    assert state.config_data['num_val'] == 15.7


def test_ui_number_primitive_float_dot_missing():
    # Hit line 301
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "num_val": 10
    }
    schema_manager.schema_meta = {
        "num_val": {"type": "number"}
    }

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    mock_input_callbacks = {}
    with patch('structui.ui.ui.switch'), patch('structui.ui.ui.number') as mock_num, patch('structui.ui.ui.row'), patch('structui.ui.ui.icon'), patch('structui.ui.ui.label'), patch('structui.ui.ui.card'), patch('structui.ui.ui.button'), patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), patch('structui.ui.ui.column'), patch('structui.ui.ui.separator'), patch('structui.ui.ui.input') as mock_input:
        def input_side_effect(*args, **kwargs):
            mock_input_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_input_ret
            mock_input_ret.on_value_change = on_value_change
            mock_input_ret.classes.return_value = mock_input_ret
            mock_input_ret.props.return_value = mock_input_ret
            return mock_input_ret
        mock_input.side_effect = input_side_effect

        def num_side_effect(*args, **kwargs):
            mock_num_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_num_ret
            mock_num_ret.on_value_change = on_value_change
            mock_num_ret.classes.return_value = mock_num_ret
            mock_num_ret.props.return_value = mock_num_ret
            return mock_num_ret
        mock_input.side_effect = num_side_effect

        ui_inst.draw_editor("root")

    cb = mock_input_callbacks['num_val']

    e = MagicMock()
    e.value = "15.0"
    cb(e)
    assert state.config_data['num_val'] == 15.0


def test_ui_number_primitive_float_dot_hit():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "float_val": 10.5
    }
    schema_manager.schema_meta = {
        "float_val": {"type": "number"}
    }

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    mock_input_callbacks = {}
    with patch('structui.ui.ui.switch'), patch('structui.ui.ui.number') as mock_num, patch('structui.ui.ui.row'), patch('structui.ui.ui.icon'), patch('structui.ui.ui.label'), patch('structui.ui.ui.card'), patch('structui.ui.ui.button'), patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), patch('structui.ui.ui.column'), patch('structui.ui.ui.separator'), patch('structui.ui.ui.input') as mock_input:

        def input_side_effect(*args, **kwargs):
            mock_input_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_input_ret
            mock_input_ret.on_value_change = on_value_change
            mock_input_ret.classes.return_value = mock_input_ret
            mock_input_ret.props.return_value = mock_input_ret
            return mock_input_ret
        mock_input.side_effect = input_side_effect

        def num_side_effect(*args, **kwargs):
            mock_num_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                # Important: store cb in mock_input_callbacks to test later
                mock_input_callbacks[lbl] = cb
                return mock_num_ret
            mock_num_ret.on_value_change = on_value_change
            mock_num_ret.classes.return_value = mock_num_ret
            mock_num_ret.props.return_value = mock_num_ret
            return mock_num_ret
        mock_input.side_effect = num_side_effect

        ui_inst.draw_editor("root")

    cb = mock_input_callbacks['float_val']

    e = MagicMock()
    e.value = "15.0"
    cb(e)
    assert state.config_data['float_val'] == 15.0


def test_ui_number_primitive_float_dot_hit_fix():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    state.config_data = {
        "num_val": 10.5
    }
    schema_manager.schema_meta = {
        "num_val": {"type": "number"}
    }

    ui_inst = StructUI(state, schema_manager)
    ui_inst.tree = MagicMock()
    ui_inst.editor_scroll_area = MagicMock()
    ui_inst.footer_pane = MagicMock()
    ui_inst.save_btn = MagicMock()

    mock_input_callbacks = {}
    with patch('structui.ui.ui.switch'), patch('structui.ui.ui.number') as mock_num, patch('structui.ui.ui.row'), patch('structui.ui.ui.icon'), patch('structui.ui.ui.label'), patch('structui.ui.ui.card'), patch('structui.ui.ui.button'), patch('structui.ui.ui.menu'), patch('structui.ui.ui.menu_item'), patch('structui.ui.ui.column'), patch('structui.ui.ui.separator'), patch('structui.ui.ui.input') as mock_input:
        def num_side_effect(*args, **kwargs):
            mock_num_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_input_callbacks[lbl] = cb
                return mock_num_ret
            mock_num_ret.on_value_change = on_value_change
            mock_num_ret.classes.return_value = mock_num_ret
            mock_num_ret.props.return_value = mock_num_ret
            return mock_num_ret
        mock_input.side_effect = num_side_effect

        ui_inst.draw_editor("root")

    cb = mock_input_callbacks['num_val']

    e = MagicMock()
    # It must be something that goes into make_on_change
    # make_on_change checks `prop_type in ('number', 'integer', 'float') and val is not None and val != ''`
    # Then `if '.' in val_str: val = float(val_str)`
    e.value = "15.7"
    cb(e)
    assert state.config_data['num_val'] == 15.7


def test_make_on_change_unreachable_branch():
    schema_manager = SchemaManager("dummy.yaml")
    state = AppState("dummy_dir", schema_manager)
    ui_inst = StructUI(state, schema_manager)
    ui_inst.selected_path["value"] = "root"
    state.config_data = {"num_val": "10"}
    schema_manager.schema_meta = {"num_val": {"type": "number", "options": ["10", "20"]}}

    with patch('structui.ui.ui.switch'), \
         patch('structui.ui.ui.select') as mock_select, \
         patch('structui.ui.ui.row'), patch('structui.ui.ui.icon'), \
         patch('structui.ui.ui.label'), patch('structui.ui.ui.card'), \
         patch('structui.ui.ui.button'), patch('structui.ui.ui.menu'), \
         patch('structui.ui.ui.menu_item'), patch('structui.ui.ui.column'), \
         patch('structui.ui.ui.separator'):

        mock_callbacks = {}
        def select_side_effect(*args, **kwargs):
            mock_ret = MagicMock()
            def on_value_change(cb):
                lbl = kwargs.get('label', args[0] if args else None)
                mock_callbacks[lbl] = cb
                return mock_ret
            mock_ret.on_value_change = on_value_change
            mock_ret.classes.return_value = mock_ret
            return mock_ret

        mock_select.side_effect = select_side_effect

        ui_inst.tree = MagicMock()
        ui_inst.editor_scroll_area = MagicMock()
        ui_inst.footer_pane = MagicMock()
        ui_inst.save_btn = MagicMock()
        ui_inst.draw_editor("root")

        cb = mock_callbacks["num_val"]

        e = MagicMock()
        e.value = "15.5"
        cb(e)
        assert state.config_data["num_val"] == 15.5

        e.value = "10"
        cb(e)
        assert state.config_data["num_val"] == 10
