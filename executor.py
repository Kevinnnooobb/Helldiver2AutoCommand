"""
战备指令执行器
Executes stratagem commands by simulating keyboard input.

直接调用 Windows SendInput API 发送硬件扫描码，
并为右 Ctrl 等扩展键正确设置 KEYEVENTF_EXTENDEDKEY 标志。
这比 keyboard 库的 keybd_event 方式更可靠，绝大多数游戏都能识别。
"""

import ctypes
import ctypes.wintypes
import time
import logging

logger = logging.getLogger(__name__)

# ─── Windows SendInput 常量与结构 ──────────────────────────────────

INPUT_KEYBOARD = 1
KEYEVENTF_SCANCODE    = 0x0008   # wScan 字段包含扫描码
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001   # 扩展键（右Ctrl/Alt、方向键、Insert 等）


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk",         ctypes.wintypes.WORD),
        ("wScan",       ctypes.wintypes.WORD),
        ("dwFlags",     ctypes.wintypes.DWORD),
        ("time",        ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx",          ctypes.wintypes.LONG),
        ("dy",          ctypes.wintypes.LONG),
        ("mouseData",   ctypes.wintypes.DWORD),
        ("dwFlags",     ctypes.wintypes.DWORD),
        ("time",        ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg",    ctypes.wintypes.DWORD),
        ("wParamL", ctypes.wintypes.WORD),
        ("wParamH", ctypes.wintypes.WORD),
    ]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type",  ctypes.wintypes.DWORD),
        ("union", _INPUT_UNION),
    ]


_user32 = ctypes.windll.user32
_SendInput = _user32.SendInput
_SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
_SendInput.restype  = ctypes.c_uint

_GetAsyncKeyState = _user32.GetAsyncKeyState
_GetAsyncKeyState.argtypes = [ctypes.c_int]
_GetAsyncKeyState.restype  = ctypes.wintypes.SHORT

# 虚拟键码，用于 GetAsyncKeyState 检测按键状态
VK_LSHIFT   = 0xA0
VK_RSHIFT   = 0xA1
VK_LCONTROL = 0xA2
VK_RCONTROL = 0xA3
VK_LMENU    = 0xA4   # Left Alt
VK_RMENU    = 0xA5   # Right Alt

# 需要在执行战备前临时释放的修饰键 (vk_code, key_name)
_MODIFIERS_TO_RELEASE = [
    (VK_LSHIFT,  "left shift"),
    (VK_RSHIFT,  "right shift"),
    (VK_LMENU,   "left alt"),
    (VK_RMENU,   "right alt"),
]

# ─── 硬件扫描码表 (scan_code, is_extended) ─────────────────────────
# 参考：https://www.win.tue.nl/~aeb/linux/kbd/scancodes-1.html

_KEY_MAP: dict[str, tuple[int, bool]] = {
    # 方向键（扩展键）
    "up":           (0x48, True),
    "down":         (0x50, True),
    "left":         (0x4B, True),
    "right":        (0x4D, True),

    # 修饰键
    "ctrl":         (0x1D, False),   # 左 Ctrl
    "left ctrl":    (0x1D, False),
    "right ctrl":   (0x1D, True),    # 扩展键
    "alt":          (0x38, False),    # 左 Alt
    "left alt":     (0x38, False),
    "right alt":    (0x38, True),     # 扩展键
    "shift":        (0x2A, False),    # 左 Shift
    "left shift":   (0x2A, False),
    "right shift":  (0x36, False),

    # 功能键
    "esc":          (0x01, False),
    "escape":       (0x01, False),
    "f1":           (0x3B, False),
    "f2":           (0x3C, False),
    "f3":           (0x3D, False),
    "f4":           (0x3E, False),
    "f5":           (0x3F, False),
    "f6":           (0x40, False),
    "f7":           (0x41, False),
    "f8":           (0x42, False),
    "f9":           (0x43, False),
    "f10":          (0x44, False),
    "f11":          (0x57, False),
    "f12":          (0x58, False),

    # 常用键
    "space":        (0x39, False),
    "enter":        (0x1C, False),
    "backspace":    (0x0E, False),
    "tab":          (0x0F, False),
    "caps lock":    (0x3A, False),

    # 数字行
    "1":            (0x02, False),
    "2":            (0x03, False),
    "3":            (0x04, False),
    "4":            (0x05, False),
    "5":            (0x06, False),
    "6":            (0x07, False),
    "7":            (0x08, False),
    "8":            (0x09, False),
    "9":            (0x0A, False),
    "0":            (0x0B, False),

    # 字母键
    "q": (0x10, False), "w": (0x11, False), "e": (0x12, False),
    "r": (0x13, False), "t": (0x14, False), "y": (0x15, False),
    "u": (0x16, False), "i": (0x17, False), "o": (0x18, False),
    "p": (0x19, False), "a": (0x1E, False), "s": (0x1F, False),
    "d": (0x20, False), "f": (0x21, False), "g": (0x22, False),
    "h": (0x23, False), "j": (0x24, False), "k": (0x25, False),
    "l": (0x26, False), "z": (0x2C, False), "x": (0x2D, False),
    "c": (0x2E, False), "v": (0x2F, False), "b": (0x30, False),
    "n": (0x31, False), "m": (0x32, False),

    # 特殊扩展键
    "insert":       (0x52, True),
    "delete":       (0x53, True),
    "home":         (0x47, True),
    "end":          (0x4F, True),
    "page up":      (0x49, True),
    "page down":    (0x51, True),

    # 小键盘 Enter（扩展键）
    "num enter":    (0x1C, True),
}


