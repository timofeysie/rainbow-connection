#!/bin/bash
# Startup script for Emoji OS Zero v0.3.1
# This script handles the Python environment setup for rc.local

echo "=== Emoji OS Zero v0.3.1 Startup ===" >> /home/tim/rc.local.log

# Run as user 'tim' to get the correct environment
sudo -u tim bash << 'EOF'
cd /home/tim/emoji-os

# Use the user's Python environment
export PATH="/home/tim/.local/bin:$PATH"
export PYTHONPATH="/home/tim/.local/lib/python3.11/site-packages:$PYTHONPATH"

# Check if bleak is available in user environment
if python3 -c "import bleak" 2>/dev/null; then
    echo "✓ Bleak module found in user environment" >> /home/tim/rc.local.log
else
    echo "✗ Bleak module not found, installing..." >> /home/tim/rc.local.log
    pip3 install --user bleak
fi

# Run the emoji OS
echo "Starting Emoji OS Zero v0.3.1..." >> /home/tim/rc.local.log
python3 emoji_os_zero_1.py >> /home/tim/rc.local.log 2>&1

echo "Emoji OS Zero v0.3.1 stopped" >> /home/tim/rc.local.log
EOF
