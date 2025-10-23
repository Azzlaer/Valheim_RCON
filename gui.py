import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import time
import main
from rcon_client import send_rcon_command

# -------------------------------
# Función para guardar la config
# -------------------------------
def save_config(cfg, tree):
    cfg["commands"] = []
    for item in tree.get_children():
        values = tree.item(item, "values")
        cfg["commands"].append({
            "command": values[0],
            "interval": int(values[1]),
            "unit": values[2],
            "repeat": int(values[3])
        })
    with open("config.json", "w") as f:
        json.dump(cfg, f, indent=4)
    messagebox.showinfo("Guardado", "Configuración guardada correctamente")

# -------------------------------
# Agregar nueva fila
# -------------------------------
def add_command(tree):
    tree.insert("", "end", values=("showMessage ...", 1, "minutes", 1))

# -------------------------------
# Función principal del GUI
# -------------------------------
def start_gui(cfg):
    root = tk.Tk()
    root.title("Valheim RCON MultiCommand Tool")
    root.geometry("950x550")

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    columns = ("Comando", "Intervalo", "Unidad", "Repeticiones")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=200)
    tree.pack(fill="both", expand=True)

    for cmd in cfg["commands"]:
        tree.insert("", "end", values=(cmd["command"], cmd["interval"], cmd["unit"], cmd["repeat"]))

    # -------------------------------
    # Área para mostrar progreso
    # -------------------------------
    progress_frame = ttk.Frame(root)
    progress_frame.pack(fill="both", expand=True, pady=10)

    progress_bars = {}

    status_label = ttk.Label(root, text="Estado: Detenido", foreground="red")
    status_label.pack(pady=5)

    # -------------------------------
    # Función de ejecución visual
    # -------------------------------
    def execute_with_progress(cmd, idx):
        interval = cmd["interval"]
        if cmd["unit"] == "minutes":
            interval *= 60
        elif cmd["unit"] == "hours":
            interval *= 3600

        repeat = cmd["repeat"]
        bar, label = progress_bars[idx]
        bar["maximum"] = interval
        for n in range(repeat):
            elapsed = 0
            while elapsed < interval and main.running:
                time.sleep(1)
                elapsed += 1
                bar["value"] = elapsed
                remaining = interval - elapsed
                label.config(text=f"Esperando {remaining} s - {cmd['command']}")
                root.update_idletasks()

            if not main.running:
                label.config(text=f"⛔ Detenido: {cmd['command']}")
                return

            # Enviar comando
            success = send_rcon_command(cfg["rcon_host"], cfg["rcon_port"], cfg["rcon_pass"], cmd["command"])
            if success:
                label.config(text=f"✅ Comando enviado: {cmd['command']}")
            else:
                label.config(text=f"❌ Error al enviar: {cmd['command']}")

            bar["value"] = 0  # Reiniciar barra para siguiente repetición
            root.update_idletasks()

    # -------------------------------
    # Botones inferiores
    # -------------------------------
    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Agregar comando", command=lambda: add_command(tree)).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Guardar configuración", command=lambda: save_config(cfg, tree)).grid(row=0, column=1, padx=5)

    # -------------------------------
    # Función de inicio
    # -------------------------------
    def start_send():
        save_config(cfg, tree)
        status_label.config(text="Estado: Ejecutando...", foreground="green")

        # Crear barras de progreso para cada comando
        for widget in progress_frame.winfo_children():
            widget.destroy()

        progress_bars.clear()

        for idx, cmd in enumerate(cfg["commands"]):
            bar = ttk.Progressbar(progress_frame, length=600)
            bar.pack(pady=4)
            label = ttk.Label(progress_frame, text=f"Listo: {cmd['command']}")
            label.pack()
            progress_bars[idx] = (bar, label)

            threading.Thread(target=execute_with_progress, args=(cmd, idx), daemon=True).start()

    # -------------------------------
    # Función de detener
    # -------------------------------
    def stop_send():
        main.stop_execution()
        status_label.config(text="Estado: Detenido", foreground="red")
        for _, (bar, label) in progress_bars.items():
            bar["value"] = 0
            label.config(text="⛔ Ejecución detenida")
        messagebox.showinfo("Detenido", "Ejecución detenida.")

    ttk.Button(btn_frame, text="Iniciar ejecución 🟢", command=start_send).grid(row=0, column=2, padx=5)
    ttk.Button(btn_frame, text="Detener ejecución 🔴", command=stop_send).grid(row=0, column=3, padx=5)

    root.mainloop()
