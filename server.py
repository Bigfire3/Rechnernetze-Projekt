from flask import Flask, render_template, request
from flask_socketio import SocketIO
import socket
import threading
import json

app = Flask(__name__)
socketio = SocketIO(app)

# Speicher für die empfangenen Sensordaten
received_data = []

# TCP-Server-Details
TCP_HOST = "0.0.0.0"  # Lauscht auf allen Schnittstellen
TCP_PORT = 5001       # Port für TCP-Server (verschieden von Flask)

# TCP-Daten empfangen
def start_tcp_server():
    print(f"Starting TCP server on port {TCP_PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((TCP_HOST, TCP_PORT))
        server_socket.listen(5)
        print(f"TCP server listening on {TCP_HOST}:{TCP_PORT}")
        
        while True:
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")
            threading.Thread(target=handle_tcp_client, args=(conn,)).start()

def handle_tcp_client(conn):
    global received_data
    with conn:
        while True:
            try:
                # Daten vom Client empfangen
                data = conn.recv(1024)
                if not data:
                    break
                
                # Dekodieren der JSON-Daten
                message = data.decode('utf-8').strip()
                try:
                    json_data = json.loads(message)
                    received_data.append(json_data)
                    
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
    return "Arduino Webserver with TCP is running!"

@app.route('/send-data', methods=['POST'])
def receive_data():
    global received_data
    try:
        data = request.json
        received_data.append(data)

        # Sende die Daten über Websocket an verbundene Clients
        socketio.emit('new_data', data)

        print(f"Received HTTP data: {data}")
        return {"status": "success", "message": "Data received"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

@app.route('/visualize')
def visualize():
    return render_template('visualization_websocket.html')

if __name__ == '__main__':
    # Starte den TCP-Server in einem separaten Thread auf Port 5001
    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()

    # Starte den Flask-Webserver auf Port 5000
    print("Starting Flask server...")
    socketio.run(app, host='0.0.0.0', port=5002)
