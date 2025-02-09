from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

latest_gaze_data = {"x": 0, "y": 0, "word": "None"}

@app.route("/update_gaze", methods=["POST"])
def update_gaze():
    """Receive gaze data from JavaScript and update the latest gaze position."""
    global latest_gaze_data
    latest_gaze_data = request.json
    print(f"Received gaze data: {latest_gaze_data}")  # Debugging output
    return jsonify({"status": "success"}), 200

@app.route("/gaze_data", methods=["GET"])
def get_gaze_data():
    """Return the latest gaze position."""
    print(f"Sending gaze data: {latest_gaze_data}")  # Debugging output
    return jsonify(latest_gaze_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
