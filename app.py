"""
绝地潜兵2 自动呼叫战备 — PyQt6 界面 (v3 Redesign)
Helldivers 2 Auto Stratagem Caller — PyQt6 GUI

Layout:
  ┌─────────────────────────────────────────────────────┐
  │  上部：设置栏 + Profile 管理                         │
  ├─────────────────────────────────────────────────────┤
  │  下部：2×5 战备选择网格                              │
  │  点击按钮 → 1 级分类菜单 → 2 级选择具体战备           │
  └─────────────────────────────────────────────────────┘
"""

import sys
import threading
import keyboard

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QDialog, QFormLayout,
    QDoubleSpinBox, QStatusBar, QMenu, QMessageBox,
    QGroupBox, QFrame, QGridLayout, QComboBox, QInputDialog,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QIcon

from stratagems import (
    STRATAGEMS,
    get_categories,
    get_stratagems_by_category,
    command_to_string,
)
from config import (
    load_config, save_config,
    DEFAULT_KEY_BINDINGS, SLOT_COUNT,
    list_profiles, save_profile, load_profile, delete_profile,
)
from executor import execute_stratagem

# ──────────────────────── 按键显示 ────────────────────────

_KEY_DISPLAY = {
    "up": "↑", "down": "↓", "left": "←", "right": "→",
    "right ctrl": "右Ctrl", "left ctrl": "左Ctrl", "ctrl": "Ctrl",
    "right shift": "右Shift", "left shift": "左Shift", "shift": "Shift",
    "right alt": "右Alt", "left alt": "左Alt", "alt": "Alt",
    "space": "空格", "enter": "回车", "tab": "Tab",
    "backspace": "退格", "escape": "Esc", "delete": "Del",
    "insert": "Ins", "home": "Home", "end": "End",
    "page up": "PgUp", "page down": "PgDn",
}
for _i in range(1, 13):
    _KEY_DISPLAY[f"f{_i}"] = f"F{_i}"


def format_key_display(key_name: str) -> str:
    if not key_name:
        return ""
    return _KEY_DISPLAY.get(key_name.lower(), key_name.upper())


# ──────────────────────── 样式表 ────────────────────────

