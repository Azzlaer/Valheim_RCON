import json
import time
import logging
import threading
from rcon_client import send_rcon_command

# Configuración del log
logging.basicConfig(filename="rcon_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# Bandera global para controlar ejecución
running = True

def stop_execution():
    """
    Detiene todos los hilos de ejecución.
    """
    global running
    running = False
    print("🛑 Ejecución detenida por el usuario.")

def countdown(seconds, text=""):
    """
    Cuenta regresiva visual antes de enviar un comando.
    """
    global running
    for i in range(seconds, 0, -1):
        if not running:
            return
        print(f"\r⏳ [{text}] Enviando en {i} segundos...", end="")
        time.sleep(1)
    print("\n")

def execute_command(cfg, cmd):
    """
    Ejecuta un comando con su propio temporizador y repeticiones.
    """
    global running
    interval = cmd["interval"]
    if cmd["unit"] == "minutes":
        interval *= 60
    elif cmd["unit"] == "hours":
        interval *= 3600

    for i in range(cmd["repeat"]):
        if not running:
            break
        countdown(interval, cmd["command"])
        if not running:
            break
        success = send_rcon_command(cfg["rcon_host"], cfg["rcon_port"], cfg["rcon_pass"], cmd["command"])
        msg = f"Comando enviado ({i+1}/{cmd['repeat']}): {cmd['command']}"
        if success:
            logging.info(msg)
            print(f"✅ {msg}")
        else:
            logging.error("❌ Error al enviar el comando.")
            print("❌ Error al enviar el comando.")

def run_console(cfg):
    """
    Ejecuta todos los comandos definidos en config.json en hilos separados.
    """
    global running
    running = True
    threads = []
    for cmd in cfg["commands"]:
        t = threading.Thread(target=execute_command, args=(cfg, cmd))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    with open("config.json") as f:
        cfg = json.load(f)

    if cfg["mode"] == "console":
        run_console(cfg)
    else:
        import gui
        gui.start_gui(cfg)
