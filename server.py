from flask import Flask, request, jsonify, render_template
import time

app = Flask(__name__)

# Speicher für empfangene Daten
received_data = []

@app.route('/')
def home():
    return "Arduino Webserver is running!"

@app.route('/send-data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        received_data.append(data)
        print(f"Received data: {data}")
        return {"status": "success", "message": "Data received"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

@app.route('/get-data', methods=['GET'])
def get_data():
    # Sende die letzten 20 Datenpunkte zurück
    return jsonify(received_data[-20:])

@app.route('/visualize')
def visualize():
    return render_template('visualization.html')  # Visualisierung im Browser

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
