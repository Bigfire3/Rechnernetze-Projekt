import network
import time
import urequests
from lsm6dsox import LSM6DSOX
from machine import Pin, I2C

# WLAN-Details
SSID = "S23 von Fabian"
PASSWORD = "12345678"

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

SERVER_URL = "http://192.168.113.31:5000/send-data"

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
        response = urequests.post(SERVER_URL, json=sensor_data)
        print(f"Server response: {response.content}")
    except Exception as e:
        print(f"Error sending data: {e}")

    time.sleep(0.001)
