from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Your GazeCloud API key
API_KEY = "your-api-key-here"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process_gaze_data", methods=["POST"])
def process_gaze_data():
    # Receive gaze data from the client
    gaze_data = request.json

    # Example: Print gaze data (timestamp, x, y)
    print(f"Gaze Data Received: {gaze_data}")

    # Optionally process or store the gaze data here

    return {"status": "success"}

if __name__ == "__main__":
    app.run(debug=True)
