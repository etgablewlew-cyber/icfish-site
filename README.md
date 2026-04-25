# icfish

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&height=180&color=0:050505,45:062b16,100:0f172a&text=ICFISH&fontColor=39ff14&fontSize=64&fontAlignY=42&desc=educational%20phishing-awareness%20project&descAlignY=68&descSize=18&animation=fadeIn" alt="icfish hacking style banner">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Author-vyahello-39ff14?style=for-the-badge&labelColor=050505" alt="Author: vyahello">
  <img src="https://img.shields.io/badge/Open%20Source-Yes-00d4ff?style=for-the-badge&labelColor=050505" alt="Open Source: Yes">
  <img src="https://img.shields.io/badge/Maintained-Yes-7c3aed?style=for-the-badge&labelColor=050505" alt="Maintained: Yes">
  <img src="https://img.shields.io/badge/Written%20in-HTML%20%26%20PHP%20%26%20Bash-ff2bd6?style=for-the-badge&labelColor=050505" alt="Written in: HTML, PHP and Bash">
</p>

```text
┌────────────────────────────────────────────────────────────────────┐
│  EDUCATIONAL USE ONLY                                              │
│  Learn how credential-harvesting pages work so you can recognize,  │
│  explain, test, and prevent them.                                  │
│                                                                    │
│  Do not use against real people, real accounts, public networks,   │
│  production systems, or any target without explicit permission.    │
└────────────────────────────────────────────────────────────────────┘
```

`icfish` is a small educational project for understanding how phishing-style login pages are structured, how browser requests reach a PHP backend, and why two-factor prompts can be abused. It is intended for local testing, security education, awareness training, and defensive review only.

It simulates a fake iCloud sign-in experience with full front-end interactions: Apple ID entry, password entry, loading states, redirect into a fake two-factor authentication screen, six-digit code input, and local test-output logging.

The author is not responsible for misuse, improper usage, illegal activity, policy violations, data loss, account compromise, or damage caused by this project. Use fake values only.

## Boundaries

```text
Allowed:       http://localhost
Allowed:       http://localhost:8080
Allowed:       http://192.168.x.x       only on your own authorized private network
Not allowed:   internet exposure, tunneling, public hosting, real credential collection
```

Example fake values:

```text
Apple ID:  student@example.test
Password:  training-password
2FA code:  123456
```

## Files

```text
.
├── index.html                  # Fake iCloud training login page with Apple ID/password flow
├── pages/
│   └── verify.html             # Fake iCloud training 2FA page with six-digit code flow
├── captures/
│   ├── capture.php             # Local JSON receiver for test credentials
│   └── capture_2fa.php         # Local JSON receiver for test 2FA codes
└── start_server.sh             # Convenience launcher for the PHP dev server
```

Generated test output is written to `creds/` in the project directory. Treat that folder as sensitive local test output and delete it after exercises.

## Quick Start

```bash
git clone https://github.com/vyahello/icfish.git
cd icfish
chmod +x start_server.sh
./start_server.sh
```

The script prints the local URLs it detects. Prefer `localhost` for solo testing:

```text
http://localhost
http://localhost:8080
```

For an authorized device on the same private network, use only a private `192.168.x.x` URL printed by the script:

```text
http://192.168.x.x
http://192.168.x.x:8080
```

## Manual Start

Run on port `8080` without root:

```bash
php -S 0.0.0.0:8080
```

Run on port `80` only if you intentionally want the standard HTTP port for a closed educational exercise:

```bash
sudo php -S 0.0.0.0:80
```

## Educational Flow

```text
┌──────────────┐     ┌──────────────────────┐     ┌───────────────────┐
│ index.html   │ --> │ captures/capture.php │ --> │ pages/verify.html │
│ fake iCloud  │     │ local test logs      │     │ fake 2FA code     │
│ login/pass   │     │                      │     │ interaction       │
└──────────────┘     └──────────────────────┘     └─────────┬─────────┘
                                                             │
                                                             v
                                                   ┌──────────────────────────┐
                                                   │ captures/capture_2fa.php │
                                                   │ local test logs          │
                                                   └──────────────────────────┘
```

1. Open the local project URL.
2. Enter fake training credentials.
3. The page sends a local JSON request to `captures/capture.php`.
4. Enter a fake six-digit training code.
5. The page sends a local JSON request to `captures/capture_2fa.php`.

## Viewing Test Output

```bash
ls -lh creds/
tail -f creds/all_credentials.log
tail -f creds/all_2fa_codes.log
```

Expected output files:

```text
credentials_YYYY-MM-DD_HH-MM-SS.txt
2fa_code_YYYY-MM-DD_HH-MM-SS.txt
all_credentials.log
all_2fa_codes.log
```

## Cleanup

Remove generated test captures after testing:

```bash
rm -rf creds/
```

## Safety Checklist

```text
[ ] I am using fake credentials only.
[ ] I am testing on localhost or an authorized 192.168.x.x private network.
[ ] I am not exposing this service to the internet.
[ ] I have permission for every device involved.
[ ] I deleted generated test captures after the exercise.
```

## Learning Goals

- Recognize cloned login-page structure.
- Understand how form data can be sent to a backend endpoint.
- Inspect local output to learn what sensitive data exposure looks like.
- Practice explaining why users should verify domains before entering credentials.
- Practice safe teardown and evidence handling in a controlled environment.

```text
Use this project to learn how phishing works so you can detect, explain,
and prevent it. Do not use it to deceive or compromise anyone.
```
