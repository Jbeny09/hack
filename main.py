import requests
import json
import socket # Digunakan untuk mendapatkan IP lokal (opsional, tapi berguna untuk melihat perbedaan)

def get_public_ip():
    """
    Mengambil alamat IP publik dari layanan eksternal.
    """
    try:
        # Menggunakan layanan seperti ipify.org atau ifconfig.me
        # untuk mendapatkan IP publik.
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status() # Akan memunculkan HTTPError untuk status kode error
        ip_data = response.json()
        return ip_data['ip']
    except requests.exceptions.RequestException as e:
        print(f"Error saat mengambil IP publik: {e}")
        return "Tidak dapat mengambil IP publik"

def get_local_ip():
    """
    Mengambil alamat IP lokal mesin yang menjalankan skrip.
    Perlu diingat, ini adalah IP di jaringan lokal (LAN), bukan IP publik.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) # Menghubungkan ke server DNS Google, tidak benar-benar mengirim data
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error saat mengambil IP lokal: {e}")
        return "Tidak dapat mengambil IP lokal"

def send_to_discord_webhook(webhook_url, username, public_ip, local_ip=None):
    """
    Mengirim informasi IP ke Discord melalui webhook.
    """
    if not webhook_url:
        print("URL Webhook Discord belum diatur. Pesan tidak terkirim.")
        return

    message_content = f"**Deteksi Koneksi Baru!**\n" \
                      f"**IP Publik:** `{public_ip}`\n"
    if local_ip:
        message_content += f"**IP Lokal:** `{local_ip}`\n"
    message_content += f"**User Agent:** `{requests.utils.default_headers()['User-Agent']}`" # Mendapatkan user agent default

    data = {
        "username": username,
        "content": message_content
    }

    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status() # Akan memunculkan HTTPError untuk status kode error
        print(f"Pesan berhasil dikirim ke Discord! Status Code: {response.status_code}")
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh} - Pastikan URL webhook benar dan aktif.")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Koneksi: {errc} - Pastikan ada koneksi internet.")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt} - Permintaan ke webhook kehabisan waktu.")
    except requests.exceptions.RequestException as err:
        print(f"Ada error lain: {err}")

if __name__ == "__main__":
    # --- KONFIGURASI PENTING ---
    DISCORD_WEBHOOK_URL = "GANTI_DENGAN_URL_WEBHOOK_DISCORD_ANDA" # <-- Ganti ini!
    BOT_USERNAME = "CyberGuard IP Logger" # Nama yang akan muncul di Discord

    print("Mencoba mengambil alamat IP...")
    public_ip_address = get_public_ip()
    local_ip_address = get_local_ip() # Ini opsional, bisa dihapus jika tidak diperlukan

    print(f"IP Publik Anda: {public_ip_address}")
    print(f"IP Lokal Anda: {local_ip_address}")

    print("Mencoba mengirim ke Discord...")
    send_to_discord_webhook(DISCORD_WEBHOOK_URL, BOT_USERNAME, public_ip=public_ip_address, local_ip=local_ip_address)

    input("\nTekan Enter untuk keluar...") # Agar jendela konsol tidak langsung tertutup
