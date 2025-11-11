# gui.py - Versión mejorada con emojis y diseño moderno

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import logging
from rcon_client import send_rcon_command

LOG = logging.getLogger(__name__)
CONFIG_FILE = "config.json"

# ---------------------------
# Guardar Configuración
# ---------------------------
def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
    LOG.info("Configuración guardada correctamente")


# ---------------------------
# GUI principal
# ---------------------------
def start_gui(cfg):
    root = tk.Tk()
    root.title("🛠️ LatinBattle RCON Tool v2")
    root.geometry("1000x680")
    root.configure(bg="#1e1e1e")  # Fondo oscuro elegante

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#252526", fieldbackground="#252526", foreground="#ffffff")
    style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10, "bold"))
    style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#00c8ff")
    style.configure("Status.TLabel", font=("Segoe UI", 10, "bold"))
    style.configure("TEntry", fieldbackground="#2d2d30", foreground="white")

    # Marco superior
    header = ttk.Label(root, text="⚙️  Administrador de Comandos RCON", style="Header.TLabel")
    header.pack(pady=10)

    # Frame principal
    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    # Botones superiores
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x", pady=5)
    ttk.Button(btn_frame, text="➕ Agregar", command=lambda: add_command(cfg, tree, root)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="✏️ Editar", command=lambda: edit_command(cfg, tree, root)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="🗑️ Eliminar", command=lambda: delete_command(cfg, tree)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="💾 Guardar", command=lambda: save_config(cfg)).pack(side="right", padx=5)

    # Tabla de comandos
    columns = ("command", "interval", "unit", "repeat", "status")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, anchor="center")
    tree.pack(fill="both", expand=True, pady=10)

    # Estado inferior
    status_var = tk.StringVar(value="🔴 Estado: Detenido")
    status_lbl = ttk.Label(root, textvariable=status_var, style="Status.TLabel", foreground="#ff5c5c")
    status_lbl.pack(pady=5)

    # Botones de control
    control_frame = ttk.Frame(root)
    control_frame.pack(pady=10)
    ttk.Button(control_frame, text="▶ Iniciar", command=lambda: start_commands(cfg, tree, status_var, root)).pack(side="left", padx=5)
    ttk.Button(control_frame, text="⏹ Detener", command=lambda: stop_commands(status_var)).pack(side="left", padx=5)

    # Cargar datos
    refresh_table(cfg, tree)

    root.mainloop()


# ---------------------------
# Tabla de comandos
# ---------------------------
def refresh_table(cfg, tree):
    for item in tree.get_children():
        tree.delete(item)
    for idx, cmd in enumerate(cfg.get("commands", [])):
        tree.insert("", "end", iid=str(idx), values=(cmd["command"], cmd["interval"], cmd["unit"], cmd["repeat"], "🟢 Listo"))


# ---------------------------
# Formularios
# ---------------------------
def add_command(cfg, tree, root):
    dlg = CommandDialog(root, title="➕ Nuevo Comando")
    root.wait_window(dlg.top)
    if dlg.result:
        cfg.setdefault("commands", []).append(dlg.result)
        save_config(cfg)
        refresh_table(cfg, tree)


def edit_command(cfg, tree, root):
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("Atención", "Selecciona un comando para editar.")
        return
    idx = int(selected[0])
    dlg = CommandDialog(root, title="✏️ Editar Comando", initial=cfg["commands"][idx])
    root.wait_window(dlg.top)
    if dlg.result:
        cfg["commands"][idx] = dlg.result
        save_config(cfg)
        refresh_table(cfg, tree)


def delete_command(cfg, tree):
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("Atención", "Selecciona un comando para eliminar.")
        return
    idx = int(selected[0])
    confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el comando '{cfg['commands'][idx]['command']}'?")
    if confirm:
        cfg["commands"].pop(idx)
        save_config(cfg)
        refresh_table(cfg, tree)


# ---------------------------
# Ejecución de comandos
# ---------------------------
running_threads = []
stop_flag = False

