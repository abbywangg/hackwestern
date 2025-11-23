import os
import time
import json
from flask import Flask, jsonify
import threading

# --- CONFIGURATION ---
# The path to the JSON file on your MAC that is being updated by your other tools
# For testing, create a dummy file at this location or change this path.
WATCHED_FILE_PATH = "source_data.json"

app = Flask(__name__)

# Global variable to hold the latest data
latest_data = {}

def load_file():
    """Reads the local JSON file safely."""
    global latest_data
    if os.path.exists(WATCHED_FILE_PATH):
        try:
            with open(WATCHED_FILE_PATH, 'r') as f:
                latest_data = json.load(f)
            # Add a timestamp to prove it's live
            latest_data['_server_timestamp'] = time.time()
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        latest_data = {"status": "waiting_for_file", "path": WATCHED_FILE_PATH}

@app.route('/data')
def serve_data():
    """This is the endpoint the Windows PC will hit."""
    load_file() # Reload data on every request to ensure freshness
    return jsonify(latest_data)

def create_dummy_data():
    """
    OPTIONAL: If you don't have a real file generating yet, 
    this function creates dummy data so you can test the connection.
    """
    while True:
        dummy_content = {
            "sensor_id": 101,
            "temperature": 20 + (time.time() % 10), # Fake fluctuating data
            "battery": 98,
            "status": "active"
        }
        with open(WATCHED_FILE_PATH, 'w') as f:
            json.dump(dummy_content, f)
        time.sleep(1)

if __name__ == '__main__':
    # Uncomment the line below to generate fake data for testing
    # threading.Thread(target=create_dummy_data, daemon=True).start()

    print(f"--- HOSTING FILE: {WATCHED_FILE_PATH} ---")
    print("--- CONNECT WINDOWS USB CABLE NOW ---")
    # Host 0.0.0.0 allows connection from external devices (the Windows PC via USB)
    app.run(host='0.0.0.0', port=5000)