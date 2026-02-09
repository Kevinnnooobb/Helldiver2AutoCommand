"""
按键与负载配置管理。
Manages direction bindings, stratagem activation key,
loadout slots with slot-level hotkeys, and named profiles.
"""

import json
import os

# Default config file path (next to this script)
_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(_DIR, "config.json")
PROFILES_DIR = os.path.join(_DIR, "profiles")

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

# Fixed 10 slots (2x5 grid)
SLOT_COUNT = 10


def _make_default():
    """Return a fresh default config dict."""
    return {
        "key_bindings": dict(DEFAULT_KEY_BINDINGS),
        "stratagem_key": DEFAULT_STRATAGEM_KEY,
        "key_delay": DEFAULT_KEY_DELAY,
        "slot_hotkeys": {},            # {"0": "f1", ...}
        "loadout": [None] * SLOT_COUNT,
        "listening_enabled": True,
        "last_profile": "",
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
        config = dict(default)
        if "key_bindings" in data and isinstance(data["key_bindings"], dict):
            config["key_bindings"] = data["key_bindings"]
        if "stratagem_key" in data and isinstance(data["stratagem_key"], str):
            config["stratagem_key"] = data["stratagem_key"]
        if "key_delay" in data:
            config["key_delay"] = float(data["key_delay"])
        if "slot_hotkeys" in data and isinstance(data.get("slot_hotkeys"), dict):
            config["slot_hotkeys"] = {
                k: v for k, v in data["slot_hotkeys"].items()
                if k.isdigit()
            }
        if "loadout" in data and isinstance(data.get("loadout"), list):
            raw = data["loadout"]
            # Pad / truncate to SLOT_COUNT
            config["loadout"] = (raw + [None] * SLOT_COUNT)[:SLOT_COUNT]
        if "listening_enabled" in data:
            config["listening_enabled"] = bool(data["listening_enabled"])
        if "last_profile" in data:
            config["last_profile"] = str(data["last_profile"])
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


# ─── Profile 管理 ───────────────────────────────────────────

def _ensure_profiles_dir():
    os.makedirs(PROFILES_DIR, exist_ok=True)


def list_profiles() -> list[str]:
    """Return sorted list of profile names (without .json extension)."""
    _ensure_profiles_dir()
    names = []
    for fn in os.listdir(PROFILES_DIR):
        if fn.endswith(".json"):
            names.append(fn[:-5])
    names.sort()
    return names


def save_profile(name: str, loadout: list, slot_hotkeys: dict):
    """Save a named profile (loadout + hotkeys)."""
    _ensure_profiles_dir()
    data = {"loadout": loadout, "slot_hotkeys": slot_hotkeys}
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_profile(name: str) -> dict | None:
    """Load a named profile. Returns dict with 'loadout' and 'slot_hotkeys', or None."""
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        loadout = data.get("loadout", [None] * SLOT_COUNT)
        loadout = (loadout + [None] * SLOT_COUNT)[:SLOT_COUNT]
        return {
            "loadout": loadout,
            "slot_hotkeys": data.get("slot_hotkeys", {}),
        }
    except (json.JSONDecodeError, OSError):
        return None


def delete_profile(name: str):
    """Delete a named profile."""
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
