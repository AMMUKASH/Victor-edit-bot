import os
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Fix Position Bot Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    Thread(target=run).start()

# --- CONFIG ---
TOKEN = "8285451307:AAH43YwSEXc_0JX5ES-RfUU_Ms8562izdzI"
FONT_DIR = "fonts"

def get_font(h):
    try:
        f_path = os.path.join(FONT_DIR, os.listdir(FONT_DIR)[0])
        return ImageFont.truetype(f_path, int(h/7))
    except:
        return ImageFont.load_default()

# --- HYBRID ENGINE ---
def generate_fixed_style(name):
    # 1. AI se sirf Background banwana (bina naam ke)
    prompt = "professional 3d neon gaming background, abstract futuristic lighting, red and blue theme, high resolution, no text"
    url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed={os.urandom(4).hex()}"
    
    response = requests.get(url)
    if response.status_code == 200:
        with open("bg.jpg", "wb") as f:
            f.write(response.content)
        
        # 2. PIL se Fixed Jagah par naam likhna
        img = Image.open("bg.jpg").convert("RGBA")
        w, h = img.size
        draw = ImageDraw.Draw(img)
        font = get_font(h)
        
        # Fixed Position: Bottom se thoda upar (Center horizontal)
        y_pos = h * 0.85 
        
        # Neon Glow Effect
        glow = Image.new("RGBA", img.size, (0,0,0,0))
        g_draw = ImageDraw.Draw(glow)
        g_draw.text((w/2, y_pos), name, fill=(255, 0, 100, 255), font=font, anchor="ms", stroke_width=20)
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(15)))
        
        # Main Text
        draw.text((w/2, y_pos), name, fill="white", font=font, anchor="ms", stroke_width=2, stroke_fill="black")
        
        out = "fixed_output.png"
        img.convert("RGB").save(out)
        return out
    return None

async def handle_message(update, context):
    name = update.message.text
    status = await update.message.reply_text(f"⏳ {name} ke liye background taiyar ho raha hai...")
    
    res = generate_fixed_style(name)
    if res:
        await update.message.reply_photo(photo=open(res, 'rb'), caption=f"🔥 Fixed Style for: {name}")
    else:
        await update.message.reply_text("Server Busy!")
    await status.delete()

if __name__ == '__main__':
    keep_alive()
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot.run_polling()
