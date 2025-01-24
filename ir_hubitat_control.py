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

def execute_hubitat_command(mapping):
    device_id = mapping["device"]
    command = mapping["command"]
    var = "/" + mapping["var"] if mapping["var"] else ""
    send_request(device_id, command, var)

# Listen for IR signals using irw command
def listen_for_ir_signals():
    print("Listening for IR signals...")
    mappings = load_mappings()
    process = subprocess.Popen(["irw"], stdout=subprocess.PIPE, text=True)

    try:
        for line in process.stdout:
            parts = line.strip().split()
            if len(parts) >= 4:  # Format: <code> <repeat> <key> <remote>
                remote = parts[3]
                ir_key = parts[2]
                
                # Check if remote exists in mappings
                if remote in mappings:
                    # Check if key exists for this remote
                    if ir_key in mappings[remote]:
                        print(f"IR Key Detected: {ir_key} from remote: {remote}")
                        mapping = mappings[remote][ir_key]
                        execute_hubitat_command(mapping)
                    else:
                        print(f"Unknown IR key: {ir_key} for remote: {remote}")
                else:
                    print(f"Unknown remote: {remote}")
    except KeyboardInterrupt:
        print("Stopping IR listener...")
        process.terminate()

def process_ir_code(code, remote):
    mappings = load_mappings()
    if remote in mappings and code in mappings[remote]:
        execute_hubitat_command(mappings[remote][code])

if __name__ == "__main__":
    listen_for_ir_signals()
