import requests
import time
from datetime import datetime

WEBHOOK_URL = "discord webhook :P" # Ganti dengan discord webhook kau sendiri niga
USER_ID = "846284633774620703" # USER ID YG MAU DI TAG

def kirim():
    data = {
        "content": f"<@{USER_ID}> jawab woi", # isi content message bebas dah
        "allowed_mentions": {
            "users": [USER_ID]
        }
    }
    
    try:
        r = requests.post(WEBHOOK_URL, json=data)
        if r.status_code == 204: # ERROR CODE NYA BS KAU TAMBAHIN BEBAS SESUAI YG NANTI DIKIRIM
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Tag terkirim")
        else:
            print(f"[!] Gagal: {r.status_code}")
            print(f"Response: {r.text}")
    except Exception as e:
        print(f"[!] Error: {e}")

count = 0
try:
    while True:
        kirim()
        count += 1
        time.sleep(0.5)
except KeyboardInterrupt:
    print(f"\nBerhenti. Total: {count} pesan") # ngasih tau udh brp pesan yg dikirim