"""
绝地潜兵2 自动呼叫战备 - PyQt6 界面（新版）
Helldivers 2 Auto Stratagem Caller - PyQt6 GUI (redesigned)

Highlights:
- 黑金科幻 UI（更高对比与卡片式排布）
- 左侧「负载」5 槽：4 个常用战备 + 1 个常驻任务战备
- 每槽可绑定独立全局快捷键（按下即在游戏内调用该战备）
- 按键捕获：方向键、激活键、槽快捷键、单个战备快捷键都靠「按下即可」
- 搜索 / 分类浏览，双击立即执行；右键菜单快捷操作
"""

import sys
import threading
import keyboard

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QLabel, QDialog, QFormLayout, QDoubleSpinBox,
    QStatusBar, QHeaderView, QMenu, QMessageBox, QGroupBox,
    QAbstractItemView, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor

from stratagems import (
    STRATAGEMS,
    get_categories,
    get_stratagems_by_category,
    search_stratagems,
    command_to_string,
)
from config import load_config, save_config, DEFAULT_KEY_BINDINGS
from executor import execute_stratagem

# 列索引
COL_MODEL = 0
COL_NAME = 1
COL_COMMAND = 2
COL_HOTKEY = 3
COL_DESC = 4
COLUMN_HEADERS = ["型号", "名称", "指令码", "快捷键", "描述"]

# 按键显示
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

# 样式表 — 深色金属 + 斜切分割
STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0b0c0f;
    color: #f8e287;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 13px;
}

/* 顶部条 */
#topBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #111218, stop:0.5 #1a1c24, stop:1 #111218);
    border: 1px solid #2c2a1a;
    border-radius: 6px;
    padding: 8px;
}

