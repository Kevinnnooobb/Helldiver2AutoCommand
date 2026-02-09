"""
绝地潜兵2 自动呼叫战备 - 可视化界面
Helldivers 2 Auto Stratagem Caller - Visual GUI

Features:
- Category-tabbed stratagem browser
- Search/filter stratagems
- Custom key binding configuration
- One-click stratagem execution
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from stratagems import (
    STRATAGEMS,
    get_categories,
    get_stratagems_by_category,
    search_stratagems,
    command_to_string,
)
from config import load_config, save_config, DEFAULT_KEY_BINDINGS
from executor import execute_stratagem


class StratagemApp:
    """Main application window for Helldivers 2 Auto Stratagem Caller."""

    def __init__(self, root):
        self.root = root
        self.root.title("绝地潜兵2 自动呼叫战备")
        self.root.geometry("900x620")
        self.root.minsize(800, 500)

        self.config = load_config()

        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        """Construct the full UI layout."""
        # Top bar: search + settings
        top_frame = ttk.Frame(self.root, padding=5)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Button(top_frame, text="⚙ 按键设置", command=self._open_settings).pack(
            side=tk.RIGHT
        )

        # Notebook for category tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.category_trees = {}
        for category in get_categories():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=category)

            tree = self._create_tree(frame)
            self.category_trees[category] = tree
            self._populate_tree(tree, get_stratagems_by_category(category))

        # Search results tab (hidden by default, shown during search)
        self.search_frame = ttk.Frame(self.notebook)
        self.search_tree = self._create_tree(self.search_frame)
        self.search_tab_added = False

        # Bottom status bar
        status_frame = ttk.Frame(self.root, padding=5)
        status_frame.pack(fill=tk.X)
        self.status_var = tk.StringVar(value="就绪 - 选择一个战备并双击执行")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        ttk.Label(
            status_frame,
            text=f"共 {len(STRATAGEMS)} 个战备",
        ).pack(side=tk.RIGHT)

    def _create_tree(self, parent):
        """Create a Treeview widget for displaying stratagems."""
        columns = ("model", "name", "command", "description")
        tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        tree.heading("model", text="型号")
        tree.heading("name", text="名称")
        tree.heading("command", text="指令码")
        tree.heading("description", text="描述")

        tree.column("model", width=110, minwidth=80)
        tree.column("name", width=180, minwidth=120)
        tree.column("command", width=140, minwidth=100)
        tree.column("description", width=400, minwidth=200)

        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Double-click to execute
        tree.bind("<Double-1>", lambda e: self._on_execute(tree))

        return tree

    def _populate_tree(self, tree, stratagems):
        """Fill a Treeview with stratagem data."""
        for item in tree.get_children():
            tree.delete(item)
        for s in stratagems:
            tree.insert(
                "",
                tk.END,
                values=(
                    s["model"],
                    s["name"],
                    command_to_string(s["command"]),
                    s["description"],
                ),
            )

    # -------------------------------------------------------------- Search
    def _on_search(self, *_args):
        """Handle search input changes."""
        keyword = self.search_var.get().strip()
        if not keyword:
            # Remove search tab if it exists
            if self.search_tab_added:
                self.notebook.forget(self.search_frame)
                self.search_tab_added = False
            return

        results = search_stratagems(keyword)
        self._populate_tree(self.search_tree, results)

        if not self.search_tab_added:
            self.notebook.add(self.search_frame, text="🔍 搜索结果")
            self.search_tab_added = True

        # Switch to search results tab
        self.notebook.select(self.search_frame)
        self.status_var.set(f"搜索 \"{keyword}\" - 找到 {len(results)} 个结果")

    # ------------------------------------------------------------ Execute
    def _on_execute(self, tree):
        """Execute the selected stratagem."""
        selection = tree.selection()
        if not selection:
            return

        item = tree.item(selection[0])
        values = item["values"]
        # Find the matching stratagem by model + name
        name = values[1]
        model = values[0]

        stratagem = None
        for s in STRATAGEMS:
            if s["name"] == name and s["model"] == model:
                stratagem = s
                break

        if stratagem is None:
            messagebox.showerror("错误", f"找不到战备: {name}")
            return

        self.status_var.set(f"正在执行: {stratagem['name']} ({command_to_string(stratagem['command'])})")
        self.root.update_idletasks()

        # Run in a separate thread so the UI doesn't freeze
        thread = threading.Thread(
            target=self._execute_in_thread, args=(stratagem,), daemon=True
        )
        thread.start()

    def _execute_in_thread(self, stratagem):
        """Execute stratagem in a background thread."""
        try:
            execute_stratagem(stratagem, self.config)
            self.root.after(0, self._set_status, f"已执行: {stratagem['name']}")
        except ImportError:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "缺少依赖",
                    "请安装 keyboard 模块:\npip install keyboard",
                ),
            )
        except Exception as exc:
            self.root.after(
                0,
                lambda: messagebox.showerror("执行错误", str(exc)),
            )

    def _set_status(self, text):
        self.status_var.set(text)

    # ----------------------------------------------------------- Settings
    def _open_settings(self):
        """Open the key binding settings dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("按键设置")
        dialog.geometry("400x320")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="方向键绑定", font=("", 12, "bold")).pack(pady=(10, 5))

        bindings_frame = ttk.Frame(dialog, padding=10)
        bindings_frame.pack(fill=tk.X)

        entries = {}
        directions = [("↑ (上)", "↑"), ("↓ (下)", "↓"), ("← (左)", "←"), ("→ (右)", "→")]

        for i, (label_text, direction) in enumerate(directions):
            ttk.Label(bindings_frame, text=label_text).grid(
                row=i, column=0, sticky=tk.W, pady=3
            )
            var = tk.StringVar(value=self.config["key_bindings"].get(direction, DEFAULT_KEY_BINDINGS[direction]))
            entry = ttk.Entry(bindings_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, padx=(10, 0), pady=3)
            entries[direction] = var

        ttk.Separator(dialog, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        misc_frame = ttk.Frame(dialog, padding=10)
        misc_frame.pack(fill=tk.X)

        ttk.Label(misc_frame, text="战备激活键:").grid(row=0, column=0, sticky=tk.W, pady=3)
        strat_var = tk.StringVar(value=self.config["stratagem_key"])
        ttk.Entry(misc_frame, textvariable=strat_var, width=15).grid(
            row=0, column=1, padx=(10, 0), pady=3
        )

        ttk.Label(misc_frame, text="按键延迟(秒):").grid(row=1, column=0, sticky=tk.W, pady=3)
        delay_var = tk.StringVar(value=str(self.config["key_delay"]))
        ttk.Entry(misc_frame, textvariable=delay_var, width=15).grid(
            row=1, column=1, padx=(10, 0), pady=3
        )

        def save():
            for direction, var in entries.items():
                self.config["key_bindings"][direction] = var.get().strip()
            self.config["stratagem_key"] = strat_var.get().strip()
            try:
                self.config["key_delay"] = float(delay_var.get().strip())
            except ValueError:
                messagebox.showerror("错误", "按键延迟必须为数字")
                return
            save_config(self.config)
            self.status_var.set("按键设置已保存")
            dialog.destroy()

        def reset():
            for direction, var in entries.items():
                var.set(DEFAULT_KEY_BINDINGS[direction])
            strat_var.set("ctrl")
            delay_var.set("0.05")

        btn_frame = ttk.Frame(dialog, padding=10)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="恢复默认", command=reset).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="保存", command=save).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(
            side=tk.RIGHT, padx=(0, 5)
        )


def main():
    """Entry point for the application."""
    root = tk.Tk()
    StratagemApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
