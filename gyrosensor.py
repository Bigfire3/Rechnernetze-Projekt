import network
import time
import ujson
from lsm6dsox import LSM6DSOX
from machine import Pin, I2C
import socket  # Für die TCP-Kommunikation

# WLAN-Details
SSID = "NoahSteiner"
PASSWORD = "18122000"

# Server-Details
SERVER_IP = "192.168.182.46"  # IP-Adresse des TCP-Servers
SERVER_PORT = 5001            # Port des TCP-Servers

# WLAN-Initialisierung
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

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

# TCP-Verbindung herstellen
try:
    print("Connecting to TCP server...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP-Socket erstellen
    s.connect((SERVER_IP, SERVER_PORT))  # Verbindung zum Server herstellen
    print("TCP connected!")

    # Sensordaten kontinuierlich senden
    while True:
        try:
            # Sensordaten auslesen
            accel_data = lsm.accel()
            gyro_data = lsm.gyro()

            # Sensordaten als JSON vorbereiten
            sensor_data = {
                "accelerometer": {"x": accel_data[0], "y": accel_data[1], "z": accel_data[2]},
                "gyroscope": {"x": gyro_data[0], "y": gyro_data[1], "z": gyro_data[2]},
                "timestamp": time.time(),
            }

            # JSON-Daten in einen String umwandeln
            json_data = ujson.dumps(sensor_data)

            # Daten an den Server senden
            s.sendall(json_data.encode('utf-8') + b'\n')  # Sende JSON-Daten mit Zeilenumbruch
            print(f"Sent: {json_data}")

            time.sleep(0.05)  # 20 Hz Sendeintervall

        except Exception as e:
            print(f"Error while sending data: {e}")
            break

except Exception as e:
    print(f"Failed to connect to TCP server: {e}")

finally:
    # Verbindung schließen
    s.close()
    print("TCP connection closed.")
