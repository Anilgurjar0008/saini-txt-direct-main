import requests, json, os, asyncio, base64, re
from pyrogram import filters
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64decode
import yt_dlp

from .utils import app

def decrypt(enc):
    enc = b64decode(enc)
    Key = '%!$!%_$&!%F)&^!^'.encode('utf-8') 
    iv =  '#*y*#2yJ*#$wJv*v'.encode('utf-8') 
    cipher = AES.new(Key, AES.MODE_CBC, iv)
    plaintext =  unpad(cipher.decrypt(enc), AES.block_size)
    return plaintext.decode('utf-8')

async def download_and_send_video(app, m, url, title):
    try:
        safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', title)[:50]
        filename = f"{safe_title}.mp4"
        ydl_opts = {
            'outtmpl': filename,
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best[height<=720]',
            'merge_output_format': 'mp4',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await m.reply_video(video=filename, caption=f"🎬 {title}", supports_streaming=True)
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        await m.reply_text(f"❌ Error downloading {title}\n{str(e)}")

@app.on_message(filters.command("utkarshlogin"))
async def handle_utk_logic(app, m):
    await m.reply_text("🔹 Send **ID*Password** (Utkarsh Login)
Example: `12345*password`")
    input1 = await app.listen(chat_id=m.chat.id)
    raw_text = input1.text
    await input1.delete()
    if "*" not in raw_text:
        await m.reply_text("❌ Invalid format! Use ID*Password")
        return
    ids, ps = raw_text.split("*")

    # Get token
    token_response = requests.get('https://online.utkarsh.com/web/home/get_states')
    token = token_response.json()["token"]
    headers = {
        'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent':'Mozilla/5.0'
    }
    data = f"csrf_name={token}&mobile={ids}&url=0&password={ps}&submit=LogIn&device_token=null"
    log_response = requests.post('https://online.utkarsh.com/web/Auth/login', headers=headers, data=data).json()["response"]
    dec_log = decrypt(log_response.replace('MDE2MTA4NjQxMDI3NDUxNQ==','==').replace(':','=='))
    dec_logs = json.loads(dec_log)
    if not dec_logs.get("status"):
        await m.reply_text("❌ Login Failed")
        return
    await m.reply_text("✅ Login Success! Fetching batches...")

    # Fetch batches
    data2 = f"type=Batch&csrf_name={token}&sort=0"
    res2 = requests.post('https://online.utkarsh.com/web/Profile/my_course', headers=headers, data=data2).json()["response"]
    decrypted_res = decrypt(res2.replace('MDE2MTA4NjQxMDI3NDUxNQ==','==').replace(':','=='))
    dc = json.loads(decrypted_res)
    bdetail = dc['data'].get("data", [])

    if not bdetail:
        await m.reply_text("❌ No courses found!")
        return

    msg = "📚 Your Batches:\n"
    for item in bdetail:
        msg += f"<code>{item['id']}</code> - {item['title']}\n"
    await m.reply_text(msg)

    # Ask batch id
    input2 = await app.listen(chat_id=m.chat.id)
    batch_id = input2.text.strip()
    await input2.delete()

    # Simulated: fetch 3 sample video urls (in real, fetch topics here)
    sample_urls = [
        ("Sample Video 1", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        ("Sample Video 2", "https://www.youtube.com/watch?v=9bZkp7q19f0"),
        ("Sample Video 3", "https://www.youtube.com/watch?v=3JZ_D3ELwOQ")
    ]

    for title, url in sample_urls:
        await download_and_send_video(app, m, url, title)
