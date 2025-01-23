import json
import subprocess
import time

# Load mapping data from JSON file
MAPPING_FILE = "ir_mappings.json"
HUBITAT_API_URL_TEMPLATE = "http://192.168.1.220/apps/api/70/devices/{device}/{command}{var}?access_token=a7d9d3bc-f4ab-49ae-8220-1b6f6c45ec87"

# Load mapping file
def load_mappings():
    with open(MAPPING_FILE, "r") as file:
        return json.load(file)

# Function to send a curl request with rate limiting
last_request_time = 0.0
def send_request(device, command, var):
    global last_request_time
    current_time = time.time()
    if current_time - last_request_time >= 1:
        # Clean up the var string to remove trailing slash if present
        var = var.rstrip('/')
        url = HUBITAT_API_URL_TEMPLATE.format(device=device, command=command, var=var)
        try:
            response = subprocess.run(["curl", "-X", "GET", url], check=True, text=True, capture_output=True)
            print(f"Request sent to {url}: {response.stdout}")
            last_request_time = current_time
        except subprocess.CalledProcessError as e:
            print(f"Error sending request: {e.stderr}")
    else:
        print("Skipping request to prevent flooding")

# Listen for IR signals using irw command
def listen_for_ir_signals():
    print("Listening for IR signals...")
    mappings = load_mappings()
    process = subprocess.Popen(["irw"], stdout=subprocess.PIPE, text=True)

    try:
        for line in process.stdout:
            parts = line.strip().split()
            if len(parts) >= 3:
                ir_key = parts[2]
                if ir_key in mappings:
                    print(f"IR Key Detected: {ir_key}")
                    device_info = mappings[ir_key]
                    device_id = device_info["device"]
                    command = device_info["command"]
                    var = "/" + device_info["var"] if device_info["var"] else ""

                    send_request(device_id, command, var)
                else:
                    print(f"Unknown IR key: {ir_key}")
    except KeyboardInterrupt:
        print("Stopping IR listener...")
        process.terminate()

def process_ir_code(code):
    mappings = load_mappings()
    for ir_key, mapping in mappings.items():
        if code == ir_key and current_remote == mapping['remote']:
            execute_hubitat_command(mapping)

if __name__ == "__main__":
    listen_for_ir_signals()
