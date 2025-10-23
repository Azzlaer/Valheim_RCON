# ⚔️ Valheim RCON Tool  
![Preview](https://github.com/Azzlaer/Valheim_RCON/blob/main/foto1.png)

### Herramienta de administración RCON para servidores de **Valheim**  
Desarrollada por **ChatGPT (OpenAI)** en conjunto con **Azzlaer** para la comunidad de **[LatinBattle.com](https://latinbattle.com)** ❤️

---

## 🧩 Descripción general

**Valheim RCON Tool** es una aplicación en **Python** con interfaz gráfica (**Tkinter**) que permite enviar comandos **RCON** a un servidor de Valheim de manera sencilla, programada y completamente configurable.

Está pensada para administradores de servidores que desean automatizar mensajes o tareas, como avisos de reinicio, mensajes de bienvenida, o recordatorios a los jugadores.

---

## 🚀 Características principales

✅ **Multi-Comando:** Permite definir múltiples comandos con tiempos y repeticiones independientes.  
✅ **Configurable:** Todos los datos del servidor y comandos se guardan en `config.json`.  
✅ **Modo GUI o Consola:** Puedes usarlo desde interfaz gráfica o solo consola.  
✅ **ProgressBar visual:** Cada comando muestra una barra de progreso con cuenta regresiva.  
✅ **Botones de control:** Iniciar / Detener ejecución en cualquier momento.  
✅ **Logs automáticos:** Cada evento se guarda en `rcon_log.txt`.  
✅ **Diseño adaptable:** La interfaz se ajusta automáticamente al maximizar la ventana.  

---

## 🧱 Estructura del proyecto

```
Valheim_RCON/
│
├── main.py            # Núcleo del programa (modo GUI o consola)
├── gui.py             # Interfaz gráfica con Tkinter
├── rcon_client.py     # Módulo de conexión RCON
├── config.json        # Configuración del servidor y comandos
├── rcon_log.txt       # Log automático de eventos
└── README.md          # Este archivo :)
```

---

## ⚙️ Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/Azzlaer/Valheim_RCON.git
   cd Valheim_RCON
   ```

2. **Instala las dependencias:**
   ```bash
   pip install mcrcon
   ```

3. **Configura tu conexión RCON** en `config.json`:
   ```json
   {
       "rcon_host": "127.0.0.1",
       "rcon_port": 2974,
       "rcon_pass": "35027595",
       "mode": "gui",
       "commands": [
           {
               "command": "showMessage Server restart in 5 minutes!",
               "interval": 5,
               "unit": "minutes",
               "repeat": 1
           },
           {
               "command": "showMessage Server restarting now!",
               "interval": 5,
               "unit": "minutes",
               "repeat": 1
           }
       ]
   }
   ```

---

## 🪟 Modo gráfico (GUI)

Ejecuta:
```bash
python main.py
```

Verás una interfaz amigable con:

- Lista editable de comandos (TreeView).  
- Botones para **Agregar**, **Guardar**, **Iniciar**, y **Detener**.  
- Barras de progreso con cuenta regresiva para cada comando.  
- Estado visual actualizado en tiempo real.  

La interfaz se ajusta automáticamente al maximizar la ventana, manteniendo el diseño centrado y ordenado.

---

## 🧠 Modo consola (opcional)

Puedes ejecutar todo sin GUI cambiando en `config.json`:
```json
"mode": "console"
```

---

## 🧾 Logs

Cada evento se registra automáticamente en `rcon_log.txt`, incluyendo:
- Fecha y hora
- Comando enviado
- Resultado de conexión

---

## 💡 Ejemplo de uso

Perfecto para automatizar:
- Mensajes de mantenimiento o reinicio.
- Anuncios automáticos para los jugadores.
- Recordatorios o alertas periódicas en el servidor.

---

## 🧑‍💻 Créditos

Proyecto desarrollado por:  
**🧠 ChatGPT (OpenAI)** en colaboración con **Azzlaer**  
para **[LatinBattle.com](https://latinbattle.com)** ⚔️

---

## 🪙 Licencia

Este proyecto es de código abierto bajo la licencia **MIT**.  
Puedes usarlo, modificarlo y distribuirlo libremente, mencionando los créditos correspondientes.

---

## ⭐ ¡Apoya el proyecto!

Si te gusta esta herramienta, deja una ⭐ en [el repositorio oficial](https://github.com/Azzlaer/Valheim_RCON)  
y ayuda a mejorar las herramientas de administración para la comunidad de Valheim.

---
