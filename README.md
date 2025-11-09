# RTL-SDR Spectrum Wallpaper for Fedora

Live radio spectrum visualisation as your desktop background!
## Requirements

- Fedora Linux with GNOME desktop
- RTL-SDR dongle
- Python 3 with Pillow (PIL)

## Quick Installation

1. **Make install script executable:**
   ```bash
   chmod +x install.sh
   ```

2. **Run installer:**
   ```bash
   ./install.sh
   ```

3. **Done!** Your wallpaper should start updating automatically.

## Manual Installation

If you prefer to install manually:

```bash
# Install dependencies
sudo dnf install rtl-sdr python3-pillow

# Make script executable
chmod +x ~/rtl_spectrum_wallpaper.py

# Copy service file
mkdir -p ~/.config/systemd/user/
cp rtl-spectrum-wallpaper.service ~/.config/systemd/user/

# Enable and start
systemctl --user daemon-reload
systemctl --user enable rtl-spectrum-wallpaper
systemctl --user start rtl-spectrum-wallpaper
```

## Customisation

Edit `~/rtl_spectrum_wallpaper.py` and modify these settings:

### Frequency Range
```python
FREQ_START = "88M"      # Start frequency
FREQ_END = "108M"       # End frequency (FM radio band example)
FREQ_STEP = "10k"       # Resolution
```

Common frequency ranges:
- FM Radio: `88M` to `108M`
- Air Band: `118M` to `137M`
- 2m Ham: `144M` to `148M`
- Weather Satellites: `137M` to `138M`
- Wide scan: `24M` to `1700M` (slower updates)

### Screen Resolution
```python
SCREEN_WIDTH = 1920     # Your monitor width
SCREEN_HEIGHT = 1080    # Your monitor height
```

### Update Speed
```python
UPDATE_INTERVAL = 5     # Seconds between updates
INTEGRATION_TIME = "2s" # RTL-SDR integration time
```

### Visual Style
```python
# Colour scheme (RGB tuples)
BG_COLOR = (10, 10, 20)           # Background
SPECTRUM_COLOR = (0, 255, 100)    # Main spectrum colour
PEAK_COLOR = (255, 50, 50)        # Peak indicators
TEXT_COLOR = (100, 255, 200)      # Labels
GRID_COLOR = (30, 30, 50)         # Grid lines

# Display mode
BARS_STYLE = True  # False for pure ASCII character mode
```

### RTL-SDR Gain
```python
GAIN = "40"  # 0-50, or "auto"
```

## Usage

### Control the Service

```bash
# Start
systemctl --user start rtl-spectrum-wallpaper

# Stop
systemctl --user stop rtl-spectrum-wallpaper

# Restart (after editing config)
systemctl --user restart rtl-spectrum-wallpaper

# Check status
systemctl --user status rtl-spectrum-wallpaper

# View live logs
journalctl --user -u rtl-spectrum-wallpaper -f

# Disable autostart
systemctl --user disable rtl-spectrum-wallpaper
```

### Test Without Installing

Run the script directly to test your settings:

```bash
python3 ~/rtl_spectrum_wallpaper.py
```

Press Ctrl+C to stop.
