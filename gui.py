import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import time
import main
from rcon_client import send_rcon_command

def save_config(cfg, tree):
    """
    Guarda la configuración del TreeView en config.json
    """
    cfg["commands"] = []
    for item in tree.get_children():
        values = tree.item(item, "values")
        cfg["commands"].append({
            "command": values[0],
            "interval": int(values[1]),
            "unit": values[2],
            "repeat": int(values[3]),
            "status": values[4] if len(values) > 4 else "Listo"
        })
    with open("config.json", "w") as f:
        json.dump(cfg, f, indent=4)
    messagebox.showinfo("Guardado", "Configuración guardada correctamente")

def add_command(tree):
    """
    Agrega una fila nueva al TreeView
    """
    tree.insert("", "end", values=("showMessage ...", 1, "minutes", 1, "Listo"))

def start_gui(cfg):
    root = tk.Tk()
    root.title("Valheim RCON MultiCommand Tool")
    root.geometry("1000x650")

    # Permitir expansión dinámica
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew")

    # Configurar estructura grid
    main_frame.rowconfigure(1, weight=1)
    main_frame.columnconfigure(0, weight=1)

    # -------------------------------
    # TreeView principal
    # -------------------------------
    columns = ("Comando", "Intervalo", "Unidad", "Repeticiones", "Estado")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.grid(row=1, column=0, sticky="nsew")

    # Scrollbars
    y_scroll = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    y_scroll.grid(row=1, column=1, sticky="ns")
    tree.configure(yscroll=y_scroll.set)

    # Cargar datos desde config.json
    for cmd in cfg["commands"]:
        tree.insert(
            "",
            "end",
            values=(
                cmd["command"],
                cmd["interval"],
                cmd["unit"],
                cmd["repeat"],
                cmd.get("status", "Listo")
            )
        )

    # -------------------------------
    # Marco de progreso
    # -------------------------------
    progress_frame = ttk.Frame(main_frame)
    progress_frame.grid(row=2, column=0, sticky="ew", pady=10)
    progress_frame.columnconfigure(0, weight=1)

    progress_bars = {}

    # -------------------------------
    # Estado general
    # -------------------------------
    status_label = ttk.Label(main_frame, text="Estado: Detenido", foreground="red")
    status_label.grid(row=3, column=0, pady=5)

    # -------------------------------
    # Función con progreso
    # -------------------------------
    def execute_with_progress(cmd, idx, item_id):
        interval = cmd["interval"]
        if cmd["unit"] == "minutes":
            interval *= 60
        elif cmd["unit"] == "hours":
            interval *= 3600

        repeat = cmd["repeat"]
        bar, label = progress_bars[idx]
        bar["maximum"] = interval

        for n in range(repeat):
            if not main.running:
                break

            elapsed = 0
            tree.set(item_id, "Estado", f"Esperando ({n+1}/{repeat})")

            while elapsed < interval and main.running:
                time.sleep(1)
                elapsed += 1
                bar["value"] = elapsed
                remaining = interval - elapsed
                label.config(text=f"{cmd['command']} - Faltan {remaining}s")
                root.update_idletasks()

            if not main.running:
                tree.set(item_id, "Estado", "⛔ Detenido")
                label.config(text=f"⛔ Detenido: {cmd['command']}")
                return

            success = send_rcon_command(cfg["rcon_host"], cfg["rcon_port"], cfg["rcon_pass"], cmd["command"])
            if success:
                label.config(text=f"✅ Enviado: {cmd['command']}")
                tree.set(item_id, "Estado", "✅ Enviado")
            else:
                label.config(text=f"❌ Error al enviar: {cmd['command']}")
                tree.set(item_id, "Estado", "❌ Error")

            bar["value"] = 0
            root.update_idletasks()

        if main.running:
            tree.set(item_id, "Estado", "✔ Finalizado")
            label.config(text=f"✔ Finalizado: {cmd['command']}")

    # -------------------------------
    # Botones
    # -------------------------------
    btn_frame = ttk.Frame(main_frame)
    btn_frame.grid(row=4, column=0, pady=10, sticky="ew")
    btn_frame.columnconfigure((0, 1, 2, 3), weight=1)

    ttk.Button(btn_frame, text="Agregar comando", command=lambda: add_command(tree)).grid(row=0, column=0, padx=5, sticky="ew")
    ttk.Button(btn_frame, text="Guardar configuración", command=lambda: save_config(cfg, tree)).grid(row=0, column=1, padx=5, sticky="ew")

    # -------------------------------
    # Iniciar ejecución
    # -------------------------------
    def start_send():
        save_config(cfg, tree)
        status_label.config(text="Estado: Ejecutando...", foreground="green")

        # Limpiar el área de progreso
        for widget in progress_frame.winfo_children():
            widget.destroy()

        progress_bars.clear()

        # Crear barras por comando
        for idx, item_id in enumerate(tree.get_children()):
            values = tree.item(item_id, "values")
            cmd = {
                "command": values[0],
                "interval": int(values[1]),
                "unit": values[2],
                "repeat": int(values[3])
            }

            frame = ttk.Frame(progress_frame)
            frame.pack(fill="x", pady=2)
            bar = ttk.Progressbar(frame, length=800)
            bar.pack(fill="x", padx=10)
            label = ttk.Label(frame, text=f"Listo: {cmd['command']}")
            label.pack(anchor="w", padx=10)
            progress_bars[idx] = (bar, label)

            tree.set(item_id, "Estado", "⏳ En ejecución")

            threading.Thread(target=execute_with_progress, args=(cmd, idx, item_id), daemon=True).start()

    # -------------------------------
    # Detener ejecución
    # -------------------------------
    def stop_send():
        main.stop_execution()
        status_label.config(text="Estado: Detenido", foreground="red")
        for _, (bar, label) in progress_bars.items():
            bar["value"] = 0
            label.config(text="⛔ Ejecución detenida")
        for item_id in tree.get_children():
            tree.set(item_id, "Estado", "⛔ Detenido")
        messagebox.showinfo("Detenido", "Ejecución detenida.")

    ttk.Button(btn_frame, text="Iniciar ejecución 🟢", command=start_send).grid(row=0, column=2, padx=5, sticky="ew")
    ttk.Button(btn_frame, text="Detener ejecución 🔴", command=stop_send).grid(row=0, column=3, padx=5, sticky="ew")

    # -------------------------------
    # Hacer todo adaptable al resize
    # -------------------------------
    for i in range(5):
        main_frame.rowconfigure(i, weight=1)
    main_frame.columnconfigure(0, weight=1)

    root.mainloop()
