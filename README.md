# CheckParkingBot 🚗📸

Bot de Telegram que captura fotos bajo demanda usando un ESP32-CAM, orquestado desde una Raspberry Pi Zero W.

## Hardware necesario

- ESP32-CAM AI Thinker con placa MB (puerto USB-C integrado)
- Raspberry Pi Zero W
- Tarjeta microSD (mínimo 8GB) para la RPi
- Fuente de alimentación 5V para cada dispositivo

---

## Parte 1 — Configurar el ESP32-CAM

### 1.1 Instalar Arduino IDE y soporte ESP32

1. Descarga Arduino IDE desde https://www.arduino.cc/en/software
2. Abre **Archivo → Preferencias** y añade esta URL en "URLs adicionales de gestor de placas":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Ve a **Herramientas → Placa → Gestor de placas**, busca `esp32` e instala el paquete de **Espressif Systems**.

### 1.2 Configurar la placa en Arduino IDE

En **Herramientas** selecciona:

| Parámetro | Valor |
|---|---|
| Board | AI Thinker ESP32-CAM |
| Port | /dev/ttyUSB0 (Linux) |
| Upload Speed | 115200 |
| Flash Frequency | 80MHz |
| Flash Mode | QIO |

### 1.3 Permisos del puerto serie en Linux

```bash
sudo usermod -a -G dialout $USER
```

Cierra sesión y vuelve a entrar para que surta efecto. Verifica con:

```bash
groups | grep dialout
```

> **Nota Fedora:** si `brltty` interfiere con el puerto, desactívalo:
> ```bash
> sudo systemctl stop brltty && sudo systemctl disable brltty
> ```

### 1.4 Flashear el sketch CameraWebServer

1. Abre **Archivo → Ejemplos → ESP32 → Camera → CameraWebServer**
2. Edita el archivo `board_config.h` y asegúrate de que **solo** está descomentada esta línea:
   ```cpp
   #define CAMERA_MODEL_AI_THINKER // Has PSRAM
   ```
3. En el archivo principal `CameraWebServer.ino` introduce tus credenciales WiFi:
   ```cpp
   const char *ssid = "TU_WIFI";
   const char *password = "TU_PASSWORD";
   ```
   > ⚠️ El ESP32 solo soporta redes **2.4GHz**.
4. Sube el sketch con el botón **→** de Arduino IDE.
5. Abre el **Monitor Serie** a **115200 baudios** y espera a ver la IP asignada:
   ```
   Camera Ready! Use 'http://192.168.x.x' to connect
   ```

### 1.5 Verificar que la cámara funciona

Abre la IP en el navegador. Deberías ver la interfaz web de la cámara con stream en directo.

### 1.6 Fijar la IP del ESP32-CAM en el router

Para que la RPi siempre sepa dónde encontrar el ESP32, asigna una IP estática por MAC en tu router (sección DHCP reservation o similar).

La MAC del dispositivo aparece en el monitor serie al arrancar:
```
MAC: 1c:c3:ab:fa:e7:30
```

---

## Parte 2 — Configurar la Raspberry Pi Zero W

### 2.1 Instalar Raspberry Pi OS

1. Descarga e instala **Raspberry Pi Imager** desde https://www.raspberrypi.com/software/
   - En Fedora: `sudo dnf install rpi-imager`
2. Selecciona:
   - **Device:** Raspberry Pi Zero W
   - **OS:** Raspberry Pi OS Lite (32-bit)
   - **Storage:** tu tarjeta microSD
3. Antes de grabar, abre la configuración avanzada (⚙️) y configura:
   - Hostname, usuario y contraseña
   - WiFi SSID y password (red 2.4GHz)
   - País WiFi: ES
   - Habilitar SSH ✅
4. Graba la tarjeta, insértala en la RPi y conecta la alimentación.
5. Espera 3-5 minutos al primer arranque.

### 2.2 Conectarse por SSH

```bash
ssh TUUSUARIO@IP_DE_LA_RPI
```

Puedes ver la IP en el panel de administración de tu router. Verifica que el puerto SSH está disponible con:

```bash
nc -zv IP_DE_LA_RPI 22
```

### 2.3 Actualizar el sistema e instalar dependencias

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip -y
pip3 install python-telegram-bot python-dotenv --break-system-packages
```

---

## Parte 3 — Crear el bot de Telegram

### 3.1 Crear el bot con BotFather

1. Busca **@BotFather** en Telegram y escribe `/newbot`
2. Sigue los pasos para elegir nombre y username (debe acabar en `bot`)
3. Guarda el **token** que te proporciona

### 3.2 Obtener tu chat_id

Busca **@userinfobot** en Telegram, escríbele cualquier mensaje y apunta tu `Id`.

### 3.3 Configurar las variables de entorno

Crea el archivo `.env` en la RPi (fuera del repositorio):

```bash
nano ~/.env
```

```env
TELEGRAM_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
ESP32_IP=192.168.1.xxx
```

### Configuración de persistencia con Systmctl
Creación del servicio para que se inicie de manera automática al encender la Raspberry.
```bash
sudo nano /etc/systemd/system/parkingbot.service
```
```ìni
[Unit]
Description=CheckParkingBot Telegram Bot
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/CheckParkingBot
ExecStart=/usr/bin/python3 /home/pi/CheckParkingBot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activa e inicia el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable parkingbot
sudo systemctl start parkingbot
```
Verifica que está corriendo
```bash
sudo systemctl status parkingbot
```
Para ver los logs en tiempo real
```bash
journalctl -u parkingbot -f
```
### 3.4 Estructura del repositorio

```
CheckParkingBot/
├── bot.py
├── .gitignore
├── .env.example
└── README.md
```

El `.gitignore` debe incluir:
```
.env
```

Y `.env.example` sirve como plantilla:
```env
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
ESP32_IP=
```

---

## Uso

### Arrancar el bot manualmente

```bash
python3 ~/CheckParkingBot/bot.py
```

### Comandos disponibles

| Comando | Acción |
|---|---|
| `/start` | Muestra el teclado con el botón |
| `/foto` | Captura y envía una foto desde el ESP32-CAM |
| 🚗 Comprobar parking | Botón equivalente a `/foto` |

> El bot solo responde al `chat_id` configurado en `.env`. Cualquier otro usuario recibirá "No autorizado."

---
