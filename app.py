from flask import Flask, render_template, request, jsonify, session
import json
import requests
import os
import subprocess
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Configuration
HUBITAT_IP = "192.168.1.220"
ACCESS_TOKEN = "a7d9d3bc-f4ab-49ae-8220-1b6f6c45ec87"
MAPPINGS_FILE = "ir_mappings.json"
LIRC_DEVICE = "/var/run/lirc/lircd-transmit"

IR_KEYS = ["KEY_POWER", "KEY_INPUT",
    "KEY_HOME", "KEY_BACK", "KEY_INFO", "KEY_UP",
    "KEY_LEFT", "KEY_OK", "KEY_RIGHT", "KEY_DOWN",
    "KEY_VOLUMEUP", "KEY_VOLUMEDOWN", "KEY_MUTE",
    "KEY_CHANNELUP", "KEY_CHANNELDOWN", "KEY_RED",
    "KEY_GREEN", "KEY_YELLOW", "KEY_BLUE",
    "KEY_PLAY", "KEY_PAUSE", "KEY_STOP",
    "KEY_RECORD", "KEY_FASTFORWARD", "KEY_REWIND", "KEY_OPTION",
    "KEY_1", "KEY_2", "KEY_3", "KEY_4",
    "KEY_5", "KEY_6", "KEY_7", "KEY_8", "KEY_9", "KEY_0"]

# Create a thread pool executor
executor = ThreadPoolExecutor(max_workers=1)

# Helper functions
def load_mappings():
    if os.path.exists(MAPPINGS_FILE):
        with open(MAPPINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_mappings(mappings):
    with open(MAPPINGS_FILE, 'w') as f:
        json.dump(mappings, f, indent=2)

def get_devices():
    url = f"http://{HUBITAT_IP}/apps/api/70/devices"
    params = {'access_token': ACCESS_TOKEN}
    try:
        response = requests.get(url, params=params)
        devices = response.json()
        return sorted(devices, key=lambda x: x.get('label', '').lower())
    except:
        return []

def restart_control_script():
    # Run the restart command in a separate thread
    executor.submit(_restart_service)

def _restart_service():
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', 'ir-control.service'],
                      check=True,
                      capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error restarting service: {e.stderr.decode()}")
    except Exception as e:
        print(f"Unexpected error restarting service: {str(e)}")

def get_available_remotes():
    try:
        result = subprocess.run(['irsend', '-d', LIRC_DEVICE, 'LIST', '', ''],
                              capture_output=True, text=True)
        remotes = result.stdout.strip().split('\n')
        return [r.strip() for r in remotes if r.strip()]
    except:
        return []

def send_continuous_ir(remote, key, duration=5):
    try:
        # Start continuous sending
        subprocess.run(['irsend', '-d', LIRC_DEVICE, 'SEND_START', remote, key])
        time.sleep(duration)
        # Stop sending
        subprocess.run(['irsend', '-d', LIRC_DEVICE, 'SEND_STOP', remote, key])
        return True
    except:
        return False

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['form_data'] = {
            'remote': request.form.get('remote'),
            'ir_key': request.form.get('ir_key'),
            'device': request.form.get('device'),
            'command': request.form.get('command')
        }
    
    form_data = session.get('form_data', {})
    
    mappings = load_mappings()
    devices = get_devices()
    remotes = get_available_remotes()
    return render_template('index.html', 
                         remotes=remotes,
                         devices=devices,
                         ir_keys=IR_KEYS,
                         mappings=mappings,
                         form_data=form_data)

@app.route('/get_device_commands/<device_id>')
def get_device_commands(device_id):
    url = f"http://{HUBITAT_IP}/apps/api/70/devices/{device_id}/commands"
    params = {'access_token': ACCESS_TOKEN}
    try:
        response = requests.get(url, params=params)
        return jsonify(response.json())
    except:
        return jsonify([])

@app.route('/add_mapping', methods=['POST'])
def add_mapping():
    mapping = request.json
    mappings = load_mappings()
    
    # Initialize remote if it doesn't exist
    if mapping['remote'] not in mappings:
        mappings[mapping['remote']] = {}
    
    # Add the mapping under the remote
    mappings[mapping['remote']][mapping['ir_key']] = {
        'device': mapping['device_id'],
        'command': mapping['command'],
        'var': '/'.join(mapping['parameters']) if mapping['parameters'] else None
    }
    
    save_mappings(mappings)
    restart_control_script()
    return jsonify({"status": "success"})

@app.route('/remove_mapping', methods=['POST'])
def remove_mapping():
    data = request.json
    remote = data.get('remote')
    ir_key = data.get('ir_key')
    
    try:
        mappings = load_mappings()
        if remote in mappings and ir_key in mappings[remote]:
            del mappings[remote][ir_key]
            # Remove remote if empty
            if not mappings[remote]:
                del mappings[remote]
            save_mappings(mappings)
            restart_control_script()
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Mapping not found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/teach_ir/<remote>/<key>', methods=['POST'])
def teach_ir(remote, key):
    success = send_continuous_ir(remote, key)
    return jsonify({"status": "success" if success else "error"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
