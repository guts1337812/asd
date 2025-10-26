#!/usr/bin/env python3
# oblivion_core_gui.py
"""
Oblivion Core — Telegram Neutralizer (GUI demo)
------------------------------------------------
ВНИМАНИЕ: это демонстрационная программа — НИЧЕГО не делает с реальными аккаунтами.
Выполняет только локальные визуальные эффекты и сохраняет JSON-отчёт.
(Уведомление видно в "About".)
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import random
import json
import logging
from datetime import datetime
from typing import List, Dict

APP_NAME = "Oblivion Core — Telegram Neutralizer"
VERSION = "v2.0-demo"

# Logging to file
LOG_FILE = "oblivion_core.log"
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("oblivion_core")

POMP_LINES = [
    "Инициирую финализацию — держите крепче.",
    "Криптопульс стабилен. Подключение по протоколу ε.",
    "Контуры блокчейна чисты. Пересылка завершается.",
    "TARGET NEUTRALIZED (display-only).",
    "Операция успешно подтверждена. Подробности в логе."
]

# ---- Helpers ----
def parse_targets(raw: str) -> List[Dict]:
    tokens = [tok.strip() for tok in raw.replace(",", " ").split() if tok.strip()]
    return [{"target": t, "type": "id" if t.isdigit() else "username"} for t in tokens]

def fake_status_counts():
    # стационарные пафосные числа — можно менять или генерировать рандомно
    return {
        "active_sessions": random.randint(3000, 7000),  # например 4213
        "linked_emails": random.randint(800, 1500),     # например 1076
        "open_connections": random.randint(12, 120)     # ещё пара цифр
    }

def fake_api_response(account_id: str) -> Dict:
    statuses = ["200 OK", "202 ACCEPTED", "403 FORBIDDEN", "404 NOT FOUND"]
    return {
        "id": account_id,
        "status": random.choice(statuses),
        "note": "Display-only simulated response (no external calls)."
    }

# ---- GUI ----
class OblivionCoreGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} — {VERSION}")
        self.geometry("920x620")
        self.minsize(900, 600)

        # state
        self.sim_thread = None
        self.stop_event = threading.Event()
        self.results = []

        # layout
        self._create_menu()
        self._create_header()
        self._create_controls()
        self._create_center()
        self._create_footer()

    def _create_menu(self):
        menubar = tk.Menu(self)
        appmenu = tk.Menu(menubar, tearoff=0)
        appmenu.add_command(label="About", command=self._show_about)
        appmenu.add_separator()
        appmenu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="Oblivion", menu=appmenu)
        self.config(menu=menubar)

    def _show_about(self):
        # Здесь видна заметная, но ненавязчивая пометка: demo / safe
        msg = (f"{APP_NAME} {VERSION}\n\n"
               "DEMO MODE — This application performs NO real external operations.\n"
               "It is a visual simulator for presentation only.\n\n"
               f"Logs: {LOG_FILE}")
        messagebox.showinfo("About", msg)

    def _create_header(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=12, pady=(10,6))
        title = ttk.Label(header, text=APP_NAME, font=("Segoe UI", 18, "bold"))
        title.pack(side="left")
        ver = ttk.Label(header, text=VERSION, foreground="#777")
        ver.pack(side="left", padx=(8,0))

        # status counts on the right (paфосные цифры)
        counts = fake_status_counts()
        self.lbl_counts = ttk.Label(header,
            text=f"Активны: {counts['active_sessions']} сессий  •  {counts['linked_emails']} почт  •  {counts['open_connections']} связей",
            font=("Segoe UI", 10, "normal"), foreground="#bb2c2c")
        self.lbl_counts.pack(side="right")

    def _create_controls(self):
        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=12)

        lbl = ttk.Label(frm, text="Targets (ID or username, separated by space or comma):")
        lbl.grid(row=0, column=0, sticky="w")

        self.entry_targets = ttk.Entry(frm)
        self.entry_targets.grid(row=1, column=0, columnspan=4, sticky="we", pady=4)
        frm.columnconfigure(0, weight=1)

        # mode toggles
        self.var_stealth = tk.BooleanVar(value=True)  # looks realistic
        self.var_fancy = tk.BooleanVar(value=True)
        self.var_report = tk.BooleanVar(value=True)

        chk1 = ttk.Checkbutton(frm, text="Stealth UI (realistic layout)", variable=self.var_stealth)
        chk2 = ttk.Checkbutton(frm, text="Fancy effects (animations)", variable=self.var_fancy)
        chk3 = ttk.Checkbutton(frm, text="Auto-save report (JSON)", variable=self.var_report)

        chk1.grid(row=2, column=0, sticky="w", padx=(0,8))
        chk2.grid(row=2, column=1, sticky="w", padx=(0,8))
        chk3.grid(row=2, column=2, sticky="w", padx=(0,8))

        # small hint (non-descriptive)
        hint = ttk.Label(frm, text="Interface mimics a real neutralizer. Operations are display-only.", foreground="#555")
        hint.grid(row=3, column=0, columnspan=4, sticky="w", pady=(6,0))

    def _create_center(self):
        center = ttk.Frame(self)
        center.pack(fill="both", expand=True, padx=12, pady=8)

        # left: console-like log pane
        left = ttk.Frame(center)
        left.pack(side="left", fill="both", expand=True)

        lbl = ttk.Label(left, text="Command Console")
        lbl.pack(anchor="w")
        # using Text widget with monospace font to look real
        self.text_console = tk.Text(left, height=22, bg="#0b0b0b", fg="#e6e6e6", insertbackground="#e6e6e6",
                                    font=("Consolas", 10), wrap="none")
        self.text_console.pack(fill="both", expand=True, padx=(0,6))
        self.text_console.configure(state="disabled")

        # right: control/status panel
        right = ttk.Frame(center, width=320)
        right.pack(side="right", fill="y")

        # variables for display
        self.var_progress = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(right, orient="horizontal", length=280, mode="determinate", variable=self.var_progress)
        self.progress_bar.pack(pady=(8,4))

        self.lbl_progress = ttk.Label(right, text="0 / 0")
        self.lbl_progress.pack()

        separator = ttk.Separator(right, orient="horizontal")
        separator.pack(fill="x", pady=8)

        # large status badges
        self.lbl_status_big = ttk.Label(right, text="STANDBY", font=("Segoe UI", 14, "bold"))
        self.lbl_status_big.pack(pady=(6,10))

        # big "system" info
        self.sysinfo = tk.Text(right, height=10, width=36, bg="#101010", fg="#cfcfcf", font=("Consolas", 10), wrap="word")
        self.sysinfo.pack(pady=(6,4))
        self.sysinfo.configure(state="disabled")
        self._append_sysinfo_initial()

    def _append_sysinfo_initial(self):
        info = [
            f"System: OblivionCore v{VERSION}",
            f"Mode: STEALTH (UI emulation)",
            f"Last sync: {datetime.utcnow().isoformat()}",
            f"Connections: {random.randint(10,120)} active",
            "Auth: token mask = ************",
        ]
        self.sysinfo.configure(state="normal")
        self.sysinfo.delete("1.0", "end")
        self.sysinfo.insert("end", "\n".join(info))
        self.sysinfo.configure(state="disabled")

    def _create_footer(self):
        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=12, pady=(6,12))

        self.btn_start = ttk.Button(frm, text="Execute Neutralization", command=self._on_start)
        self.btn_start.pack(side="left")

        btn_stop = ttk.Button(frm, text="Abort", command=self._on_stop)
        btn_save = ttk.Button(frm, text="Save Console", command=self._save_console)
        btn_clear = ttk.Button(frm, text="Clear Console", command=self._clear_console)

        btn_stop.pack(side="left", padx=8)
        btn_clear.pack(side="left", padx=8)
        btn_save.pack(side="right")

    # ---- console helpers ----
    def console_write(self, text: str, newline: bool = True, tag: str = ""):
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{ts}] "
        line = prefix + text + ("\n" if newline else "")
        # log to file
        logger.info(text)
        # append to text widget in main thread
        def _append():
            self.text_console.configure(state="normal")
            self.text_console.insert("end", line)
            self.text_console.see("end")
            self.text_console.configure(state="disabled")
        self.after(0, _append)

    def _clear_console(self):
        self.text_console.configure(state="normal")
        self.text_console.delete("1.0", "end")
        self.text_console.configure(state="disabled")
        self.console_write("Console cleared by user.", newline=True)

    def _save_console(self):
        txt = self.text_console.get("1.0", "end").strip()
        if not txt:
            messagebox.showinfo("Save Console", "Console is empty.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".log", filetypes=[("Log files","*.log"),("All files","*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            messagebox.showinfo("Saved", f"Console saved to {path}")

    # ---- simulation control ----
    def _on_start(self):
        if self.sim_thread and self.sim_thread.is_alive():
            messagebox.showwarning("Running", "Operation already in progress.")
            return
        raw = self.entry_targets.get().strip()
        if not raw:
            messagebox.showinfo("No targets", "Please enter at least one target.")
            return
        targets = parse_targets(raw)
        if not targets:
            messagebox.showinfo("No targets", "Please enter at least one valid target.")
            return
        self.results = []
        self.stop_event.clear()
        self.var_progress.set(0)
        self.progress_bar['maximum'] = len(targets)
        self.lbl_progress.config(text=f"0 / {len(targets)}")
        self.console_write(f"Starting operation: targets={len(targets)}  stealth={self.var_stealth.get()} fancy={self.var_fancy.get()}")
        # start worker thread
        self.sim_thread = threading.Thread(target=self._worker, args=(targets,), daemon=True)
        self.sim_thread.start()

    def _on_stop(self):
        if self.sim_thread and self.sim_thread.is_alive():
            self.stop_event.set()
            self.console_write("Abort requested by user. Attempting graceful stop...", True)
        else:
            self.console_write("No running operation to abort.", True)

    def _worker(self, targets: List[Dict]):
        total = len(targets)
        for i, t in enumerate(targets, start=1):
            if self.stop_event.is_set():
                self.console_write("Operation aborted.", True)
                break
            self._process_one(t, i, total)
            # update progress
            self.after(0, lambda c=i: self._update_progress(c, total))
        else:
            self.console_write("Operation completed.", True)
            # auto-save report if enabled
            if self.var_report.get():
                self.after(0, self._auto_save_report)

    def _process_one(self, target: Dict, index: int, total: int):
        tgt = target["target"]
        typ = target["type"]
        # very realistic-looking staged output (all local)
        steps = [
            f"[core] resolving {tgt} ...",
            f"[network] establishing secure channel ...",
            f"[auth] validating tokens ...",
            f"[ops] executing neutralization routines ...",
            f"[finalize] committing changes ..."
        ]
        for s in steps:
            if self.stop_event.is_set():
                break
            # write to console with slight random delays
            self.console_write(s)
            # accent big status text
            self._set_big_status(s)
            time.sleep(0.45 + random.random() * 0.5)

        # final fake response
        resp = fake_api_response(tgt)
        ok = resp["status"].startswith("2")
        msg = random.choice(POMP_LINES)
        result_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "target": tgt,
            "type": typ,
            "result": resp,
            "message": msg,
            "display_only": True
        }
        self.results.append(result_entry)

        # console final line for this target
        outcome = "SUCCESS" if ok else "WARNING"
        self.console_write(f"[{outcome}] {tgt} -> {resp['status']}  // {msg}")
        # small pause
        time.sleep(0.25 + random.random() * 0.3)

    def _set_big_status(self, txt: str):
        # show short status in the right panel
        self.lbl_status_big.config(text=txt[:28])

    def _update_progress(self, current: int, total: int):
        self.var_progress.set(current)
        self.lbl_progress.config(text=f"{current} / {total}")

    def _auto_save_report(self):
        # save to file with default name
        name = f"oblivion_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        path = filedialog.asksaveasfilename(defaultextension=".json", initialfile=name,
                                            filetypes=[("JSON files","*.json"),("All files","*.*")])
        if not path:
            self.console_write("Report save cancelled by user.", True)
            return
        data = {
            "app": APP_NAME,
            "version": VERSION,
            "generated_at": datetime.utcnow().isoformat(),
            "results": self.results,
            "note": "DISPLAY-ONLY REPORT. No external ops performed."
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.console_write(f"Report saved: {path}", True)

    # ---- close handler ----
    def _on_close(self):
        if self.sim_thread and self.sim_thread.is_alive():
            if not messagebox.askyesno("Exit", "An operation is running. Exit anyway?"):
                return
            self.stop_event.set()
            time.sleep(0.2)
        self.destroy()

def main():
    app = OblivionCoreGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
