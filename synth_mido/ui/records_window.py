"""Felvételek ablak: lista, lejátszás, törlés."""

import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from synth_mido.core import recorder
from synth_mido.core.i18n import t
from synth_mido.ui.common import (
    format_seconds,
    pretty_instrument,
)


class RecordsWindowMixin:

    def open_records(self):
        if self.records_win is not None and self.records_win.winfo_exists():
            self.records_win.deiconify()
            self.records_win.lift()
            self.refresh_records()
            return
        win = tk.Toplevel(self.root)
        self.records_win = win
        self.bind_text(win, lambda: t("records.title"), option="title")
        win.geometry("720x380")
        win.minsize(520, 260)
        win.configure(bg=self.palette["bg"])

        body = ttk.Frame(win, padding=10)
        body.pack(fill="both", expand=True)

        columns = ("name", "created", "duration", "notes", "instrument")
        widths = (200, 140, 60, 60, 180)
        tree = ttk.Treeview(body, columns=columns, show="headings", selectmode="extended")
        for col, width in zip(columns, widths):
            self.bind_text(tree, lambda c=col: t(f"records.col.{c}"), option=("heading", col))
            tree.column(col, width=width, anchor="e" if col in ("duration", "notes") else "w")
        tree.tag_configure("error", foreground=self.palette["muted"])
        self.records_tree = tree
        scroll = ttk.Scrollbar(body, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        btns = ttk.Frame(body)
        btns.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        tr = self.tr
        tr(ttk.Button(btns, command=self.play_selected_record, style="Accent.TButton"), "btn.play").pack(
            side="left", padx=(0, 3)
        )
        tr(ttk.Button(btns, command=self.select_all_records), "btn.select_all").pack(side="left", padx=3)
        tr(ttk.Button(btns, command=self.delete_selected_records), "btn.delete").pack(side="left", padx=3)
        tr(ttk.Button(btns, command=self.refresh_records), "btn.refresh").pack(side="left", padx=3)
        tr(ttk.Button(btns, command=self.open_records_folder), "btn.open_folder").pack(side="left", padx=3)
        tr(ttk.Button(btns, command=win.destroy), "btn.close").pack(side="right")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        tree.bind("<Double-1>", lambda e: self.play_selected_record() if tree.identify_row(e.y) else None)
        tree.bind("<Return>", lambda _e: self.play_selected_record())
        tree.bind("<Delete>", lambda _e: self.delete_selected_records())
        tree.bind("<Control-a>", lambda _e: self.select_all_records())
        win.bind("<Escape>", lambda _e: win.destroy())
        win.bind("<Destroy>", self._on_records_destroy)
        self.refresh_records()
        tree.focus_set()


    def _on_records_destroy(self, event):
        if event.widget is self.records_win:
            self.records_win = None
            self.records_tree = None


    def refresh_records(self):
        tree = self.records_tree
        if tree is None:
            return
        tree.delete(*tree.get_children())
        for info in recorder.list_records():
            if info.error:
                values = (info.name, "—", "—", "—", t("records.broken", error=info.error))
                tree.insert("", "end", iid=str(info.path), values=values, tags=("error",))
            else:
                values = (
                    info.name,
                    info.created.replace("T", " "),
                    format_seconds(info.duration),
                    info.note_count,
                    ", ".join(pretty_instrument(i) for i in info.instruments),
                )
                tree.insert("", "end", iid=str(info.path), values=values)


    def play_selected_record(self):
        tree = self.records_tree
        if tree is None:
            return
        selected = tree.selection()
        if len(selected) != 1:
            messagebox.showinfo(t("msg.pick_one.title"), t("msg.pick_one"), parent=self.records_win)
            return
        self.play_record_file(selected[0], parent=self.records_win)


    def select_all_records(self):
        if self.records_tree is not None:
            self.records_tree.selection_set(self.records_tree.get_children())
        return "break"


    def delete_selected_records(self):
        tree = self.records_tree
        if tree is None:
            return
        selected = tree.selection()
        if not selected:
            messagebox.showinfo(t("msg.no_selection.title"), t("msg.no_selection"), parent=self.records_win)
            return
        if len(selected) == 1:
            question = t("msg.delete_one", name=tree.set(selected[0], "name"))
        else:
            question = t("msg.delete_many", count=len(selected))
        if not messagebox.askyesno(t("msg.delete.title"), question, parent=self.records_win):
            return
        try:
            count = recorder.delete_records(selected)
        except (ValueError, OSError) as e:
            messagebox.showerror(t("msg.delete_error.title"), str(e), parent=self.records_win)
            count = 0
        self.log_line(t("log.deleted", count=count))
        self.refresh_records()


    def open_records_folder(self):
        folder = recorder.RECORDS_DIR
        try:
            folder.mkdir(parents=True, exist_ok=True)
            if sys.platform.startswith("win"):
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
        except OSError as e:
            messagebox.showerror(t("msg.error"), t("msg.folder_error", error=e), parent=self.records_win)