def stop_commands(status_var):
    global stop_flag
    stop_flag = True
    status_var.set("🔴 Estado: Detenido")


def start_commands(cfg, tree, status_var, root):
    global stop_flag
    stop_flag = False
    status_var.set("🟢 Ejecutando comandos...")
    threads = []
    for idx, cmd in enumerate(cfg["commands"]):
        t = threading.Thread(target=execute_command, args=(cfg, cmd, tree, idx, root))
        t.daemon = True
        t.start()
        threads.append(t)
    running_threads.extend(threads)


def execute_command(cfg, cmd, tree, idx, root):
    interval = cmd["interval"]
    if cmd["unit"] == "minutes":
        interval *= 60
    elif cmd["unit"] == "hours":
        interval *= 3600

    repeat = cmd["repeat"]

    for i in range(repeat):
        if stop_flag:
            update_status(tree, idx, "⏹ Detenido", root)
            return
        update_status(tree, idx, f"⏳ Esperando {interval}s", root)
        for j in range(interval):
            if stop_flag:
                update_status(tree, idx, "⏹ Detenido", root)
                return
            time.sleep(1)
        ok, resp = send_rcon_command(cfg["rcon_host"], cfg["rcon_port"], cfg["rcon_pass"], cmd["command"])
        if ok:
            update_status(tree, idx, f"✅ Enviado ({i+1}/{repeat})", root)
        else:
            update_status(tree, idx, f"❌ Error ({i+1}/{repeat})", root)
        time.sleep(1)

    update_status(tree, idx, "🏁 Completado", root)


def update_status(tree, idx, text, root):
    root.after(0, lambda: tree.set(str(idx), "status", text))


# ---------------------------
# Diálogo elegante para crear/editar
# ---------------------------
class CommandDialog:
    def __init__(self, parent, title="Comando", initial=None):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x300")
        self.top.configure(bg="#2d2d30")
        self.result = None

        ttk.Label(self.top, text="💬 Comando:", style="TLabel").pack(anchor="w", padx=8, pady=(8, 0))
        self.e_cmd = ttk.Entry(self.top, width=60)
        self.e_cmd.pack(padx=8, pady=4)

        ttk.Label(self.top, text="⏱️ Intervalo:", style="TLabel").pack(anchor="w", padx=8, pady=(8, 0))
        self.e_interval = ttk.Entry(self.top, width=20)
        self.e_interval.pack(padx=8, pady=4)

        ttk.Label(self.top, text="🧭 Unidad:", style="TLabel").pack(anchor="w", padx=8, pady=(8, 0))
        self.c_unit = ttk.Combobox(self.top, values=["seconds", "minutes", "hours"], state="readonly", width=18)
        self.c_unit.set("seconds")
        self.c_unit.pack(padx=8, pady=4)

        ttk.Label(self.top, text="🔁 Repeticiones:", style="TLabel").pack(anchor="w", padx=8, pady=(8, 0))
        self.e_repeat = ttk.Entry(self.top, width=20)
        self.e_repeat.pack(padx=8, pady=4)

        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="💾 Guardar", command=self.save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Cancelar", command=self.top.destroy).pack(side="left", padx=5)

        if initial:
            self.e_cmd.insert(0, initial["command"])
            self.e_interval.insert(0, str(initial["interval"]))
            self.c_unit.set(initial["unit"])
            self.e_repeat.insert(0, str(initial["repeat"]))

    def save(self):
        cmd = self.e_cmd.get().strip()
        interval = self.e_interval.get().strip()
        unit = self.c_unit.get()
        repeat = self.e_repeat.get().strip()

        if not cmd or not interval.isdigit() or not repeat.isdigit():
            messagebox.showerror("Error", "Por favor, completa todos los campos correctamente.")
            return

        self.result = {
            "command": cmd,
            "interval": int(interval),
            "unit": unit,
            "repeat": int(repeat)
        }
        self.top.destroy()
