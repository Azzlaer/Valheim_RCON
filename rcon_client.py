# rcon_client.py
import logging
import time

logger = logging.getLogger(__name__)

# Intentamos usar mcrcon (más fiable para servidores basados en Valve-like)
try:
    from mcrcon import MCRcon
    MCRCON_AVAILABLE = True
except Exception:
    MCRCON_AVAILABLE = False

def send_rcon_command(host, port, password, command, retries=2, retry_delay=3):
    """
    Envía comando RCON. Devuelve (True, response) o (False, error_str)
    Intenta usar mcrcon si está disponible, si no, hace un intento simple por socket (no garantizado para todos los servidores).
    """
    for attempt in range(1, retries + 2):
        try:
            if MCRCON_AVAILABLE:
                with MCRcon(host, password, port=port) as mcr:
                    resp = mcr.command(command)
                    logger.info(f"RCON success: {command} -> {resp}")
                    return True, str(resp)
            else:
                # Fallback muy simple: solo intenta una conexión TCP y mandar texto (no siempre funciona según implementación RCON)
                import socket
                with socket.create_connection((host, port), timeout=5) as s:
                    # Nota: esto NO implementa el protocolo RCON formal — usar MCRcon recomendado
                    payload = (command + "\n").encode("utf-8")
                    s.sendall(payload)
                    try:
                        data = s.recv(4096)
                        resp = data.decode("utf-8", errors="ignore")
                    except Exception:
                        resp = ""
                    logger.info(f"RCON fallback sent: {command}")
                    return True, resp
        except Exception as e:
            logger.warning(f"Intento {attempt} fallido para comando '{command}': {e}")
            if attempt <= retries:
                time.sleep(retry_delay)
            else:
                logger.error(f"Error definitivo enviando RCON: {e}")
                return False, str(e)
