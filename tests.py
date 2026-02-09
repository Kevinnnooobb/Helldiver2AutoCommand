"""
Tests for Helldivers 2 Auto Stratagem Caller.
"""

import json
import os
import tempfile
import unittest

from stratagems import (
    STRATAGEMS,
    get_categories,
    get_stratagems_by_category,
    search_stratagems,
    command_to_string,
    UP, DOWN, LEFT, RIGHT,
    CATEGORY_WEAPONS, CATEGORY_ORBITAL, CATEGORY_EAGLE,
    CATEGORY_DEFENSIVE, CATEGORY_SENTRIES, CATEGORY_VEHICLES,
    CATEGORY_SPECIAL, CATEGORY_MISSION,
)
from config import load_config, save_config, DEFAULT_KEY_BINDINGS, get_key_for_direction
from executor import execute_stratagem


class TestStratagems(unittest.TestCase):
    """Tests for stratagem data integrity and helper functions."""

    def test_all_stratagems_have_required_fields(self):
        """Every stratagem must have category, model, name, command, description."""
        required = {"category", "model", "name", "command", "description"}
        for s in STRATAGEMS:
            with self.subTest(name=s.get("name", "UNKNOWN")):
                self.assertTrue(required.issubset(s.keys()))

    def test_commands_contain_only_valid_directions(self):
        """Command lists must only contain ↑ ↓ ← → ."""
        valid = {UP, DOWN, LEFT, RIGHT}
        for s in STRATAGEMS:
            with self.subTest(name=s["name"]):
                for d in s["command"]:
                    self.assertIn(d, valid)

    def test_commands_are_non_empty(self):
        for s in STRATAGEMS:
            with self.subTest(name=s["name"]):
                self.assertGreater(len(s["command"]), 0)

    def test_total_stratagem_count(self):
        """Verify we have all stratagems from the spec."""
        self.assertGreaterEqual(len(STRATAGEMS), 80)

    def test_get_categories_returns_all(self):
        categories = get_categories()
        expected = {
            CATEGORY_WEAPONS, CATEGORY_ORBITAL, CATEGORY_EAGLE,
            CATEGORY_DEFENSIVE, CATEGORY_SENTRIES, CATEGORY_VEHICLES,
            CATEGORY_SPECIAL, CATEGORY_MISSION,
        }
        self.assertEqual(set(categories), expected)

    def test_get_stratagems_by_category(self):
        weapons = get_stratagems_by_category(CATEGORY_WEAPONS)
        self.assertGreater(len(weapons), 0)
        for s in weapons:
            self.assertEqual(s["category"], CATEGORY_WEAPONS)

    def test_search_by_name(self):
        results = search_stratagems("机枪")
        self.assertGreater(len(results), 0)
        for r in results:
            found = (
                "机枪" in r["name"]
                or "机枪" in r["model"]
                or "机枪" in r["description"]
            )
            self.assertTrue(found)

    def test_search_by_model(self):
        results = search_stratagems("APW-1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["model"], "APW-1")

    def test_search_case_insensitive(self):
        results = search_stratagems("apw-1")
        self.assertEqual(len(results), 1)

    def test_search_no_results(self):
        results = search_stratagems("不存在的战备xyz")
        self.assertEqual(len(results), 0)

    def test_command_to_string(self):
        self.assertEqual(command_to_string([DOWN, LEFT, DOWN, UP, RIGHT]), "↓←↓↑→")
        self.assertEqual(command_to_string([RIGHT, RIGHT, RIGHT]), "→→→")

    def test_specific_stratagem_mg43(self):
        """Verify MG-43 data matches the spec."""
        mg43 = [s for s in STRATAGEMS if s["model"] == "MG-43"]
        self.assertEqual(len(mg43), 1)
        self.assertEqual(mg43[0]["name"], "机枪")
        self.assertEqual(mg43[0]["command"], [DOWN, LEFT, DOWN, UP, RIGHT])

    def test_specific_stratagem_orbital_airburst(self):
        """Verify orbital airburst (轨道空爆攻击) data."""
        found = [s for s in STRATAGEMS if s["name"] == "轨道空爆攻击"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["command"], [RIGHT, RIGHT, RIGHT])

    def test_eagle_stratagems_count(self):
        eagles = get_stratagems_by_category(CATEGORY_EAGLE)
        self.assertEqual(len(eagles), 7)

    def test_mission_stratagems(self):
        missions = get_stratagems_by_category(CATEGORY_MISSION)
        self.assertGreaterEqual(len(missions), 4)
        names = [m["name"] for m in missions]
        self.assertIn("增援", names)
        self.assertIn("SOS 信标", names)
        self.assertIn("补给", names)


class TestConfig(unittest.TestCase):
    """Tests for configuration loading and saving."""

    def test_load_default_config(self):
        """Loading from non-existent file returns defaults."""
        nonexistent = os.path.join(tempfile.gettempdir(), "nonexistent_config_test.json")
        config = load_config(nonexistent)
        self.assertEqual(config["key_bindings"], DEFAULT_KEY_BINDINGS)
        self.assertEqual(config["stratagem_key"], "ctrl")
        self.assertIsInstance(config["key_delay"], float)

    def test_save_and_load_config(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        try:
            config = {
                "key_bindings": {"↑": "i", "↓": "k", "←": "j", "→": "l"},
                "stratagem_key": "alt",
                "key_delay": 0.1,
            }
            save_config(config, path)
            loaded = load_config(path)
            self.assertEqual(loaded["key_bindings"]["↑"], "i")
            self.assertEqual(loaded["stratagem_key"], "alt")
            self.assertAlmostEqual(loaded["key_delay"], 0.1)
        finally:
            os.unlink(path)

    def test_load_corrupt_config(self):
        """Corrupt JSON falls back to defaults."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("NOT VALID JSON{{{")
            path = f.name

        try:
            config = load_config(path)
            self.assertEqual(config["key_bindings"], DEFAULT_KEY_BINDINGS)
        finally:
            os.unlink(path)

    def test_get_key_for_direction(self):
        nonexistent = os.path.join(tempfile.gettempdir(), "nonexistent.json")
        config = load_config(nonexistent)
        self.assertEqual(get_key_for_direction("↑", config), "w")
        self.assertEqual(get_key_for_direction("↓", config), "s")
        self.assertEqual(get_key_for_direction("←", config), "a")
        self.assertEqual(get_key_for_direction("→", config), "d")


class TestExecutor(unittest.TestCase):
    """Tests for the stratagem executor (with mock keyboard)."""

    def test_execute_sends_correct_keys(self):
        """Verify the executor presses and releases the right keys in order."""
        pressed = []
        released = []

        class MockKeyboard:
            def press(self, key):
                pressed.append(key)

            def release(self, key):
                released.append(key)

        stratagem = {
            "model": "MG-43",
            "name": "机枪",
            "command": [DOWN, LEFT, DOWN, UP, RIGHT],
            "description": "test",
        }
        config = {
            "key_bindings": {"↑": "w", "↓": "s", "←": "a", "→": "d"},
            "stratagem_key": "ctrl",
            "key_delay": 0,
        }

        execute_stratagem(stratagem, config, keyboard_module=MockKeyboard())

        # First press should be the stratagem key
        self.assertEqual(pressed[0], "ctrl")
        # Then the directional keys: s, a, s, w, d
        self.assertEqual(pressed[1:], ["s", "a", "s", "w", "d"])
        # Released keys: direction keys + stratagem key at the end
        self.assertEqual(released, ["s", "a", "s", "w", "d", "ctrl"])

    def test_execute_with_custom_bindings(self):
        """Custom key bindings should be respected."""
        pressed = []

        class MockKeyboard:
            def press(self, key):
                pressed.append(key)

            def release(self, key):
                pass

        stratagem = {
            "model": "TEST",
            "name": "test",
            "command": [UP, DOWN],
            "description": "test",
        }
        config = {
            "key_bindings": {"↑": "i", "↓": "k", "←": "j", "→": "l"},
            "stratagem_key": "alt",
            "key_delay": 0,
        }

        execute_stratagem(stratagem, config, keyboard_module=MockKeyboard())
        self.assertEqual(pressed[0], "alt")
        self.assertEqual(pressed[1:], ["i", "k"])

    def test_stratagem_key_released_on_error(self):
        """Stratagem key must be released even if an error occurs during execution."""
        released = []

        class MockKeyboard:
            def press(self, key):
                if key == "w":
                    raise RuntimeError("test error")

            def release(self, key):
                released.append(key)

        stratagem = {
            "model": "TEST",
            "name": "test",
            "command": [UP],
            "description": "test",
        }
        config = {
            "key_bindings": {"↑": "w", "↓": "s", "←": "a", "→": "d"},
            "stratagem_key": "ctrl",
            "key_delay": 0,
        }

        with self.assertRaises(RuntimeError):
            execute_stratagem(stratagem, config, keyboard_module=MockKeyboard())

        # Stratagem key should still be released
        self.assertIn("ctrl", released)


if __name__ == "__main__":
    unittest.main()
