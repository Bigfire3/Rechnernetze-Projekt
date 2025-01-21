from flask import Flask, render_template, request
from flask_socketio import SocketIO
import socket
import threading
import json

app = Flask(__name__)  # Flask-Anwendung initialisieren
socketio = SocketIO(app)  # WebSocket-Unterstützung hinzufügen

# Speicher für die empfangenen Sensordaten
received_data = []  # Liste zur Speicherung von Sensordaten

# TCP-Server-Details
TCP_HOST = "0.0.0.0"  # Lauscht auf allen verfügbaren Schnittstellen
TCP_PORT = 5001  # Port für TCP-Kommunikation

# TCP-Daten empfangen
def start_tcp_server():
    print(f"Starting TCP server on port {TCP_PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((TCP_HOST, TCP_PORT))  # Server an Host und Port binden
        server_socket.listen(5)  # Warteschlangenlimit setzen
        print(f"TCP server listening on {TCP_HOST}:{TCP_PORT}")
        
        while True:
            conn, addr = server_socket.accept()  # Verbindung akzeptieren
            print(f"Connected by {addr}")
            threading.Thread(target=handle_tcp_client, args=(conn,)).start()  # Thread für Client starten

def handle_tcp_client(conn):
    global received_data
    with conn:
        while True:
            try:
                # Daten vom Client empfangen
                data = conn.recv(1024)  # Bis zu 1024 Bytes empfangen
                if not data:
                    break
                
                # Dekodieren der JSON-Daten
                message = data.decode('utf-8').strip()  # Daten als String dekodieren
                try:
                    json_data = json.loads(message)  # JSON-Daten parsen
                    received_data.append(json_data)  # Daten speichern
                    
                    # Daten an WebSocket-Clients senden
                    socketio.emit('new_data', json_data)
                    print(f"Received TCP data: {json_data}")
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {message}")
            except Exception as e:
                print(f"Error handling TCP client: {e}")
                break
        print("Client disconnected.")

# Flask-Routen
@app.route('/')
def home():
    return "Arduino Webserver with TCP is running!"  # Startseite der Anwendung

@app.route('/send-data', methods=['POST'])
def receive_data():
    global received_data
    try:
        data = request.json  # JSON-Daten aus der Anfrage
        received_data.append(data)

        # Sende die Daten über WebSocket an verbundene Clients
        socketio.emit('new_data', data)

        print(f"Received HTTP data: {data}")
        return {"status": "success", "message": "Data received"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

@app.route('/visualize')
def visualize():
    return render_template('visualization_websocket.html')  # Visualisierungsseite laden

if __name__ == '__main__':
    # Starte den TCP-Server in einem separaten Thread
    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()

    # Starte den Flask-Webserver
    print("Starting Flask server...")
    socketio.run(app, host='0.0.0.0', port=5002)
