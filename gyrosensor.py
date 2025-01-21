import network
import time
import ujson
from lsm6dsox import LSM6DSOX
from machine import Pin, I2C
import socket  # Für die TCP-Kommunikation

# WLAN-Details
SSID = "NoahSteiner"  # Name des WLANs
PASSWORD = "18122000"  # Passwort des WLANs

# Server-Details
SERVER_IP = "192.168.182.46"  # IP-Adresse des TCP-Servers
SERVER_PORT = 5001  # Port des TCP-Servers

# WLAN-Initialisierung
wlan = network.WLAN(network.STA_IF)  # WLAN-Schnittstelle im Station-Modus
wlan.active(True)  # WLAN aktivieren

print("Connecting to WiFi...")
wlan.connect(SSID, PASSWORD)  # Verbindung zum WLAN herstellen

# Warten, bis die Verbindung hergestellt ist
while not wlan.isconnected():
    print(".", end="")  # Fortschritt anzeigen
    time.sleep(1)  # 1 Sekunde warten

print("\nWiFi connected!")
print("IP address:", wlan.ifconfig()[0])  # IP-Adresse anzeigen

# Gyrosensor initialisieren
lsm = LSM6DSOX(I2C(0, scl=Pin(13), sda=Pin(12)))  # Sensor mit I2C verbinden

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
            accel_data = lsm.accel()  # Beschleunigungsdaten
            gyro_data = lsm.gyro()  # Gyroskopdaten

            # Sensordaten als JSON vorbereiten
            sensor_data = {
                "accelerometer": {"x": accel_data[0], "y": accel_data[1], "z": accel_data[2]},
                "gyroscope": {"x": gyro_data[0], "y": gyro_data[1], "z": gyro_data[2]},
                "timestamp": time.time(),  # Aktueller Zeitstempel
            }

            # JSON-Daten in einen String umwandeln
            json_data = ujson.dumps(sensor_data)

            # Daten an den Server senden
            s.sendall(json_data.encode('utf-8') + b'\n')  # Senden der Daten mit Zeilenumbruch
            print(f"Sent: {json_data}")

            time.sleep(0.05)  # 20 Hz Sendeintervall

        except Exception as e:
            print(f"Error while sending data: {e}")
            break  # Schleife beenden bei Fehler

except Exception as e:
    print(f"Failed to connect to TCP server: {e}")

finally:
    # Verbindung schließen
    s.close()
    print("TCP connection closed.")  # Ressourcen freigeben
