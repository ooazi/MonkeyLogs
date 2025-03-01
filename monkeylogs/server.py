from flask import Flask, jsonify, render_template, send_from_directory
import os
import json
import numpy as np
import subprocess

# Paths
LOG_PATH = os.path.expanduser("~/monkeylogger/monkeylogs/log/log.jsonc")
GRAPH_DIR = os.path.expanduser("~/monkeylogger/monkeylogs/static/graphs/")

app = Flask(__name__)

def load_typing_data():
    """📂 Loads typing session data from log file."""
    if not os.path.exists(LOG_PATH):
        return []

    try:
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
            return data.get("sessions", [])
    except json.JSONDecodeError:
        return []
    
def get_last_modified_time():
    """📂 Get last modified timestamp of log.jsonc."""
    return os.path.getmtime(LOG_PATH) if os.path.exists(LOG_PATH) else 0

def compute_averages(data):
    """📊 Computes averages for WPM and session duration."""
    if not data:
        return {"avg_wpm": 0, "avg_session_duration": 0}

    wpm_values = [s["wpm"] for s in data]
    session_durations = [s["session_duration"] for s in data]

    return {
        "avg_wpm": round(np.mean(wpm_values), 2),
        "avg_session_duration": round(np.mean(session_durations), 2)
    }

LAST_GENERATED_TIME = 0  # Keeps track of the last time graphs were generated

def generate_graphs():
    """📊 Runs graph generation script only if new data is detected."""
    global LAST_GENERATED_TIME

    current_modified_time = get_last_modified_time()

    if current_modified_time > LAST_GENERATED_TIME:
        print("📊 New data detected! Regenerating graphs...")
        subprocess.run(["python3", os.path.expanduser("~/monkeylogger/monkeylogs/graph.py")])
        LAST_GENERATED_TIME = current_modified_time  # Update last generated time
    else:
        print("✅ Graphs are already up-to-date. No need to regenerate.")

def ensure_graphs():
    """🚀 Ensure graphs are generated before the server starts."""
    if not os.path.exists(GRAPH_DIR):
        os.makedirs(GRAPH_DIR)

    print("⏳ Ensuring graphs are up to date before server starts...")
    generate_graphs()  # Only regenerates if necessary

@app.route("/")
def index():
    """📄 Serve the main frontend page."""
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    """🖼️ Serve the favicon."""
    return send_from_directory(os.path.join(app.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.route("/api/stats")
def get_stats():
    """📊 API to get typing statistics and regenerate graphs if needed."""
    data = load_typing_data()

    # Debugging: Print data to see if sessions exist
    print("📂 Loaded Data from log.jsonc:", data)

    averages = compute_averages(data)

    # Check if graphs need to be updated
    generate_graphs()

    return jsonify({"averages": averages, "sessions": data})

if __name__ == "__main__":
    print("🚀 Starting MonkeyLogs server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)