STYLESHEET = """
/* ===================== 全局基础 ===================== */
QMainWindow, QWidget {
    background-color: #0a0b10;
    color: #f0e4a8;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 13px;
}
QLabel { font-size: 13px; }

/* ===================== 顶部工具栏 ===================== */
#topBar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #10111a, stop:0.5 #1a1d28, stop:1 #10111a);
    border: 1px solid #2e2c1e;
    border-radius: 8px;
    padding: 10px 16px;
}

/* ===================== 按钮（通用） ===================== */
QPushButton {
    background-color: #1a1d28;
    color: #f0e4a8;
    border: 1px solid #d4a825;
    border-radius: 6px;
    padding: 7px 14px;
    font-size: 13px;
    font-weight: 600;
    min-height: 18px;
}
QPushButton:hover {
    background-color: #252838;
    border-color: #f5c842;
    color: #fff;
}
QPushButton:pressed {
    background-color: #f5c842;
    color: #0a0b10;
    border-color: #f5c842;
}
QPushButton:disabled {
    color: #5c5228;
    border-color: #332c14;
    background-color: #12131a;
}

/* 监听按钮 */
QPushButton#listenBtn[active="true"] {
    border-color: #4be85c;
    color: #4be85c;
    font-weight: 700;
}

/* 按键捕获按钮 */
QPushButton#captureBtn {
    border-color: #6d5a1a;
    min-width: 100px;
    padding: 6px 10px;
    font-size: 12px;
}
QPushButton#captureBtn:hover { border-color: #f5c842; color: #fff; }
QPushButton#captureBtn[capturing="true"] {
    border-color: #ffa500;
    color: #ffa500;
    font-weight: 700;
}

/* ===================== 战备槽位按钮 ===================== */
QPushButton#slotBtn {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #161924, stop:1 #0f1018);
    border: 2px solid #2e2c1e;
    border-radius: 10px;
    color: #6a5e30;
    font-size: 13px;
    font-weight: 600;
    padding: 10px 6px;
    min-height: 100px;
}
QPushButton#slotBtn:hover {
    border-color: #d4a825;
    color: #f0e4a8;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #1e2130, stop:1 #141620);
}
QPushButton#slotBtn[filled="true"] {
    border-color: #f5c842;
    color: #f5c842;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #1a1812, stop:1 #12110d);
}
QPushButton#slotBtn[filled="true"]:hover {
    border-color: #ffe066;
    color: #fff;
}

/* ===================== 下拉框 ===================== */
QComboBox {
    background-color: #131520;
    color: #f0e4a8;
    border: 1px solid #4a3b15;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    min-width: 160px;
}
QComboBox:focus { border-color: #f5c842; }
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #141620;
    color: #f0e4a8;
    border: 1px solid #2e2c1e;
    selection-background-color: #2a2d3a;
    selection-color: #fff;
}

/* ===================== 输入框 ===================== */
QLineEdit {
    background-color: #131520;
    color: #f0e4a8;
    border: 1px solid #4a3b15;
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
    selection-background-color: #f5c842;
    selection-color: #0a0b10;
}
QLineEdit:focus { border-color: #f5c842; }

/* ===================== 菜单 ===================== */
QMenu {
    background-color: #141620;
    color: #f0e4a8;
    border: 1px solid #2e2c1e;
    border-radius: 6px;
    padding: 4px;
    font-size: 13px;
}
QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #2a2d3a;
    color: #fff;
}
QMenu::separator {
    height: 1px;
    background: #2e2c1e;
    margin: 4px 8px;
}

/* ===================== 分组框 ===================== */
QGroupBox {
    border: 1px solid #2e2c1e;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 16px;
    color: #f5c842;
    font-weight: bold;
    font-size: 13px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
}

/* ===================== 状态栏 ===================== */
QStatusBar {
    background: #0c0d14;
    color: #d4c674;
    border-top: 1px solid #2e2c1e;
    font-size: 12px;
    padding: 3px 8px;
}

/* ===================== 对话框 ===================== */
QDialog {
    background-color: #0e0f16;
    color: #f0e4a8;
}
QDoubleSpinBox {
    background-color: #131520;
    color: #f0e4a8;
    border: 1px solid #4a3b15;
    border-radius: 5px;
    padding: 5px 8px;
    font-size: 13px;
}
QDoubleSpinBox:focus { border-color: #f5c842; }

/* ===================== 网格区域标题 ===================== */
#gridTitle {
    font-size: 18px;
    font-weight: 800;
    color: #f5c842;
    letter-spacing: 2px;
    padding: 6px 0;
}
#gridSubtitle {
    color: #9c8b48;
    font-size: 12px;
}

/* ===================== 分隔线 ===================== */
#separator {
    background-color: #2e2c1e;
    min-height: 1px;
    max-height: 1px;
}
"""

# ──────────────────────── 按键捕获按钮 ────────────────────