def _lookup_key(key_name: str) -> tuple[int, bool]:
    """查找按键的 (硬件扫描码, 是否扩展键)。"""
    low = key_name.lower().strip()
    # 直接匹配
    if low in _KEY_MAP:
        return _KEY_MAP[low]
    # 尝试别名
    aliases = {
        "control": "ctrl", "left control": "left ctrl",
        "right control": "right ctrl", "return": "enter",
    }
    alias = aliases.get(low)
    if alias and alias in _KEY_MAP:
        return _KEY_MAP[alias]
    raise ValueError(f"未知按键: {key_name!r}，请在 _KEY_MAP 中添加")


def _send_key_event(scan_code: int, extended: bool, key_up: bool):
    """通过 SendInput 发送单个键盘事件。"""
    flags = KEYEVENTF_SCANCODE
    if extended:
        flags |= KEYEVENTF_EXTENDEDKEY
    if key_up:
        flags |= KEYEVENTF_KEYUP

    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = 0
    inp.union.ki.wScan = scan_code
    inp.union.ki.dwFlags = flags
    inp.union.ki.time = 0
    inp.union.ki.dwExtraInfo = None

    result = _SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    if result != 1:
        logger.warning("SendInput 失败, scan=0x%02X ext=%s up=%s", scan_code, extended, key_up)


def _press_key(key_name: str):
    """按下一个键。"""
    sc, ext = _lookup_key(key_name)
    _send_key_event(sc, ext, key_up=False)


def _release_key(key_name: str):
    """释放一个键。"""
    sc, ext = _lookup_key(key_name)
    _send_key_event(sc, ext, key_up=True)


def _is_key_pressed(vk_code: int) -> bool:
    """通过 GetAsyncKeyState 判断某个键是否正被按下。"""
    return (_GetAsyncKeyState(vk_code) & 0x8000) != 0


def _release_held_modifiers() -> list[str]:
    """释放当前按住的修饰键(Shift/Alt)，返回被释放的键名列表。"""
    released = []
    for vk, name in _MODIFIERS_TO_RELEASE:
        if _is_key_pressed(vk):
            sc, ext = _lookup_key(name)
            _send_key_event(sc, ext, key_up=True)
            released.append(name)
            logger.debug("临时释放修饰键: %s", name)
    return released


def _restore_modifiers(keys: list[str]):
    """重新按下之前被临时释放的修饰键。"""
    for name in keys:
        sc, ext = _lookup_key(name)
        _send_key_event(sc, ext, key_up=False)
        logger.debug("恢复修饰键: %s", name)


def execute_stratagem(stratagem, config, keyboard_module=None):
    """
    Execute a stratagem command sequence by simulating key presses.

    Uses Windows SendInput API directly for maximum game compatibility.

    Args:
        stratagem: A stratagem dict with a 'command' list of direction arrows.
        config: Configuration dict with 'key_bindings', 'stratagem_key', 'key_delay'.
        keyboard_module: Unused, kept for API compatibility.
    """
    key_bindings = config["key_bindings"]
    stratagem_key = config["stratagem_key"]
    key_delay = config.get("key_delay", 0.05)
    command = stratagem["command"]

    logger.info(
        "执行战备: %s (%s) - 指令: %s  [激活键=%s]",
        stratagem["name"],
        stratagem["model"],
        "".join(command),
        stratagem_key,
    )

    # Hold down the stratagem activation key
    # 不释放已按住的修饰键（如左Shift奔跑），游戏支持同时奔跑和呼叫战备
    _press_key(stratagem_key)
    time.sleep(key_delay)

    try:
        for direction in command:
            key = key_bindings.get(direction, direction)
            _press_key(key)
            time.sleep(key_delay)
            _release_key(key)
            time.sleep(key_delay)
    finally:
        # Always release the stratagem key
        _release_key(stratagem_key)

    logger.info("战备指令执行完成: %s", stratagem["name"])
