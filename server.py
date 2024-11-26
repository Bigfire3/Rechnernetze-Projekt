from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Arduino Webserver is running!"

@app.route('/send-data', methods=['POST'])
def receive_data():
    try:
        data = request.json  # Daten vom Arduino (als JSON-Format)
        print(f"Received data: {data}")
        return {"status": "success", "message": "Data received"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

@app.route('/get-data', methods=['GET'])
def send_data():
    # Beispiel-Daten, die an den Arduino gesendet werden
    response_data = {"message": "Hello Arduino!", "status": "active"}
    return response_data

if __name__ == '__main__':
    # Setze den Host auf '0.0.0.0', um externe Verbindungen zuzulassen
    app.run(host='0.0.0.0', port=5000)  # Server läuft auf Port 5000
