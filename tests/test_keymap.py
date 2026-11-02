"""Tests for config/corne_choc_pro.keymap.

Plain-text parsing only (no third-party dependencies). The original 42
bindings per layer are loaded from tests/fixtures/original_bindings.json,
which was extracted verbatim from the previous corne-config-zmk keymap
(config/corne.keymap) and is checked in as the baseline.
Only two original &none slots are intentionally extended for RGB controls.

The Corne Choc Pro inserts four middle keys into the original Corne layout
(rows 0 and 1 each gain two keys between the halves):

    original index -> new index
    0..5           -> 0..5    row 0, left of the insert
    6..11          -> 8..13   row 0, right of the insert
    12..17         -> 14..19  row 1, left of the insert
    18..23         -> 22..27  row 1, right of the insert
    24..35         -> 28..39  row 2, unchanged
    36..41         -> 40..45  thumb row, unchanged
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KEYMAP_PATH = REPO_ROOT / "config" / "corne_choc_pro.keymap"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "original_bindings.json"

ORIGINAL_LAYERS = ["default_layer", "system", "symbols", "brackets"]
LAYER_ORDER = ORIGINAL_LAYERS + ["maintenance"]
POSITION_COUNT = 46

# User-requested lighting controls replace only previously unused positions
# in the original System layer. Keep the original fixture unchanged.
SYSTEM_LIGHTING = {5: "&rgb_ug RGB_TOG", 17: "&rgb_ug RGB_EFF"}

# Keymap indices of the four inserted middle positions (rows 0/1, cols 6/7).
EXTRA_LEFT_TOP = 6  # not fitted on this build
EXTRA_RIGHT_TOP = 7  # regular key (play/pause on default)
EXTRA_LEFT_BOTTOM = 20  # not fitted on this build
EXTRA_RIGHT_BOTTOM = 21  # right_ex2 encoder push (mute on default)

EXTRA_BINDINGS = {
    "default_layer": {
        EXTRA_LEFT_TOP: "&none",
        EXTRA_RIGHT_TOP: "&kp C_PLAY_PAUSE",
        EXTRA_LEFT_BOTTOM: "&none",
        EXTRA_RIGHT_BOTTOM: "&kp C_MUTE",
    },
    "system": {
        EXTRA_LEFT_TOP: "&none",
        EXTRA_RIGHT_TOP: "&trans",
        EXTRA_LEFT_BOTTOM: "&none",
        EXTRA_RIGHT_BOTTOM: "&trans",
    },
    "symbols": {
        EXTRA_LEFT_TOP: "&none",
        EXTRA_RIGHT_TOP: "&trans",
        EXTRA_LEFT_BOTTOM: "&none",
        EXTRA_RIGHT_BOTTOM: "&trans",
    },
    "brackets": {
        EXTRA_LEFT_TOP: "&none",
        EXTRA_RIGHT_TOP: "&trans",
        EXTRA_LEFT_BOTTOM: "&none",
        EXTRA_RIGHT_BOTTOM: "&trans",
    },
}

# Maintenance layer: left-half positions only; "letter" comments refer to
# the default-layer binding at the same position. Everything else,
# including the two combo keys (7 and 45), is transparent.
MAINTENANCE_SPECIALS = {
    1: "&sys_reset",  # Q
    2: "&bootloader",  # W
    3: "&studio_unlock",  # F
    5: "&bt BT_SEL 4",  # G
    15: "&out OUT_USB",  # A
    16: "&out OUT_BLE",  # R
    17: "&none",  # S
}

SENSOR_BINDING = "&inc_dec_kp C_VOL_DN C_VOL_UP"
SENSOR_COUNT = 4  # left_ex1, left_ex2, right_ex1, right_ex2


def new_index_for_old(old_index):
    """Map an original 42-layout keymap index to the new 46-layout index."""
    if not 0 <= old_index <= 41:
        raise ValueError("old index out of range: %r" % old_index)
    if old_index < 6:
        return old_index
    if old_index < 18:
        return old_index + 2
    return old_index + 4


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def node_body(text, name):
    """Return the flat body of a named node (nodes used here never nest)."""
    match = re.search(r"\b%s\s*\{([^}]*)\}" % re.escape(name), text, flags=re.S)
    if not match:
        raise AssertionError("node %r not found" % name)
    return match.group(1)


def tokenize_groups(tokens):
    """Group a whitespace-split DT phandle list into behavior bindings.

    A binding starts at each '&' token; following tokens are its parameters.
    """
    groups = []
    for token in tokens:
        if token.startswith("&"):
            groups.append([token])
        else:
            groups[-1].append(token)
    return [" ".join(group) for group in groups]


def property_groups(body, prop):
    """Parse a '<...>;' property of a node into grouped binding strings."""
    pattern = r"(?<![\w-])%s\s*=\s*<(.*?)>;" % re.escape(prop)
    match = re.search(pattern, body, flags=re.S)
    if not match:
        raise AssertionError("property %r not found" % prop)
    return tokenize_groups(match.group(1).split())


class KeymapTestCase(unittest.TestCase):
    """Loads and prepares the parsed keymap for the tests below."""

    @classmethod
    def setUpClass(cls):
        cls.text = KEYMAP_PATH.read_text()
        cls.stripped = strip_comments(cls.text)
        cls.bindings = {
            layer: property_groups(node_body(cls.stripped, layer), "bindings")
            for layer in LAYER_ORDER
        }


class TestLayerStructure(KeymapTestCase):
    def test_layer_order_preserved_and_maintenance_is_fourth(self):
        positions = {name: self.stripped.index("%s {" % name) for name in LAYER_ORDER}
        self.assertEqual(
            [name for name, _ in sorted(positions.items(), key=lambda kv: kv[1])],
            LAYER_ORDER,
        )

    def test_all_layers_have_46_bindings(self):
        for layer, bindings in self.bindings.items():
            self.assertEqual(len(bindings), POSITION_COUNT, layer)

    def test_descriptive_display_name_on_every_layer(self):
        expected = {
            "default_layer": "Default",
            "system": "System",
            "symbols": "Symbols",
            "brackets": "Brackets",
            "maintenance": "Maintenance",
        }
        for layer, name in expected.items():
            body = node_body(self.stripped, layer)
            match = re.search(r'display-name\s*=\s*"([^"]*)"', body)
            self.assertIsNotNone(match, layer)
            self.assertEqual(match.group(1), name, layer)


class TestOriginalBindingsPreserved(KeymapTestCase):
    def test_original_bindings_preserved_except_requested_lighting_additions(self):
        fixture = json.loads(FIXTURE_PATH.read_text())
        self.assertEqual(sorted(fixture), sorted(ORIGINAL_LAYERS))
        for layer in ORIGINAL_LAYERS:
            original = fixture[layer]
            self.assertEqual(len(original), 42, layer)
            current = self.bindings[layer]
            for old_index, binding in enumerate(original):
                expected = SYSTEM_LIGHTING.get(old_index, binding) if layer == "system" else binding
                self.assertEqual(current[new_index_for_old(old_index)], expected,
                                 "%s: original position %d" % (layer, old_index))

    def test_lighting_controls_only_replace_unused_system_positions(self):
        original = json.loads(FIXTURE_PATH.read_text())["system"]
        for old_index, binding in SYSTEM_LIGHTING.items():
            self.assertEqual(original[old_index], "&none")
            self.assertEqual(self.bindings["system"][new_index_for_old(old_index)], binding)

    def test_inserted_extras_per_layer(self):
        for layer in ORIGINAL_LAYERS:
            current = self.bindings[layer]
            for position, expected in EXTRA_BINDINGS[layer].items():
                self.assertEqual(current[position], expected,
                                 "%s: extra position %d" % (layer, position))


class TestMaintenanceLayer(KeymapTestCase):
    def test_bindings(self):
        bindings = self.bindings["maintenance"]
        for position in range(POSITION_COUNT):
            expected = MAINTENANCE_SPECIALS.get(position, "&trans")
            self.assertEqual(bindings[position], expected, position)

    def test_combo_keys_are_transparent(self):
        # Position 7 (top-right middle key) and position 45 (outer right
        # thumb) form the combo that opens this layer.
        self.assertEqual(self.bindings["maintenance"][7], "&trans")
        self.assertEqual(self.bindings["maintenance"][45], "&trans")


class TestMaintenanceCombo(KeymapTestCase):
    def test_combo_properties(self):
        body = node_body(self.stripped, "maintenance_combo")
        self.assertRegex(body, r"timeout-ms\s*=\s*<50>")
        self.assertRegex(body, r"key-positions\s*=\s*<7\s+45>")
        self.assertRegex(body, r"bindings\s*=\s*<&mo\s+4>")
        self.assertRegex(body, r"layers\s*=\s*<0>")

    def test_combo_only_in_combos_container(self):
        self.assertRegex(self.stripped, r"combos\s*\{")
        self.assertIn("compatible = \"zmk,combos\"", self.stripped)


class TestSensorBindings(KeymapTestCase):
    def test_all_layers_bind_all_four_sensors_to_volume(self):
        for layer in LAYER_ORDER:
            body = node_body(self.stripped, layer)
            bindings = property_groups(body, "sensor-bindings")
            self.assertEqual(bindings, [SENSOR_BINDING] * SENSOR_COUNT, layer)


class TestPreservedSemantics(KeymapTestCase):
    def test_htp_hold_tap_behavior_unchanged(self):
        # 250 ms tapping term, tap-preferred flavor, hold = shifted letter
        # (LS(...) as the hold parameter), preserved verbatim from the
        # previous keymap.
        body = node_body(self.stripped, "homerow_mods")
        self.assertIn("#binding-cells = <2>", body)
        self.assertIn("tapping-term-ms = <250>", body)
        self.assertIn("quick-tap-ms = <0>", body)
        self.assertIn("flavor = \"tap-preferred\"", body)
        self.assertIn("bindings = <&kp>, <&kp>;", body)

    def test_chosen_physical_layout_is_default_layout(self):
        self.assertIn("zmk,physical-layout = &default_layout", self.stripped)

    def test_sensor_binding_direction_follows_vendor(self):
        # Vendor order is C_VOL_DN then C_VOL_UP; the actual rotation
        # direction must be confirmed on the physical board.
        self.assertIn("&inc_dec_kp C_VOL_DN C_VOL_UP", self.stripped)


if __name__ == "__main__":
    unittest.main()
