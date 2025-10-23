from mcrcon import MCRcon

def send_rcon_command(host, port, password, command):
    """
    Envía un comando al servidor RCON.
    Retorna True si fue exitoso, False si hubo error.
    """
    try:
        with MCRcon(host, password, port=port) as mcr:
            response = mcr.command(command)
            print(f"📡 Respuesta del servidor: {response}")
            return True
    except Exception as e:
        print(f"⚠️ Error RCON: {e}")
        return False
