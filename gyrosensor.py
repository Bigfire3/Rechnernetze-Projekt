import network
import time
import ujson
from lsm6dsox import LSM6DSOX
from machine import Pin, I2C
import websocket  # WebSocket-Bibliothek für MicroPython

# WLAN-Details
SSID = "NoahSteiner"
PASSWORD = "18122000"

# Server-Details
SERVER_IP = "192.168.45.31"  # IP-Adresse deines Flask-WebSocket-Servers
SERVER_PORT = 5000
WEB_SOCKET_URL = f"ws://{SERVER_IP}:{SERVER_PORT}/socket.io/?EIO=4&transport=websocket"

# WLAN-Initialisierung
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Verbindung herstellen
print("Connecting to WiFi...")
wlan.connect(SSID, PASSWORD)

# Warten, bis die Verbindung hergestellt ist
while not wlan.isconnected():
    print(".", end="")
    time.sleep(1)

print("\nWiFi connected!")
print("IP address:", wlan.ifconfig()[0])

# Gyrosensor initialisieren
lsm = LSM6DSOX(I2C(0, scl=Pin(13), sda=Pin(12)))

# WebSocket-Verbindung herstellen
try:
    print("Connecting to WebSocket server...")
    ws = websocket.websocket()
    ws.connect(WEB_SOCKET_URL)
    print("WebSocket connected!")
except Exception as e:
    print(f"Failed to connect to WebSocket server: {e}")
    raise SystemExit

# Sensordaten kontinuierlich senden
try:
    while True:
        accel_data = lsm.accel()
        gyro_data = lsm.gyro()

        # Sensordaten als JSON vorbereiten
        sensor_data = {
            "accelerometer": {"x": accel_data[0], "y": accel_data[1], "z": accel_data[2]},
            "gyroscope": {"x": gyro_data[0], "y": gyro_data[1], "z": gyro_data[2]},
            "timestamp": time.time(),
        }

        # Daten an den Server senden
        try:
            json_data = ujson.dumps(sensor_data)  # Daten in JSON umwandeln
            ws.send(json_data)
            print(f"Sent: {json_data}")
        except Exception as e:
            print(f"Error sending data: {e}")
            ws.close()
            raise SystemExit

        time.sleep(0.1)  # Daten alle 0.1 Sekunden senden

except KeyboardInterrupt:
    print("Stopping WebSocket communication.")
    ws.close()