QLineEdit {
    background-color: #151722;
    color: #f8e287;
    border: 1px solid #4a3b15;
    border-radius: 5px;
    padding: 6px 10px;
    selection-background-color: #f5c842;
    selection-color: #0b0c0f;
}
QLineEdit:focus { border-color: #f5c842; }

QPushButton {
    background-color: #161820;
    color: #f8e287;
    border: 1px solid #f5c842;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
}
QPushButton:hover { background-color: #1e2130; border-color: #ffd86a; }
QPushButton:pressed { background-color: #f5c842; color: #0b0c0f; }
QPushButton:disabled { color: #72652c; border-color: #403614; }
QPushButton#executeBtn { border-width: 2px; background-color: #272a36; }
QPushButton#listenBtn[active="true"] { border-color: #4be85c; color: #4be85c; }
QPushButton#captureBtn { border-color: #78621f; min-width: 110px; }
QPushButton#captureBtn[capturing="true"] { border-color: #ffa500; color: #ffa500; }

QTabWidget::pane {
    border: 1px solid #2c2a1a;
    background-color: #101019;
    border-radius: 6px;
}
QTabBar::tab {
    background: #151722;
    color: #b7a04d;
    border: 1px solid #2c2a1a;
    padding: 8px 18px;
    margin-right: 3px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    font-weight: bold;
}
QTabBar::tab:selected { background: #1f2230; color: #f8e287; border-bottom: 2px solid #f5c842; }
QTabBar::tab:hover:!selected { background: #1b1e2a; }

QTableWidget {
    background-color: #101019;
    alternate-background-color: #131624;
    color: #e8d27a;
    border: 1px solid #2c2a1a;
    gridline-color: #26231a;
    selection-background-color: #2c2f3f;
    selection-color: #f8e287;
}
QHeaderView::section {
    background-color: #171a24;
    color: #f8e287;
    border: 1px solid #2c2a1a;
    padding: 6px 8px;
    font-weight: bold;
}

QGroupBox {
    border: 1px solid #2c2a1a;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 14px;
    color: #f5c842;
    font-weight: bold;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }

#cardFrame {
    background: #11141f;
    border: 1px solid #2c2a1a;
    border-radius: 10px;
    padding: 10px;
}
#cardFrame[mission="true"] { border-color: #3f2b00; background: #161922; }
#cardTitle { font-size: 14px; font-weight: 700; color: #f5c842; }
#cardDesc { color: #9c8b48; font-size: 12px; }

QStatusBar {
    background: #0c0d12;
    color: #bfae62;
    border-top: 1px solid #2c2a1a;
    font-size: 12px;
}
"""

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
        self.key_captured.emit(key_name)

    def cleanup(self):
        if self._hook:
            try:
                keyboard.unhook(self._hook)
            except Exception:
                pass
            self._hook = None
        self._capturing = False

class KeyCaptureDialog(QDialog):
    def __init__(self, parent=None, title="设置快捷键"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(340, 180)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.captured_key: str | None = None
        self._hook = keyboard.on_press(self._on_key)
        self._done = False

        layout = QVBoxLayout(self)
        hint = QLabel("请按下要绑定的快捷键")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setFont(QFont("Microsoft YaHei UI", 13))
        layout.addWidget(hint)

        sub = QLabel("支持 F1-F12 / 小键盘 / 方向键 / 右Ctrl 等\n按 Esc 取消 / 按 Del 清除")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color:#9c8b48;")
        layout.addWidget(sub)

        self.key_label = QLabel("")
        self.key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_label.setFont(QFont("Microsoft YaHei UI", 22, QFont.Weight.Bold))
        self.key_label.setStyleSheet("color:#ffa500;")
        layout.addWidget(self.key_label)

    def _on_key(self, event):
        if self._done:
            return
        name = event.name
        if name in ("escape", "esc"):
            self._done = True
            QTimer.singleShot(0, self.reject)
            return
        if name == "delete":
            self._done = True
            self.captured_key = ""
            QTimer.singleShot(0, self.accept)
            return
        self._done = True
        self.captured_key = name
        QTimer.singleShot(0, lambda: self._show_and_accept(name))

    def _show_and_accept(self, key_name: str):
        self.key_label.setText(format_key_display(key_name))
        QTimer.singleShot(250, self.accept)

    def reject(self):
        self._unhook()
        super().reject()

    def _unhook(self):
        if self._hook:
            try:
                keyboard.unhook(self._hook)
            except Exception:
                pass
            self._hook = None

    def closeEvent(self, a0):
        self._unhook()
        super().closeEvent(a0)

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

class LoadoutCard(QFrame):
    assign_clicked = pyqtSignal(int)
    clear_clicked = pyqtSignal(int)
    execute_clicked = pyqtSignal(int)
    hotkey_changed = pyqtSignal(int, str)

    def __init__(self, index: int, title: str, desc: str, hotkey: str, parent=None):
        super().__init__(parent)
        self.index = index
        self.setObjectName("cardFrame")
        self._build_ui(title, desc, hotkey)

    def _build_ui(self, title: str, desc: str, hotkey: str):
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        header.addWidget(title_label)
        header.addStretch()
        self.hotkey_btn = KeyCaptureButton(hotkey, self)
        self.hotkey_btn.setFixedWidth(110)
        self.hotkey_btn.key_captured.connect(lambda k, idx=self.index: self.hotkey_changed.emit(idx, k))
        header.addWidget(QLabel("槽快捷键"))
        header.addWidget(self.hotkey_btn)
        layout.addLayout(header)

        self.name_label = QLabel("未绑定")
        self.name_label.setStyleSheet("font-size:15px; font-weight:700;")
        self.desc_label = QLabel(desc)
        self.desc_label.setObjectName("cardDesc")
        self.cmd_label = QLabel("指令: -")
        self.cmd_label.setStyleSheet("color:#d6c060; font-family: Consolas;")
        layout.addWidget(self.name_label)
        layout.addWidget(self.cmd_label)
        layout.addWidget(self.desc_label)

        btns = QHBoxLayout()
        assign = QPushButton("设为当前选择")
        assign.clicked.connect(lambda _=False, idx=self.index: self.assign_clicked.emit(idx))
        clear = QPushButton("清除")
        clear.clicked.connect(lambda _=False, idx=self.index: self.clear_clicked.emit(idx))
        exec_btn = QPushButton("▶ 执行")
        exec_btn.clicked.connect(lambda _=False, idx=self.index: self.execute_clicked.emit(idx))
        btns.addWidget(assign)
        btns.addWidget(clear)
        btns.addWidget(exec_btn)
        layout.addLayout(btns)

    def update_content(self, stratagem: dict | None):
        if stratagem is None:
            self.name_label.setText("未绑定")
            self.cmd_label.setText("指令: -")
            self.desc_label.setText("选择战备后点击“设为当前选择”")
            return
        self.name_label.setText(f"{stratagem['name']}  ({stratagem['model']})")
        self.cmd_label.setText(f"指令: {command_to_string(stratagem['command'])}")
        self.desc_label.setText(stratagem.get("description", ""))

    def set_hotkey(self, key: str):
        self.hotkey_btn.set_key(key)

class StratagemApp(QMainWindow):
    _hotkey_triggered = pyqtSignal(dict)
    _slot_triggered = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("绝地潜兵2 自动呼叫战备")
        self.resize(1180, 760)
        self.setMinimumSize(900, 600)

        self.config = load_config()
        self._listening = False
        self._executing = False
        self._capture_mode = False
        self._global_hook = None
        self._hotkey_map: dict[str, dict] = {}
        self._stratagem_hotkeys: dict[tuple, str] = {}
        self.loadout: list[dict | None] = []
        cfg_loadout = (self.config.get("loadout") or [])[:5]
        self.loadout.extend(cfg_loadout)
        while len(self.loadout) < 5:
            self.loadout.append(None)
        self.slot_hotkeys: dict[str, str] = self.config.get("slot_hotkeys", {})
        self.slot_key_map: dict[str, int] = {}

        self._build_hotkey_maps()
        self._build_ui()
        self._hotkey_triggered.connect(self._on_hotkey_triggered)
        self._slot_triggered.connect(self._execute_slot)

        if self.config.get("listening_enabled", True):
            self._start_listening()

    # ------------- 构建热键映射 -------------
    def _build_hotkey_maps(self):
        self._hotkey_map.clear()
        self._stratagem_hotkeys.clear()
        for key_name, info in self.config.get("stratagem_hotkeys", {}).items():
            model, name = info.get("model"), info.get("name")
            if not model or not name:
                continue
            self._stratagem_hotkeys[(model, name)] = key_name
            for s in STRATAGEMS:
                if s["model"] == model and s["name"] == name:
                    self._hotkey_map[key_name] = s
                    break
        self._rebuild_slot_key_map()

    def _rebuild_slot_key_map(self):
        self.slot_key_map.clear()
        for slot_str, key in self.slot_hotkeys.items():
            if key:
                self.slot_key_map[key] = int(slot_str)

    # ------------- UI -------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QHBoxLayout(central)
        main.setContentsMargins(10, 10, 10, 6)
        main.setSpacing(10)

        # 左侧负载
        loadout_panel = QVBoxLayout()
        loadout_panel.setSpacing(8)
        header = QLabel("⚔ 任务负载 / 4 + 常驻任务")
        header.setStyleSheet("font-size:16px; font-weight:700;")
        loadout_panel.addWidget(header)

        self.slot_cards: list[LoadoutCard] = []
        slot_titles = ["槽1", "槽2", "槽3", "槽4", "任务常驻"]
        slot_desc = ["常用战备槽", "常用战备槽", "常用战备槽", "常用战备槽", "用于任务常驻战备"]
        for idx in range(5):
            card = LoadoutCard(idx, slot_titles[idx], slot_desc[idx], self.slot_hotkeys.get(str(idx), ""), self)
            if idx == 4:
                card.setProperty("mission", True)
            card.assign_clicked.connect(self._assign_selected_to_slot)
            card.clear_clicked.connect(self._clear_slot)
            card.execute_clicked.connect(self._execute_slot)
            card.hotkey_changed.connect(self._set_slot_hotkey)
            self.slot_cards.append(card)
            card.update_content(self._find_stratagem_in_loadout(idx))
            loadout_panel.addWidget(card)

        loadout_panel.addStretch()
        main.addLayout(loadout_panel, 4)

        # 右侧列表与操作
        right_col = QVBoxLayout()
        top_bar = QHBoxLayout()
        top_bar.setObjectName("topBar")
        title = QLabel("⚡ 战备浏览")
        title.setStyleSheet("font-size:16px; font-weight:700;")
        top_bar.addWidget(title)
        top_bar.addSpacing(10)
        top_bar.addWidget(QLabel("🔍"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索名称 / 型号 / 描述…")
        self.search_input.setFixedWidth(260)
        self.search_input.textChanged.connect(self._on_search)
        top_bar.addWidget(self.search_input)
        top_bar.addStretch()

        self.execute_btn = QPushButton("▶ 执行选中")
        self.execute_btn.setObjectName("executeBtn")
        self.execute_btn.clicked.connect(self._execute_selected)
        top_bar.addWidget(self.execute_btn)

        self.hotkey_btn = QPushButton("⌨ 战备快捷键")
        self.hotkey_btn.clicked.connect(self._set_hotkey_for_selected)
        top_bar.addWidget(self.hotkey_btn)

        self.listen_btn = QPushButton("🔇 监听关")
        self.listen_btn.setObjectName("listenBtn")
        self.listen_btn.clicked.connect(self._toggle_listening)
        top_bar.addWidget(self.listen_btn)

        settings_btn = QPushButton("⚙ 按键设置")
        settings_btn.clicked.connect(self._open_settings)
        top_bar.addWidget(settings_btn)
        right_col.addLayout(top_bar)

        self.tab_widget = QTabWidget()
        self.category_tables: dict[str, QTableWidget] = {}
        for category in get_categories():
            table = self._create_table()
            self._populate_table(table, get_stratagems_by_category(category))
            self.tab_widget.addTab(table, category)
            self.category_tables[category] = table
        self.search_table = self._create_table()
        self._search_tab_added = False
        right_col.addWidget(self.tab_widget)

        main.addLayout(right_col, 8)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel()
        self.hotkey_count_label = QLabel()
        self.listen_status_label = QLabel()
        self.status_bar.addWidget(self.status_label, 1)
        self.status_bar.addPermanentWidget(self.hotkey_count_label)
        self.status_bar.addPermanentWidget(self.listen_status_label)
        self._update_status("就绪 — 选择战备，双击执行或绑定槽位")

    def _create_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(COLUMN_HEADERS))
        table.setHorizontalHeaderLabels(COLUMN_HEADERS)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        vheader = table.verticalHeader()
        if vheader:
            vheader.setVisible(False)
        table.setShowGrid(False)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        header = table.horizontalHeader()
        if header:
            header.setSectionResizeMode(COL_MODEL, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(COL_NAME, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(COL_COMMAND, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(COL_HOTKEY, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(COL_DESC, QHeaderView.ResizeMode.Stretch)
            header.setMinimumSectionSize(60)

        table.doubleClicked.connect(lambda idx: self._on_double_click(table, idx))
        table.customContextMenuRequested.connect(lambda pos: self._show_context_menu(table, pos))
        return table

    def _populate_table(self, table: QTableWidget, stratagems: list[dict]):
        table.setRowCount(len(stratagems))
        for row, s in enumerate(stratagems):
            model_item = QTableWidgetItem(s["model"])
            name_item = QTableWidgetItem(s["name"])
            cmd_item = QTableWidgetItem(command_to_string(s["command"]))
            cmd_item.setFont(QFont("Consolas", 13))
            hk = self._stratagem_hotkeys.get((s["model"], s["name"]), "")
            hk_item = QTableWidgetItem(format_key_display(hk))
            if hk:
                hk_item.setForeground(QColor("#ffa500"))
            desc_item = QTableWidgetItem(s.get("description", ""))
            for item in (model_item, name_item, cmd_item, hk_item, desc_item):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, COL_MODEL, model_item)
            table.setItem(row, COL_NAME, name_item)
            table.setItem(row, COL_COMMAND, cmd_item)
            table.setItem(row, COL_HOTKEY, hk_item)
            table.setItem(row, COL_DESC, desc_item)

    def _refresh_hotkey_column(self, table: QTableWidget):
        for row in range(table.rowCount()):
            model_item = table.item(row, COL_MODEL)
            name_item = table.item(row, COL_NAME)
            if not model_item or not name_item:
                continue
            key = (model_item.text(), name_item.text())
            hk = self._stratagem_hotkeys.get(key, "")
            hk_item = table.item(row, COL_HOTKEY)
            if hk_item:
                hk_item.setText(format_key_display(hk))
                hk_item.setForeground(QColor("#ffa500") if hk else QColor("#5b4b1b"))

    def _refresh_all_hotkeys(self):
        for t in self.category_tables.values():
            self._refresh_hotkey_column(t)
        self._refresh_hotkey_column(self.search_table)

    def _active_table(self) -> QTableWidget:
        w = self.tab_widget.currentWidget()
        return w if isinstance(w, QTableWidget) else self.search_table

    def _selected_stratagem(self, table: QTableWidget) -> dict | None:
        selection = table.selectionModel()
        if selection is None:
            return None
        rows = selection.selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        model_item = table.item(row, COL_MODEL)
        name_item = table.item(row, COL_NAME)
        if not model_item or not name_item:
            return None
        model = model_item.text()
        name = name_item.text()
        for s in STRATAGEMS:
            if s["model"] == model and s["name"] == name:
                return s
        return None

    # ------------- 搜索 -------------
    def _on_search(self, text: str):
        keyword = text.strip()
        if not keyword:
            if self._search_tab_added:
                idx = self.tab_widget.indexOf(self.search_table)
                if idx >= 0:
                    self.tab_widget.removeTab(idx)
                self._search_tab_added = False
            return
        results = search_stratagems(keyword)
        self._populate_table(self.search_table, results)
        if not self._search_tab_added:
            self.tab_widget.addTab(self.search_table, "🔍 搜索结果")
            self._search_tab_added = True
        self.tab_widget.setCurrentWidget(self.search_table)
        self._update_status(f"搜索 \"{keyword}\" — {len(results)} 条")

    # ------------- 表格交互 -------------
    def _on_double_click(self, table: QTableWidget, index):
        if index.column() == COL_HOTKEY:
            self._set_hotkey_for_selected()
        else:
            s = self._selected_stratagem(table)
            if s:
                self._execute_stratagem(s)

    def _show_context_menu(self, table: QTableWidget, pos):
        s = self._selected_stratagem(table)
        if not s:
            return
        menu = QMenu(self)
        act_exec = menu.addAction("▶ 执行")
        act_set_hk = menu.addAction("⌨ 设置战备快捷键")
        menu.addSeparator()
        sub_slots = menu.addMenu("设为槽位")
        slot_actions = []
        if sub_slots:
            for idx in range(5):
                text = f"槽{idx+1}" if idx < 4 else "任务常驻"
                act = sub_slots.addAction(text)
                slot_actions.append(act)
        viewport = table.viewport()
        mapped_pos = viewport.mapToGlobal(pos) if viewport else QPoint()
        chosen = menu.exec(mapped_pos)
        if chosen == act_exec:
            self._execute_stratagem(s)
        elif chosen == act_set_hk:
            self._set_hotkey_for_stratagem(s)
        elif chosen in slot_actions:
            slot_idx = slot_actions.index(chosen)
            self._assign_to_slot(slot_idx, s)

    # ------------- 执行 -------------
    def _execute_selected(self):
        s = self._selected_stratagem(self._active_table())
        if s:
            self._execute_stratagem(s)

    def _execute_stratagem(self, stratagem: dict):
        if self._executing:
            return
        self._executing = True
        name = stratagem["name"]
        cmd = command_to_string(stratagem["command"])
        self._update_status(f"正在执行: {name} ({cmd}) …")
        thread = threading.Thread(target=self._execute_thread, args=(stratagem,), daemon=True)
        thread.start()

    def _execute_thread(self, stratagem: dict):
        try:
            execute_stratagem(stratagem, self.config)
            QTimer.singleShot(0, lambda: self._update_status(f"✔ 已执行: {stratagem['name']}"))
        except ImportError:
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "缺少依赖", "请安装 keyboard 模块:\npip install keyboard"))
        except Exception as exc:
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "执行错误", str(exc)))
        finally:
            self._executing = False

    # ------------- 槽位管理 -------------
    def _assign_selected_to_slot(self, idx: int):
        s = self._selected_stratagem(self._active_table())
        if s:
            self._assign_to_slot(idx, s)

    def _assign_to_slot(self, idx: int, stratagem: dict):
        self.loadout[idx] = {"model": stratagem["model"], "name": stratagem["name"]}
        self.slot_cards[idx].update_content(stratagem)
        self._persist_loadout()
        self._update_status(f"槽 {idx+1} 已设置为 {stratagem['name']}")

    def _clear_slot(self, idx: int):
        self.loadout[idx] = None
        self.slot_cards[idx].update_content(None)
        self._persist_loadout()
        self._update_status(f"槽 {idx+1} 已清除")

    def _execute_slot(self, idx: int):
        stratagem = self._find_stratagem_in_loadout(idx)
        if stratagem:
            self._execute_stratagem(stratagem)

    def _find_stratagem_in_loadout(self, idx: int) -> dict | None:
        item = self.loadout[idx]
        if not item:
            return None
        for s in STRATAGEMS:
            if s["model"] == item.get("model") and s["name"] == item.get("name"):
                return s
        return None

    def _persist_loadout(self):
        self.config["loadout"] = self.loadout
        save_config(self.config)

    # ------------- 战备快捷键（单个） -------------
    def _set_hotkey_for_selected(self):
        s = self._selected_stratagem(self._active_table())
        if s:
            self._set_hotkey_for_stratagem(s)

    def _set_hotkey_for_stratagem(self, stratagem: dict):
        self._capture_mode = True
        dialog = KeyCaptureDialog(self, f"设置快捷键 — {stratagem['name']}")
        result = dialog.exec()
        self._capture_mode = False
        if result != QDialog.DialogCode.Accepted:
            return
        key = dialog.captured_key
        if key is None:
            return
        key_pair = (stratagem["model"], stratagem["name"])
        if key == "":
            self._clear_hotkey_for_stratagem(stratagem)
            return
        if key in self._hotkey_map:
            old = self._hotkey_map[key]
            self._stratagem_hotkeys.pop((old["model"], old["name"]), None)
        old_key = self._stratagem_hotkeys.get(key_pair)
        if old_key:
            self._hotkey_map.pop(old_key, None)
            self.config["stratagem_hotkeys"].pop(old_key, None)
        self._hotkey_map[key] = stratagem
        self._stratagem_hotkeys[key_pair] = key
        self.config["stratagem_hotkeys"][key] = {"model": stratagem["model"], "name": stratagem["name"]}
        save_config(self.config)
        self._refresh_all_hotkeys()
        self._update_status(f"已绑定: {format_key_display(key)} → {stratagem['name']}")

    def _clear_hotkey_for_stratagem(self, stratagem: dict):
        key_pair = (stratagem["model"], stratagem["name"])
        old_key = self._stratagem_hotkeys.pop(key_pair, None)
        if old_key:
            self._hotkey_map.pop(old_key, None)
            self.config["stratagem_hotkeys"].pop(old_key, None)
            save_config(self.config)
        self._refresh_all_hotkeys()
        self._update_status(f"已清除 {stratagem['name']} 的快捷键")

    # ------------- 槽位快捷键 -------------
    def _set_slot_hotkey(self, idx: int, key: str):
        if key is None:
            return
        if key == "":
            self.slot_hotkeys.pop(str(idx), None)
        else:
            # 去重：同一键只保留最后设定的槽
            for slot_str, k in list(self.slot_hotkeys.items()):
                if k == key:
                    self.slot_hotkeys.pop(slot_str, None)
            self.slot_hotkeys[str(idx)] = key
        self.config["slot_hotkeys"] = self.slot_hotkeys
        save_config(self.config)
        self._rebuild_slot_key_map()
        self._update_status(f"槽 {idx+1} 快捷键已更新为 {format_key_display(key)}" if key else f"槽 {idx+1} 快捷键已清除")

    # ------------- 全局监听 -------------
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
            return
        if key in self._hotkey_map:
            self._hotkey_triggered.emit(self._hotkey_map[key])

    def _on_hotkey_triggered(self, stratagem: dict):
        if not self._executing:
            self._execute_stratagem(stratagem)

    def _update_listen_ui(self):
        if self._listening:
            self.listen_btn.setText("🔊 监听开")
            self.listen_btn.setProperty("active", True)
        else:
            self.listen_btn.setText("🔇 监听关")
            self.listen_btn.setProperty("active", False)
        bound = len(self._stratagem_hotkeys)
        self.hotkey_count_label.setText(f"战备快捷键 {bound}")
        self.listen_status_label.setText("● 监听中" if self._listening else "○ 未监听")
        self.listen_status_label.setStyleSheet("color:#4be85c;" if self._listening else "color:#666;")

    # ------------- 设置对话框 -------------
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

    # ------------- 状态 / 键盘 -------------
    def _update_status(self, text: str = ""):
        self.status_label.setText(text)
        self._update_listen_ui()

    def keyPressEvent(self, a0):
        if a0 is None:
            return
        key = a0.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._execute_selected()
        elif key == Qt.Key.Key_Delete:
            s = self._selected_stratagem(self._active_table())
            if s:
                self._clear_hotkey_for_stratagem(s)
        elif key == Qt.Key.Key_F5:
            self._toggle_listening()
        else:
            super().keyPressEvent(a0)

    # ------------- 关闭清理 -------------
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
