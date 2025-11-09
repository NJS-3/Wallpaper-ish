#!/bin/bash
# RTL-SDR Spectrum Wallpaper Installation Script

echo "============================================"
echo "RTL-SDR Spectrum Wallpaper Installer"
echo "============================================"

# Check if rtl-sdr is installed
if ! command -v rtl_power &> /dev/null; then
    echo "[!] rtl_power not found. Installing rtl-sdr..."
    sudo dnf install -y rtl-sdr
fi

# Check for Python dependencies
echo "[*] Checking Python dependencies..."
python3 -c "import PIL" 2>/dev/null || {
    echo "[!] PIL/Pillow not found. Installing..."
    sudo dnf install -y python3-pillow
}

# Make script executable
echo "[*] Making script executable..."
chmod +x ~/rtl_spectrum_wallpaper.py

# Install systemd service
echo "[*] Installing systemd service..."
mkdir -p ~/.config/systemd/user/
cp rtl-spectrum-wallpaper.service ~/.config/systemd/user/

# Reload systemd
systemctl --user daemon-reload

# Enable service
echo "[*] Enabling service to start at boot..."
systemctl --user enable rtl-spectrum-wallpaper.service

echo ""
echo "============================================"
echo "Installation complete!"
echo "============================================"
echo ""
echo "Commands:"
echo "  Start now:    systemctl --user start rtl-spectrum-wallpaper"
echo "  Stop:         systemctl --user stop rtl-spectrum-wallpaper"
echo "  Status:       systemctl --user status rtl-spectrum-wallpaper"
echo "  Disable:      systemctl --user disable rtl-spectrum-wallpaper"
echo "  View logs:    journalctl --user -u rtl-spectrum-wallpaper -f"
echo ""
echo "Edit ~/rtl_spectrum_wallpaper.py to customise:"
echo "  - Frequency range (FREQ_START, FREQ_END)"
echo "  - Screen resolution (SCREEN_WIDTH, SCREEN_HEIGHT)"
echo "  - Colours and style (BG_COLOR, SPECTRUM_COLOR, etc.)"
echo "  - Update interval (UPDATE_INTERVAL)"
echo ""
echo "Start the service now? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    systemctl --user start rtl-spectrum-wallpaper
    echo "[+] Service started! Check your desktop wallpaper in a few seconds."
fi