class KeyCaptureButton(QPushButton):
    key_captured = pyqtSignal(str)
    _key_ready = pyqtSignal(str)

    def __init__(self, current_key: str = "", parent=None):
        label = format_key_display(current_key) if current_key else "点击捕获"
        super().__init__(label, parent)
        self.setObjectName("captureBtn")
        self._current = current_key
        self._capturing = False
        self._hook = None
        self.clicked.connect(self._start)
        self._key_ready.connect(self._finish)

    def get_key(self) -> str:
        return self._current

    def set_key(self, key_name: str):
        self._current = key_name
        self.setText(format_key_display(key_name) if key_name else "点击捕获")

    def _start(self):
        if self._capturing:
            return
        self._capturing = True
        self.setProperty("capturing", True)
        self.style().unpolish(self)
        self.style().polish(self)
        self.setText("⌨ 按下按键…")
        self._hook = keyboard.on_press(self._on_key)

    def _on_key(self, event):
        if not self._capturing:
            return
        self._capturing = False
        if self._hook:
            try:
                keyboard.unhook(self._hook)
            except Exception:
                pass
            self._hook = None
        self._key_ready.emit(event.name)

    def _finish(self, key_name: str):
        self._current = key_name
        self.setText(format_key_display(key_name))
        self.setProperty("capturing", False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.key_captured.emit(key_name)

    def cleanup(self):
        if self._hook:
            try:
                keyboard.unhook(self._hook)
            except Exception:
                pass
            self._hook = None
        self._capturing = False


# ──────────────────────── 设置对话框 ────────────────────

class SettingsDialog(QDialog):
    def __init__(self, parent=None, config: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("⚙ 按键设置")
        self.setFixedSize(420, 380)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.config = config or {}
        self._captures: dict[str, KeyCaptureButton] = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        dir_group = QGroupBox("方向键绑定（点击后按目标键）")
        dir_layout = QFormLayout(dir_group)
        for label_text, direction in [("↑ 上", "↑"), ("↓ 下", "↓"), ("← 左", "←"), ("→ 右", "→")]:
            current = self.config.get("key_bindings", {}).get(direction, DEFAULT_KEY_BINDINGS[direction])
            btn = KeyCaptureButton(current, self)
            btn.setFixedWidth(140)
            self._captures[direction] = btn
            dir_layout.addRow(QLabel(label_text), btn)
        layout.addWidget(dir_group)

        misc = QGroupBox("战备激活键与延迟")
        misc_layout = QFormLayout(misc)
        strat_btn = KeyCaptureButton(self.config.get("stratagem_key", "ctrl"), self)
        strat_btn.setFixedWidth(140)
        self._captures["stratagem_key"] = strat_btn
        misc_layout.addRow(QLabel("战备激活键"), strat_btn)

        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.01, 1.0)
        self.delay_spin.setSingleStep(0.01)
        self.delay_spin.setDecimals(3)
        self.delay_spin.setValue(self.config.get("key_delay", 0.05))
        self.delay_spin.setSuffix(" 秒")
        self.delay_spin.setFixedWidth(140)
        misc_layout.addRow(QLabel("按键延迟"), self.delay_spin)
        layout.addWidget(misc)

        row = QHBoxLayout()
        reset_btn = QPushButton("恢复默认")
        reset_btn.clicked.connect(self._reset)
        save_btn = QPushButton("保存")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        row.addWidget(reset_btn)
        row.addStretch()
        row.addWidget(cancel_btn)
        row.addWidget(save_btn)
        layout.addLayout(row)

    def _reset(self):
        for direction, default_key in DEFAULT_KEY_BINDINGS.items():
            self._captures[direction].set_key(default_key)
        self._captures["stratagem_key"].set_key("ctrl")
        self.delay_spin.setValue(0.05)

    def get_result(self) -> dict:
        bindings = {d: self._captures[d].get_key() for d in ("↑", "↓", "←", "→")}
        return {
            "key_bindings": bindings,
            "stratagem_key": self._captures["stratagem_key"].get_key(),
            "key_delay": self.delay_spin.value(),
        }

    def closeEvent(self, a0):
        for btn in self._captures.values():
            btn.cleanup()
        super().closeEvent(a0)


# ──────────────────────── 主窗口 ────────────────────

class StratagemApp(QMainWindow):
    _slot_triggered = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("绝地潜兵2 — 自动呼叫战备")
        self.resize(960, 620)
        self.setMinimumSize(800, 520)

        self.config = load_config()
        self._listening = False
        self._executing = False
        self._capture_mode = False
        self._global_hook = None

        # 固定 10 槽位 (2×5)，每次启动为空
        self.loadout: list[dict | None] = [None] * SLOT_COUNT
        self.slot_hotkeys: dict[str, str] = {}
        self.slot_key_map: dict[str, int] = {}
        self._rebuild_slot_key_map()

        self._build_ui()
        self._slot_triggered.connect(self._execute_slot)

        if self.config.get("listening_enabled", True):
            self._start_listening()

    # ─────────── 槽位键映射 ───────────
    def _rebuild_slot_key_map(self):
        self.slot_key_map.clear()
        for slot_str, key in self.slot_hotkeys.items():
            if key:
                self.slot_key_map[key] = int(slot_str)

    # ─────────── UI 构建 ───────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 10, 14, 6)
        root.setSpacing(10)

        # ═══════ 上部：工具栏 ═══════
        self._build_top_bar(root)

        # 分隔线
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)

        # ═══════ 下部：2×5 战备网格 ═══════
        self._build_grid(root)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel()
        self.listen_status_label = QLabel()
        self.status_bar.addWidget(self.status_label, 1)
        self.status_bar.addPermanentWidget(self.listen_status_label)
        self._update_status("就绪 — 点击槽位选择战备")

    # ─── 上部工具栏 ───
    def _build_top_bar(self, parent_layout: QVBoxLayout):
        bar = QFrame()
        bar.setObjectName("topBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

        # 标题
        title = QLabel("⚡ HD2 战备助手")
        title.setStyleSheet("font-size:16px; font-weight:800; letter-spacing:1px;")
        layout.addWidget(title)
        layout.addSpacing(16)

        # Profile 管理
        layout.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(140)
        self.profile_combo.setEditable(False)
        self._refresh_profile_combo()
        layout.addWidget(self.profile_combo)

        save_prof_btn = QPushButton("💾 保存")
        save_prof_btn.setToolTip("保存当前负载为 Profile")
        save_prof_btn.clicked.connect(self._save_profile)
        layout.addWidget(save_prof_btn)

        load_prof_btn = QPushButton("📂 读取")
        load_prof_btn.setToolTip("读取选中的 Profile")
        load_prof_btn.clicked.connect(self._load_profile)
        layout.addWidget(load_prof_btn)

        del_prof_btn = QPushButton("🗑 删除")
        del_prof_btn.setToolTip("删除选中的 Profile")
        del_prof_btn.clicked.connect(self._delete_profile)
        layout.addWidget(del_prof_btn)

        layout.addStretch()

        # 清空全部
        clear_btn = QPushButton("✕ 清空全部")
        clear_btn.setStyleSheet(
            "border-color:#e85c5c; color:#e85c5c; font-size:12px; padding:5px 10px;"
        )
        clear_btn.clicked.connect(self._clear_all_slots)
        layout.addWidget(clear_btn)

        # 监听按钮
        self.listen_btn = QPushButton("○ 监听关")
        self.listen_btn.setObjectName("listenBtn")
        self.listen_btn.setMinimumWidth(90)
        self.listen_btn.clicked.connect(self._toggle_listening)
        layout.addWidget(self.listen_btn)

        # 设置按钮
        settings_btn = QPushButton("⚙ 设置")
        settings_btn.setMinimumWidth(70)
        settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(settings_btn)

        parent_layout.addWidget(bar)

    # ─── 下部 2×5 网格 ───
    def _build_grid(self, parent_layout: QVBoxLayout):
        header = QHBoxLayout()
        lbl = QLabel("⚔ 战备栏位")
        lbl.setObjectName("gridTitle")
        header.addWidget(lbl)
        header.addStretch()
        sub = QLabel("点击槽位选择战备，右键清除 / 执行")
        sub.setObjectName("gridSubtitle")
        header.addWidget(sub)
        parent_layout.addLayout(header)

        grid = QGridLayout()
        grid.setSpacing(10)
        self.slot_buttons: list[QPushButton] = []

        for idx in range(SLOT_COUNT):
            btn = self._create_slot_button(idx)
            row = idx // 5
            col = idx % 5
            grid.addWidget(btn, row, col)
            self.slot_buttons.append(btn)

        parent_layout.addLayout(grid, 1)

    def _create_slot_button(self, idx: int) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("slotBtn")
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn.setMinimumSize(140, 110)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        btn.clicked.connect(lambda _=False, i=idx: self._show_stratagem_menu(i))
        btn.customContextMenuRequested.connect(lambda pos, i=idx: self._show_slot_context_menu(i, pos))
        self._update_slot_button(btn, idx, self.loadout[idx])
        return btn

    def _display_name(self, s: dict) -> str:
        model = s.get("model", "")
        name = s.get("name", "")
        if model and model != "无型号":
            return f"{model}\n{name}"
        return name

    def _update_slot_button(self, btn: QPushButton, idx: int, item: dict | None):
        """Update a slot button's text and style."""
        hk = self.slot_hotkeys.get(str(idx), "")
        hk_text = f"  [{format_key_display(hk)}]" if hk else ""
        slot_label = f"槽{idx + 1}{hk_text}"

        if item is None:
            btn.setText(f"{slot_label}\n\n— EMPTY —")
            btn.setProperty("filled", False)
        else:
            # Find full stratagem data
            strat = self._find_stratagem(item)
            if strat:
                cmd = command_to_string(strat["command"])
                name = self._display_name(strat)
                btn.setText(f"{slot_label}\n\n{name}\n{cmd}")
            else:
                btn.setText(f"{slot_label}\n\n{item.get('name', '?')}")
            btn.setProperty("filled", True)

        btn.style().unpolish(btn)
        btn.style().polish(btn)

    def _refresh_all_slot_buttons(self):
        for idx, btn in enumerate(self.slot_buttons):
            self._update_slot_button(btn, idx, self.loadout[idx])

    # ─────────── 级联菜单：选择战备 ───────────
    def _show_stratagem_menu(self, slot_idx: int):
        menu = QMenu(self)
        menu.setMinimumWidth(200)

        categories = get_categories()
        for cat in categories:
            sub_menu = menu.addMenu(cat)
            if sub_menu is None:
                continue
            sub_menu.setMinimumWidth(240)
            stratagems = get_stratagems_by_category(cat)
            for s in stratagems:
                name = self._display_name(s).replace("\n", "  ")
                cmd = command_to_string(s["command"])
                act = sub_menu.addAction(f"{name}   {cmd}")
                act.setData(s)

        chosen = menu.exec(self.slot_buttons[slot_idx].mapToGlobal(
            self.slot_buttons[slot_idx].rect().center()
        ))
        if chosen is not None:
            strat = chosen.data()
            if strat:
                self._assign_to_slot(slot_idx, strat)

    # ─────────── 右键菜单 ───────────
    def _show_slot_context_menu(self, slot_idx: int, pos):
        menu = QMenu(self)
        item = self.loadout[slot_idx]

        if item:
            exec_act = menu.addAction("▶ 执行")
            clear_act = menu.addAction("✕ 清除")
            menu.addSeparator()
        else:
            exec_act = None
            clear_act = None

        select_act = menu.addAction("☰ 选择战备…")
        menu.addSeparator()

        # 快捷键设置
        hk_act = menu.addAction("⌨ 设置快捷键…")
        hk_clear_act = menu.addAction("⌨ 清除快捷键")

        btn = self.slot_buttons[slot_idx]
        chosen = menu.exec(btn.mapToGlobal(pos))
        if chosen is None:
            return

        if chosen == exec_act and item:
            self._execute_slot(slot_idx)
        elif chosen == clear_act:
            self._clear_slot(slot_idx)
        elif chosen == select_act:
            self._show_stratagem_menu(slot_idx)
        elif chosen == hk_act:
            self._capture_slot_hotkey(slot_idx)
        elif chosen == hk_clear_act:
            self._set_slot_hotkey(slot_idx, "")

    # ─────────── 快捷键捕获 ───────────
    def _capture_slot_hotkey(self, slot_idx: int):
        """Open a small dialog to capture a hotkey for this slot."""
        self._capture_mode = True
        dlg = QDialog(self)
        dlg.setWindowTitle(f"槽{slot_idx + 1} 快捷键")
        dlg.setFixedSize(280, 120)
        dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel(f"为槽 {slot_idx + 1} 按下快捷键…"))
        cap = KeyCaptureButton(self.slot_hotkeys.get(str(slot_idx), ""), dlg)
        cap.setFixedWidth(180)
        layout.addWidget(cap, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dlg.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dlg.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._set_slot_hotkey(slot_idx, cap.get_key())
        cap.cleanup()
        self._capture_mode = False

    # ─────────── 槽位操作 ───────────
    def _assign_to_slot(self, idx: int, stratagem: dict):
        self.loadout[idx] = {"model": stratagem["model"], "name": stratagem["name"]}
        self._update_slot_button(self.slot_buttons[idx], idx, self.loadout[idx])
        self._persist_loadout()
        self._update_status(f"槽 {idx + 1} ← {stratagem['name']}")

    def _clear_slot(self, idx: int):
        self.loadout[idx] = None
        self._update_slot_button(self.slot_buttons[idx], idx, None)
        self._persist_loadout()
        self._update_status(f"槽 {idx + 1} 已清除")

    def _clear_all_slots(self):
        for idx in range(SLOT_COUNT):
            self.loadout[idx] = None
        self.slot_hotkeys.clear()
        self._rebuild_slot_key_map()
        self._refresh_all_slot_buttons()
        self._persist_loadout()
        self._update_status("已清空全部槽位")

    def _execute_slot(self, idx: int):
        strat = self._find_stratagem_from_loadout(idx)
        if strat:
            self._execute_stratagem(strat)

    # ─────────── 查找战备 ───────────
    def _find_stratagem(self, item: dict | None) -> dict | None:
        if not item:
            return None
        for s in STRATAGEMS:
            if s["model"] == item.get("model") and s["name"] == item.get("name"):
                return s
        return None

    def _find_stratagem_from_loadout(self, idx: int) -> dict | None:
        if idx < 0 or idx >= SLOT_COUNT:
            return None
        return self._find_stratagem(self.loadout[idx])

    # ─────────── 执行 ───────────
    def _execute_stratagem(self, stratagem: dict):
        if self._executing:
            return
        self._executing = True
        name = stratagem["name"]
        cmd = command_to_string(stratagem["command"])
        self._update_status(f"正在执行: {name} ({cmd}) …")
        thread = threading.Thread(target=self._exec_thread, args=(stratagem,), daemon=True)
        thread.start()

    def _exec_thread(self, stratagem: dict):
        try:
            execute_stratagem(stratagem, self.config)
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._update_status(f"✔ 已执行: {stratagem['name']}"))
        except Exception as exc:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "执行错误", str(exc)))
        finally:
            self._executing = False

    # ─────────── 快捷键管理 ───────────
    def _set_slot_hotkey(self, idx: int, key: str):
        if key:
            # 去重
            for slot_str, k in list(self.slot_hotkeys.items()):
                if k == key:
                    self.slot_hotkeys.pop(slot_str, None)
            self.slot_hotkeys[str(idx)] = key
        else:
            self.slot_hotkeys.pop(str(idx), None)

        self._rebuild_slot_key_map()
        self._update_slot_button(self.slot_buttons[idx], idx, self.loadout[idx])
        self._persist_loadout()
        self._update_status(
            f"槽 {idx + 1} 快捷键 → {format_key_display(key)}" if key
            else f"槽 {idx + 1} 快捷键已清除"
        )

    # ─────────── Profile 管理 ───────────
    def _refresh_profile_combo(self):
        self.profile_combo.clear()
        self.profile_combo.addItem("（未选择）")
        for name in list_profiles():
            self.profile_combo.addItem(name)

    def _save_profile(self):
        name, ok = QInputDialog.getText(
            self, "保存 Profile", "请输入 Profile 名称:",
            text=self.profile_combo.currentText() if self.profile_combo.currentIndex() > 0 else "",
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        save_profile(name, self.loadout, self.slot_hotkeys)
        self.config["last_profile"] = name
        save_config(self.config)
        self._refresh_profile_combo()
        # 选中刚保存的
        idx = self.profile_combo.findText(name)
        if idx >= 0:
            self.profile_combo.setCurrentIndex(idx)
        self._update_status(f"Profile \"{name}\" 已保存")

    def _load_profile(self):
        idx = self.profile_combo.currentIndex()
        if idx <= 0:
            QMessageBox.information(self, "提示", "请先选择一个 Profile")
            return
        name = self.profile_combo.currentText()
        data = load_profile(name)
        if data is None:
            QMessageBox.warning(self, "错误", f"无法读取 Profile \"{name}\"")
            return
        self.loadout = data["loadout"]
        self.slot_hotkeys = data.get("slot_hotkeys", {})
        self._rebuild_slot_key_map()
        self._refresh_all_slot_buttons()
        self._persist_loadout()
        self.config["last_profile"] = name
        save_config(self.config)
        self._update_status(f"已载入 Profile \"{name}\"")

    def _delete_profile(self):
        idx = self.profile_combo.currentIndex()
        if idx <= 0:
            QMessageBox.information(self, "提示", "请先选择一个 Profile")
            return
        name = self.profile_combo.currentText()
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定删除 Profile \"{name}\"？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        delete_profile(name)
        self._refresh_profile_combo()
        self._update_status(f"Profile \"{name}\" 已删除")

    # ─────────── 持久化 ───────────
    def _persist_loadout(self):
        self.config["loadout"] = self.loadout
        self.config["slot_hotkeys"] = self.slot_hotkeys
        save_config(self.config)

    # ─────────── 全局监听 ───────────
    def _start_listening(self):
        if self._global_hook is not None:
            return
        self._global_hook = keyboard.on_press(self._on_global_key)
        self._listening = True
        self._update_listen_ui()

    def _stop_listening(self):
        if self._global_hook is not None:
            try:
                keyboard.unhook(self._global_hook)
            except Exception:
                pass
            self._global_hook = None
        self._listening = False
        self._update_listen_ui()

    def _toggle_listening(self):
        if self._listening:
            self._stop_listening()
        else:
            self._start_listening()

    def _on_global_key(self, event):
        if self._capture_mode or self._executing:
            return
        key = event.name
        if key in self.slot_key_map:
            self._slot_triggered.emit(self.slot_key_map[key])

    def _update_listen_ui(self):
        if self._listening:
            self.listen_btn.setText("● 监听开")
            self.listen_btn.setProperty("active", True)
        else:
            self.listen_btn.setText("○ 监听关")
            self.listen_btn.setProperty("active", False)
        self.listen_btn.style().unpolish(self.listen_btn)
        self.listen_btn.style().polish(self.listen_btn)

        slots_bound = sum(1 for k in self.slot_hotkeys.values() if k)
        self.listen_status_label.setText(
            f"快捷键 {slots_bound} | {'● 监听中' if self._listening else '○ 未监听'}"
        )
        self.listen_status_label.setStyleSheet(
            "color:#4be85c;" if self._listening else "color:#666;"
        )

    # ─────────── 设置对话框 ───────────
    def _open_settings(self):
        self._capture_mode = True
        dialog = SettingsDialog(self, self.config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            self.config["key_bindings"] = result["key_bindings"]
            self.config["stratagem_key"] = result["stratagem_key"]
            self.config["key_delay"] = result["key_delay"]
            save_config(self.config)
            self._update_status("按键设置已保存")
        self._capture_mode = False

    # ─────────── 状态 ───────────
    def _update_status(self, text: str = ""):
        self.status_label.setText(text)
        self._update_listen_ui()

    # ─────────── 键盘快捷 ───────────
    def keyPressEvent(self, a0):
        if a0 is None:
            return
        key = a0.key()
        if key == Qt.Key.Key_F5:
            self._toggle_listening()
        else:
            super().keyPressEvent(a0)

    # ─────────── 关闭清理 ───────────
    def closeEvent(self, a0):
        self.config["listening_enabled"] = self._listening
        save_config(self.config)
        self._stop_listening()
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        if a0:
            a0.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = StratagemApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
