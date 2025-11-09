#!/usr/bin/env python3
"""
RTL-SDR Spectrum Wallpaper Generator
Captures radio spectrum data and displays it as a stylised ASCII-art wallpaper
"""

import subprocess
import time
import os
import signal
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ============ CONFIGURATION ============
FREQ_START = "88M"      # Start frequency (e.g., 88M for FM radio)
FREQ_END = "108M"       # End frequency
FREQ_STEP = "10k"       # Frequency step
GAIN = "40"             # RTL-SDR gain (0-50, or 'auto')
INTEGRATION_TIME = "2s" # How long to integrate signal
UPDATE_INTERVAL = 5     # Seconds between wallpaper updates

# Display settings
WALLPAPER_PATH = str(Path.home() / ".rtl_spectrum_wallpaper.png")
SCREEN_WIDTH = 1920     # Adjust to your resolution
SCREEN_HEIGHT = 1080    # Adjust to your resolution

# Visual style
BG_COLOR = (10, 10, 20)              # Dark blue background
SPECTRUM_COLOR = (0, 255, 100)       # Green spectrum
PEAK_COLOR = (255, 50, 50)           # Red for peaks
TEXT_COLOR = (100, 255, 200)         # Cyan text
GRID_COLOR = (30, 30, 50)            # Subtle grid

ASCII_CHARS = [" ", "░", "▒", "▓", "█"]  # Intensity characters
BARS_STYLE = True        # Set False for ASCII-only style

# ============ GLOBAL VARIABLES ============
rtl_power_process = None

# ============ SIGNAL HANDLER ============
def signal_handler(sig, frame):
    """Clean shutdown on Ctrl+C"""
    print("\n[*] Shutting down gracefully...")
    if rtl_power_process:
        rtl_power_process.terminate()
        rtl_power_process.wait()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ============ RTL-SDR FUNCTIONS ============
