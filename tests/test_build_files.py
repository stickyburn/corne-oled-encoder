"""Tests for the repo's build and configuration files.

Covers the hardware definition JSON, the build matrix, the GitHub Actions
workflow, the west manifest, the per-side conf/overlay files, the settings
reset directory and .gitignore. No third-party dependencies: build.yaml
and the manifest are parsed textually (build.yaml is plain YAML with
scalar keys, which the zmkfirmware workflow converts to JSON with yq).
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

ZMK_REVISION = "edf5c0814fd3ea202e43aad2d68fd32e882a518c"
KEEBART_REVISION = "98c5a1181ff7db1f480f684f714126922d55b8f0"


def read(*parts):
    return REPO_ROOT.joinpath(*parts).read_text()


class TestHardwareJson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(read("config", "corne_choc_pro.json"))

    def test_contains_only_the_default_layout(self):
        # The 5-column layout of the vendor file is intentionally dropped;
        # this build is the 46-position six-column board only.
        self.assertEqual(set(self.doc["layouts"]), {"default_layout"})

    def test_default_layout_has_46_keys_with_expected_geometry(self):
        keys = self.doc["layouts"]["default_layout"]["layout"]
        self.assertEqual(len(keys), 46)
        per_row = {}
        for key in keys:
            per_row[key["row"]] = per_row.get(key["row"], 0) + 1
        self.assertEqual(per_row, {0: 14, 1: 14, 2: 12, 3: 6})
        for key in keys:
            self.assertIn("x", key)
            self.assertIn("y", key)

    def test_sensor_refs_match_real_dts_labels_in_order(self):
        # The vendor JSON's refs (left_encoder_ex1, ...) do not match the
        # board devicetree labels; the refs must be the real labels, in the
        # board's sensor list order: left ex1/ex2 then right ex1/ex2.
        sensors = self.doc["sensors"]
        self.assertEqual(len(sensors), 4)
        self.assertEqual(
            [sensor["ref"] for sensor in sensors],
            ["left_ex1_encoder", "left_ex2_encoder",
             "right_ex1_encoder", "right_ex2_encoder"],
        )


class TestBuildMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        text = read("build.yaml")
        match = re.search(r"(?m)^include:\s*$", text)
        assert match, "no include: key in build.yaml"
        entries = []
        for chunk in re.split(r"(?m)^  - board:\s*", text[match.end():]):
            lines = [line for line in chunk.splitlines()
                     if line.strip() and not line.lstrip().startswith("#")]
            if not lines:
                continue
            entry = {"board": lines[0].strip()}
            for line in lines[1:]:
                prop = re.match(r"^    ([a-z-]+):\s*(.*?)\s*$", line)
                if prop:
                    entry[prop.group(1)] = prop.group(2)
            entries.append(entry)
        assert entries, "no build matrix entries parsed"
        cls.entries = entries

    def by_board(self, board):
        return [entry for entry in self.entries if entry["board"] == board]

    def test_has_four_jobs(self):
        self.assertEqual(len(self.entries), 4)
        self.assertEqual(len(self.by_board("corne_choc_pro_left")), 2)
        self.assertEqual(len(self.by_board("corne_choc_pro_right")), 2)

    def test_normal_left_build(self):
        left = [entry for entry in self.by_board("corne_choc_pro_left")
                if entry.get("shield") != "settings_reset"]
        self.assertEqual(len(left), 1)
        entry = left[0]
        self.assertEqual(entry["shield"], "sharp_mip")
        self.assertEqual(entry["snippet"], "studio-rpc-usb-uart")
        self.assertEqual(entry["cmake-args"], "-DCONFIG_ZMK_STUDIO=y")
        self.assertEqual(entry["artifact-name"], "corne-oled-encoder-left")

    def test_normal_right_build_has_no_shield_snippet_or_studio(self):
        right = [entry for entry in self.by_board("corne_choc_pro_right")
                 if entry.get("shield") != "settings_reset"]
        self.assertEqual(len(right), 1)
        entry = right[0]
        self.assertNotIn("shield", entry)
        self.assertNotIn("snippet", entry)
        self.assertNotIn("cmake-args", entry)
        self.assertEqual(entry["artifact-name"], "corne-oled-encoder-right")

    def test_settings_reset_builds(self):
        for board, artifact in [("corne_choc_pro_left", "settings-reset-left"),
                                 ("corne_choc_pro_right", "settings-reset-right")]:
            reset = [entry for entry in self.by_board(board)
                     if entry.get("shield") == "settings_reset"]
            self.assertEqual(len(reset), 1, board)
            entry = reset[0]
            self.assertEqual(entry["cmake-args"],
                             "-DZMK_CONFIG=${GITHUB_WORKSPACE}/config/reset")
            self.assertNotIn("snippet", entry)
            self.assertEqual(entry["artifact-name"], artifact)

    def test_artifact_names_are_distinct(self):
        names = [entry["artifact-name"] for entry in self.entries]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(sorted(names),
                         ["corne-oled-encoder-left", "corne-oled-encoder-right",
                          "settings-reset-left", "settings-reset-right"])


class TestWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read(".github", "workflows", "build-user-config.yml")

    def test_uses_pinned_zmk_reusable_workflow(self):
        self.assertIn(
            "uses: zmkfirmware/zmk/.github/workflows/build-user-config.yml@%s"
            % ZMK_REVISION,
            self.text,
        )

    def test_name_triggers_and_permissions(self):
        self.assertIn("name: Build firmware", self.text)
        for trigger in ("push:", "pull_request:", "workflow_dispatch:"):
            self.assertRegex(self.text, r"(?m)^  %s\s*$" % trigger)
        self.assertRegex(self.text, r"(?m)^permissions:\s*\n\s*contents: read")

    def test_inputs_point_at_repo_layout(self):
        self.assertIn("build_matrix_path: build.yaml", self.text)
        self.assertIn("config_path: config", self.text)


class TestWestManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("config", "west.yml")
        cls.chunks = re.split(r"(?m)^    - name: ", cls.text)[1:]

    def chunk(self, name):
        for chunk in self.chunks:
            if chunk.startswith(name):
                return chunk
        raise AssertionError("project %r not found" % name)

    def test_zmk_is_pinned_with_app_import(self):
        chunk = self.chunk("zmk")
        self.assertIn("url: https://github.com/zmkfirmware/zmk", chunk)
        self.assertIn("revision: %s" % ZMK_REVISION, chunk)
        self.assertIn("import: app/west.yml", chunk)

    def test_keebart_module_is_pinned_without_import(self):
        chunk = self.chunk("keebart-zmk-config")
        self.assertIn("url: https://github.com/Keebart/zmk-config", chunk)
        self.assertIn("revision: %s" % KEEBART_REVISION, chunk)
        self.assertIn("path: modules/keebart", chunk)
        self.assertNotIn("import:", chunk)

    def test_self_path_is_config(self):
        self.assertRegex(self.text, r"(?m)^  self:\s*\n\s*path: config")


class TestConfFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.left = read("config", "corne_choc_pro_left.conf")
        cls.right = read("config", "corne_choc_pro_right.conf")

    SHARED = [
        "CONFIG_ZMK_KEYBOARD_NAME=\"Corne Choc BT\"",
        "CONFIG_ZMK_IDLE_TIMEOUT=300000",
        "CONFIG_ZMK_SLEEP=y",
        "CONFIG_ZMK_IDLE_SLEEP_TIMEOUT=1800000",
        "CONFIG_ZMK_RGB_UNDERGLOW=y",
        "CONFIG_ZMK_RGB_UNDERGLOW_ON_START=n",
        "CONFIG_ZMK_RGB_UNDERGLOW_AUTO_OFF_IDLE=y",
        "CONFIG_ZMK_RGB_UNDERGLOW_BRT_MAX=30",
    ]

    def test_shared_settings_on_both_halves(self):
        for conf in (self.left, self.right):
            for line in self.SHARED:
                self.assertIn(line, conf)

    def test_left_enables_display_stack(self):
        self.assertIn("CONFIG_ZMK_DISPLAY=y", self.left)
        self.assertIn("CONFIG_ZMK_DISPLAY_WORK_QUEUE_DEDICATED=y", self.left)
        self.assertIn("CONFIG_ZMK_DISPLAY_BLANK_ON_IDLE=n", self.left)

    def test_right_disables_display(self):
        self.assertIn("CONFIG_ZMK_DISPLAY=n", self.right)
        self.assertNotIn("CONFIG_ZMK_DISPLAY_WORK_QUEUE_DEDICATED", self.right)
        self.assertNotIn("CONFIG_ZMK_DISPLAY_BLANK_ON_IDLE", self.right)

    def test_no_experimental_tx_power_overrides(self):
        for conf in (self.left, self.right):
            self.assertNotIn("CONFIG_BT_CTLR_TX_PWR", conf)


class TestOverlays(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.left = read("config", "corne_choc_pro_left.overlay")
        cls.right = read("config", "corne_choc_pro_right.overlay")

    def assert_status(self, text, label, status):
        self.assertRegex(
            text,
            r"&%s\s*\{\s*status\s*=\s*\"%s\";\s*\}" % (label, status),
            "%s should be %s" % (label, status),
        )

    def test_left_overlay_disables_all_four_encoders(self):
        for label in ("left_ex1_encoder", "left_ex2_encoder",
                      "right_ex1_encoder", "right_ex2_encoder"):
            self.assert_status(self.left, label, "disabled")
        self.assertNotIn('"okay"', self.left)

    def test_right_overlay_keeps_only_lower_right_encoder(self):
        for label in ("left_ex1_encoder", "left_ex2_encoder",
                      "right_ex1_encoder"):
            self.assert_status(self.right, label, "disabled")
        self.assert_status(self.right, "right_ex2_encoder", "okay")
        self.assertEqual(self.right.count('"okay"'), 1)


class TestMiscFiles(unittest.TestCase):
    def test_reset_config_directory_is_kept_in_place(self):
        readme = REPO_ROOT / "config" / "reset" / "README.md"
        self.assertTrue(readme.is_file())
        self.assertIn("ZMK_CONFIG", readme.read_text())

    def test_gitignore_covers_build_and_test_artifacts(self):
        text = read(".gitignore")
        self.assertIn("firmware/", text)
        self.assertIn("__pycache__/", text)


if __name__ == "__main__":
    unittest.main()