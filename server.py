from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Speicher für die empfangenen Sensordaten
received_data = []

@app.route('/')
def home():
    return "Arduino Webserver is running!"

@app.route('/send-data', methods=['POST'])
def receive_data():
    global received_data
    try:
        data = request.json
        received_data.append(data)

        # Sende die Daten über Websocket an verbundene Clients
        socketio.emit('new_data', data)

        print(f"Received data: {data}")
        return {"status": "success", "message": "Data received"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

@app.route('/visualize')
def visualize():
    return render_template('visualization_websocket.html')  # Neue HTML-Datei für Websocket-Visualisierung

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
