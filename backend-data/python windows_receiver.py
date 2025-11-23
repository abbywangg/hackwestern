import requests
import json
import csv
import time
import os
from datetime import datetime

# --- CONFIGURATION ---
# 1. Open CMD on Windows, type 'ipconfig', find the Gateway for the Apple USB adapter.
# It is usually 172.20.10.1
MAC_IP_ADDRESS = "172.20.10.1" 
MAC_PORT = "5000"
URL = f"http://{MAC_IP_ADDRESS}:{MAC_PORT}/data"

# File paths where Windows will save the data
OUTPUT_JSON = "received_live.json"
OUTPUT_CSV = "received_history.csv"

def flatten_json(y):
    """Helper to flatten nested JSON so it fits in a CSV line."""
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

def run_bridge():
    print(f"--- SEARCHING FOR MAC AT {URL} ---")
    
    # Create CSV headers flag
    file_exists = os.path.isfile(OUTPUT_CSV)
    
    while True:
        try:
            # 1. REQUEST Data from Mac
            response = requests.get(URL, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                
                # 2. SAVE raw JSON (Overwrites specifically to keep "current state")
                with open(OUTPUT_JSON, 'w') as f:
                    json.dump(data, f, indent=4)
                
                # 3. PROCESS to CSV (Appends history)
                flat_data = flatten_json(data)
                
                # Add local Windows timestamp
                flat_data['windows_receive_time'] = datetime.now().strftime("%H:%M:%S")
                
                with open(OUTPUT_CSV, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=flat_data.keys())
                    
                    # If new file, write header
                    if not os.path.isfile(OUTPUT_CSV) or os.stat(OUTPUT_CSV).st_size == 0:
                        writer.writeheader()
                        
                    writer.writerow(flat_data)
                
                print(f"[{flat_data['windows_receive_time']}] Synced: {data}")
            
            else:
                print(f"Connected, but Mac returned error: {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"Scanning for connection on {MAC_IP_ADDRESS}...")
            time.sleep(2) # Wait longer if disconnected
        except Exception as e:
            print(f"Error: {e}")
        
        # Poll rate (Every 0.5 seconds)
        time.sleep(0.5)

if __name__ == "__main__":
    # Ensure clean start
    print("Starting Windows Bridge System...")
    run_bridge()