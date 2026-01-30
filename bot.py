import os
import random
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- RENDER SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    Thread(target=run).start()

# --- CONFIGURATION ---
TOKEN = "8285451307:AAH43YwSEXc_0JX5ES-RfUU_Ms8562izdzI" 
FONT_DIR = "fonts"

# --- NEW STYLISH ENGINE ---
def make_stylish_edit(img_path, text, font_name):
    if img_path:
        img = Image.open(img_path).convert("RGBA")
    else:
        img = Image.new('RGB', (1080, 1080), color=(10, 10, 10)).convert("RGBA")
    
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    try:
        f_path = os.path.join(FONT_DIR, font_name)
        # Bada Font (Main Name)
        font_main = ImageFont.truetype(f_path, int(h/7))
        # Chota Font (Bottom Text)
        font_sub = ImageFont.truetype(f_path, int(h/15))
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # --- GLOW EFFECT LOGIC ---
    # Layer for glow
    glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    
    # Draw thick red/orange shadow for glow
    glow_draw.text((w/2, h-h//4), text, fill=(255, 50, 0, 255), font=font_main, anchor="ms", stroke_width=15)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=10))
    
    # Merge glow with main image
    img.alpha_composite(glow_layer)
    
    # Draw Main Yellow Text
    draw.text((w/2, h-h//4), text, fill="yellow", font=font_main, anchor="ms", stroke_width=2, stroke_fill="white")
    
    # Draw "Girl" Style sub-text
    draw.text((w/2 + 100, h-h//6), "Girl", fill="white", font=font_sub, anchor="ms")

    out = "stylish_output.png"
    img.convert("RGB").save(out)
    return out

# --- HANDLERS ---
async def start(u, c):
    await u.message.reply_text("Bhai! Ab bot naye Killer Style mein edit karega. Photo bhejien!")

async def handle_input(u, c):
    msg = u.message.caption or u.message.text
    if not msg: return
    c.user_data['t'] = msg
    
    if u.message.photo:
        f = await u.message.photo[-1].get_file()
        await f.download_to_drive("in.png")
        c.user_data['p'] = "in.png"
    else:
        c.user_data['p'] = None

    all_f = [f for f in os.listdir(FONT_DIR) if f.endswith('.ttf')]
    btns = [[InlineKeyboardButton(f"Style Font: {fn}", callback_data=f"S:{fn}")] for fn in all_f]
    await u.message.reply_text("Font chunein (Glow effect ke saath):", reply_markup=InlineKeyboardMarkup(btns))

async def button(u, c):
    q = u.callback_query
    await q.answer()
    d = q.data.split(":")
    
    if d[0] == "S":
        await q.edit_message_text("Killer Style Editing chalu hai... 🔥")
        res = make_stylish_edit(c.user_data.get('p'), c.user_data.get('t'), d[1])
        await q.message.reply_photo(open(res, 'rb'), caption="Ye lo bhai Killer Look!")

# --- RUN ---
if __name__ == '__main__':
    keep_alive()
    app_bot = Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.ALL, handle_input))
    app_bot.add_handler(CallbackQueryHandler(button))
    app_bot.run_polling()
