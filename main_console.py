import time
import logging
import threading
from rcon_client import send_rcon_command

logging.basicConfig(filename="rcon_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

def run_console(cfg):
    print("🖥️ Modo consola iniciado...\n")
    threads = []

    def execute(cmd):
        interval = cmd["interval"]
        if cmd["unit"] == "minutes":
            interval *= 60
        elif cmd["unit"] == "hours":
            interval *= 3600

        for i in range(cmd["repeat"]):
            print(f"⏳ Ejecutando '{cmd['command']}' en {interval}s...")
            time.sleep(interval)
            send_rcon_command(cfg["rcon_host"], cfg["rcon_port"], cfg["rcon_pass"], cmd["command"])
            print(f"✅ Comando enviado: {cmd['command']}")

    for cmd in cfg["commands"]:
        t = threading.Thread(target=execute, args=(cmd,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
