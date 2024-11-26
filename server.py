from flask import Flask, request, jsonify

app = Flask(__name__)

# Globale Variable zur Speicherung empfangener Daten
received_data = []

@app.route('/')
def home():
    return "Arduino Webserver is running!"

@app.route('/send-data', methods=['POST'])
def receive_data():
    try:
        data = request.json  # JSON-Daten vom Arduino empfangen
        received_data.append(data)  # Speichere die Daten zur späteren Auswertung
        print(f"Received data: {data}")
        return {"status": "success", "message": "Data received"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

@app.route('/get-data', methods=['GET'])
def send_data():
    return jsonify(received_data)  # Gibt alle gespeicherten Daten zurück

if __name__ == '__main__':
    # Server auf allen Netzwerkschnittstellen starten
    app.run(host='0.0.0.0', port=5000)
