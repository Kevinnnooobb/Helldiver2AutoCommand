"""
按键与负载配置管理。
Manages direction bindings, stratagem activation key, per-stratagem hotkeys,
and loadout slots with slot-level hotkeys for quick in-game triggers.
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

# Loadout slots: 0-3 为常用战备，4 为常驻任务战备
DEFAULT_LOADOUT = [None, None, None, None, None]


def _make_default():
    """Return a fresh default config dict."""
    return {
        "key_bindings": dict(DEFAULT_KEY_BINDINGS),
        "stratagem_key": DEFAULT_STRATAGEM_KEY,
        "key_delay": DEFAULT_KEY_DELAY,
        "stratagem_hotkeys": {},       # {"key_name": {"model": "...", "name": "..."}}
        "slot_hotkeys": {},            # {"0": "f1", ...}
        "loadout": list(DEFAULT_LOADOUT),
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
        if "stratagem_hotkeys" in data and isinstance(data["stratagem_hotkeys"], dict):
            config["stratagem_hotkeys"] = data["stratagem_hotkeys"]
        if "slot_hotkeys" in data and isinstance(data.get("slot_hotkeys"), dict):
            config["slot_hotkeys"] = data["slot_hotkeys"]
        if "loadout" in data and isinstance(data.get("loadout"), list):
            # 保证长度为 5
            cfg_loadout = data["loadout"][:5] + [None] * max(0, 5 - len(data["loadout"]))
            config["loadout"] = cfg_loadout
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
