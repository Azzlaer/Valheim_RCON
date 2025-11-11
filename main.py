# main.py
import json
import logging
import sys
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

LOG_FILE = "rcon_log.txt"
CONFIG_FILE = "config.json"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_config():
    cfg_path = Path(CONFIG_FILE)
    if not cfg_path.exists():
        raise FileNotFoundError(f"No se encontró {CONFIG_FILE} en {cfg_path.resolve()}")
    with cfg_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def show_startup_error(msg):
    # intenta mostrar un messagebox si la GUI puede mostrarse
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error al iniciar", msg)
        root.destroy()
    except Exception:
        # fallback: print y log
        print(msg)
    logging.error(msg)

def main():
    try:
        cfg = load_config()
    except Exception as e:
        tb = traceback.format_exc()
        logging.error("Error cargando config.json:\n" + tb)
        show_startup_error(f"Error cargando {CONFIG_FILE}:\n{e}\nRevisa rcon_log.txt")
        sys.exit(1)

    mode = cfg.get("mode", "gui").lower()
    try:
        if mode == "console":
            # import tardío para evitar problemas si GUI falta
            from gui import run_console_mode
            run_console_mode(cfg)
        else:
            # GUI mode (por defecto)
            from gui import start_gui
            start_gui(cfg)
    except Exception as e:
        tb = traceback.format_exc()
        logging.error("Error iniciando la aplicación:\n" + tb)
        show_startup_error(f"Error iniciando la aplicación:\n{e}\nRevisa rcon_log.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