def start_rtl_power():
    """Start rtl_power in continuous mode"""
    csv_path = "/tmp/rtl_spectrum.csv"
    
    # Remove old CSV if exists
    if os.path.exists(csv_path):
        os.remove(csv_path)
    
    cmd = [
        "rtl_power",
        "-f", f"{FREQ_START}:{FREQ_END}:{FREQ_STEP}",
        "-g", GAIN,
        "-i", INTEGRATION_TIME,
        "-e", INTEGRATION_TIME,
        csv_path
    ]
    
    print(f"[*] Starting rtl_power: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    return process, csv_path

def read_spectrum_data(csv_path):
    """Read the latest spectrum data from CSV"""
    try:
        if not os.path.exists(csv_path):
            return None
        
        # Read last line of CSV (most recent data)
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            if not lines:
                return None
            
            last_line = lines[-1].strip()
            parts = last_line.split(',')
            
            if len(parts) < 6:
                return None
            
            # CSV format: date, time, freq_low, freq_high, step, samples, db1, db2, ...
            freq_low = float(parts[2])
            freq_high = float(parts[3])
            db_values = [float(x) for x in parts[6:]]
            
            return {
                'freq_low': freq_low,
                'freq_high': freq_high,
                'db_values': db_values
            }
    except Exception as e:
        print(f"[!] Error reading spectrum data: {e}")
        return None

# ============ VISUALISATION FUNCTIONS ============
def normalize_db_values(db_values):
    """Normalise dB values to 0-1 range"""
    if not db_values:
        return []
    
    min_db = min(db_values)
    max_db = max(db_values)
    
    if max_db == min_db:
        return [0.5] * len(db_values)
    
    return [(db - min_db) / (max_db - min_db) for db in db_values]

def create_spectrum_image(spectrum_data):
    """Create the spectrum wallpaper image"""
    img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    if spectrum_data is None:
        # Draw "Waiting for data..." message
        try:
            font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSansMono.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        draw.text((SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2), 
                  "Waiting for RTL-SDR data...", 
                  fill=TEXT_COLOR, font=font)
        return img
    
    db_values = spectrum_data['db_values']
    freq_low = spectrum_data['freq_low']
    freq_high = spectrum_data['freq_high']
    
    if not db_values:
        return img
    
    normalized = normalize_db_values(db_values)
    
    # Calculate dimensions
    margin_x = 100
    margin_y = 100
    plot_width = SCREEN_WIDTH - 2 * margin_x
    plot_height = SCREEN_HEIGHT - 2 * margin_y
    
    # Draw grid
    for i in range(0, 11, 2):
        y = margin_y + int(plot_height * i / 10)
        draw.line([(margin_x, y), (SCREEN_WIDTH - margin_x, y)], fill=GRID_COLOR, width=1)
    
    for i in range(0, 11, 2):
        x = margin_x + int(plot_width * i / 10)
        draw.line([(x, margin_y), (x, SCREEN_HEIGHT - margin_y)], fill=GRID_COLOR, width=1)
    
    # Draw spectrum bars or ASCII
    bar_width = plot_width / len(normalized)
    
    for i, value in enumerate(normalized):
        x = margin_x + i * bar_width
        bar_height = value * plot_height
        y = SCREEN_HEIGHT - margin_y - bar_height
        
        if BARS_STYLE:
            # Draw gradient bars
            color = spectrum_color_gradient(value)
            draw.rectangle(
                [x, y, x + bar_width - 1, SCREEN_HEIGHT - margin_y],
                fill=color
            )
        else:
            # ASCII style - draw characters
            char_index = int(value * (len(ASCII_CHARS) - 1))
            char = ASCII_CHARS[char_index]
            
            try:
                font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSansMono.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Stack characters vertically based on intensity
            num_chars = int(value * 30)
            for j in range(num_chars):
                char_y = SCREEN_HEIGHT - margin_y - j * 20
                draw.text((x, char_y), char, fill=SPECTRUM_COLOR, font=font)
    
    # Draw labels
    try:
        font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSansMono.ttf", 24)
        small_font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSansMono.ttf", 18)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Title
    title = f"RTL-SDR SPECTRUM: {freq_low/1e6:.1f} - {freq_high/1e6:.1f} MHz"
    draw.text((margin_x, 30), title, fill=TEXT_COLOR, font=font)
    
    # Frequency labels
    for i in range(0, 6):
        freq_mhz = freq_low/1e6 + (freq_high - freq_low)/1e6 * i / 5
        x = margin_x + int(plot_width * i / 5)
        draw.text((x - 30, SCREEN_HEIGHT - margin_y + 10), 
                  f"{freq_mhz:.1f}", fill=TEXT_COLOR, font=small_font)
    
    # Timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    draw.text((SCREEN_WIDTH - margin_x - 200, 30), timestamp, fill=TEXT_COLOR, font=small_font)
    
    return img

def spectrum_color_gradient(value):
    """Generate colour gradient based on intensity"""
    if value < 0.3:
        # Low: dark blue to blue
        intensity = int(value / 0.3 * 255)
        return (0, 0, intensity)
    elif value < 0.6:
        # Medium: blue to green
        t = (value - 0.3) / 0.3
        return (0, int(t * 255), int((1-t) * 255))
    elif value < 0.8:
        # High: green to yellow
        t = (value - 0.6) / 0.2
        return (int(t * 255), 255, 0)
    else:
        # Peak: yellow to red
        t = (value - 0.8) / 0.2
        return (255, int((1-t) * 255), 0)

def set_gnome_wallpaper(image_path):
    """Set GNOME desktop wallpaper"""
    try:
        # Convert to absolute path and file:// URI
        abs_path = os.path.abspath(image_path)
        uri = f"file://{abs_path}"
        
        # Set wallpaper
        subprocess.run([
            "gsettings", "set", "org.gnome.desktop.background",
            "picture-uri", uri
        ], check=True)
        
        # Also set for dark mode
        subprocess.run([
            "gsettings", "set", "org.gnome.desktop.background",
            "picture-uri-dark", uri
        ], check=True)
        
        print(f"[+] Wallpaper updated: {image_path}")
        return True
    except Exception as e:
        print(f"[!] Error setting wallpaper: {e}")
        return False

# ============ MAIN LOOP ============
def main():
    """Main execution loop"""
    print("=" * 60)
    print("RTL-SDR SPECTRUM WALLPAPER")
    print("=" * 60)
    print(f"[*] Frequency range: {FREQ_START} - {FREQ_END}")
    print(f"[*] Wallpaper path: {WALLPAPER_PATH}")
    print(f"[*] Update interval: {UPDATE_INTERVAL}s")
    print(f"[*] Press Ctrl+C to stop")
    print("=" * 60)
    
    global rtl_power_process
    
    # Start rtl_power
    rtl_power_process, csv_path = start_rtl_power()
    
    # Wait for initial data
    print("[*] Waiting for initial spectrum data...")
    time.sleep(5)
    
    # Main loop
    while True:
        try:
            # Read spectrum data
            spectrum_data = read_spectrum_data(csv_path)
            
            # Create wallpaper image
            img = create_spectrum_image(spectrum_data)
            
            # Save image
            img.save(WALLPAPER_PATH, 'PNG')
            
            # Set as wallpaper
            set_gnome_wallpaper(WALLPAPER_PATH)
            
            # Wait before next update
            time.sleep(UPDATE_INTERVAL)
            
        except Exception as e:
            print(f"[!] Error in main loop: {e}")
            time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
