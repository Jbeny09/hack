// starting QR :P
// BARU DI TEST DI LINUX DI WINDOWS BELOM sabar bang ._.
// actually kali linux but idk kalo di windows work 
const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const client = new Client({
    authStrategy: new LocalAuth()
});

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('WhatsApp Bot siap!');
});

// Konfigurasi Gambar :P
const GAMBAR_PATH = '/home/ben/gambar.jpg'; // misalnya bisa diganti sesuai nama linux

// Erm sending da message bro dawg
client.on('message', async msg => {
    const text = msg.body.toLowerCase().trim();

    // kalo ada kata 'done' di text atau sentence org
    if (text.includes('done')) {
        // function disini
        try {
            const media = MessageMedia.fromFilePath(GAMBAR_PATH);
            await client.sendMessage(msg.from, media);
            console.log(`Mengirim gambar ke ${msg.from}`);
        } catch (err) {
            await msg.reply(`❌ Gambar tidak ditemukan di ${GAMBAR_PATH}`); // kalo ga ketemu gambar pathnya HARUS BENER PATHNYA
            console.log(`Error: ${err.message}`);
        }
    }
});

client.initialize();
