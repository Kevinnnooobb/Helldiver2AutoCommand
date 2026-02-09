"""
按键配置管理
Manages key bindings for stratagem direction inputs and the stratagem activation key.
Supports loading/saving custom key bindings from a JSON config file.
Supports per-stratagem hotkey bindings for in-game quick trigger.
"""

import json
import os

# Default config file path (next to this script)
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# Default key bindings: maps direction arrows to keyboard keys
DEFAULT_KEY_BINDINGS = {
    "↑": "w",
    "↓": "s",
    "←": "a",
    "→": "d",
}

# The key held down to open the stratagem input mode in-game
DEFAULT_STRATAGEM_KEY = "ctrl"

# Delay between key presses in seconds
DEFAULT_KEY_DELAY = 0.05


def _make_default():
    """Return a fresh default config dict."""
    return {
        "key_bindings": dict(DEFAULT_KEY_BINDINGS),
        "stratagem_key": DEFAULT_STRATAGEM_KEY,
        "key_delay": DEFAULT_KEY_DELAY,
        "loadout": [],                 # [{"model": "...", "name": "...", "hotkey": "f1"}, ...]
        "mission_hotkeys": {},         # {"增援": "f9", ...}
        "listening_enabled": True,
    }


def load_config(path=None):
    """Load configuration from a JSON file. Returns default config if file doesn't exist."""
    if path is None:
        path = DEFAULT_CONFIG_PATH

    default = _make_default()

    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults so missing keys get filled in
        config = dict(default)
        if "key_bindings" in data and isinstance(data["key_bindings"], dict):
            config["key_bindings"] = data["key_bindings"]
        if "stratagem_key" in data and isinstance(data["stratagem_key"], str):
            config["stratagem_key"] = data["stratagem_key"]
        if "key_delay" in data:
            config["key_delay"] = float(data["key_delay"])
        if "loadout" in data and isinstance(data["loadout"], list):
            config["loadout"] = data["loadout"]
        if "mission_hotkeys" in data and isinstance(data["mission_hotkeys"], dict):
            config["mission_hotkeys"] = data["mission_hotkeys"]
        if "listening_enabled" in data:
            config["listening_enabled"] = bool(data["listening_enabled"])
        return config
    except (json.JSONDecodeError, ValueError, OSError):
        return default


def save_config(config, path=None):
    """Save configuration to a JSON file."""
    if path is None:
        path = DEFAULT_CONFIG_PATH

    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_key_for_direction(direction, config):
    """Get the keyboard key mapped to a direction arrow."""
    return config["key_bindings"].get(direction, direction)
