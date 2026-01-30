import os
import random
import requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from PIL import Image, ImageDraw, ImageFont

# --- RENDER SERVER (Don't touch) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    Thread(target=run).start()

# --- CONFIGURATION ---
TOKEN = "8285451307:AAH43YwSEXc_0JX5ES-RfUU_Ms8562izdzI" 
FONT_DIR = "fonts"

# --- CORE LOGIC ---
def make_edit(img_path, text, font_name, mode):
    if img_path:
        img = Image.open(img_path).convert("RGBA")
    else:
        img = Image.new('RGB', (1080, 1080), color=(20, 20, 20)).convert("RGBA")
    
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    try:
        f_path = os.path.join(FONT_DIR, font_name)
        font = ImageFont.truetype(f_path, int(h/12))
    except:
        font = ImageFont.load_default()

    txt_color = "yellow" if mode == "THUMB" else "white"
    draw.text((w/2, h-150), text, fill=txt_color, font=font, anchor="ms", stroke_width=5, stroke_fill="black")
    
    out = "final.png"
    img.convert("RGB").save(out)
    return out

# --- HANDLERS ---
async def start(u, c):
    await u.message.reply_text("Bhai! Photo bhej ya naam likh, main edit kar dunga.")

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
    btns = [[InlineKeyboardButton(f"Font: {fn}", callback_data=f"F:{fn}")] for fn in all_f]
    await u.message.reply_text("Font Select Karein:", reply_markup=InlineKeyboardMarkup(btns))

async def button(u, c):
    q = u.callback_query
    await q.answer()
    d = q.data.split(":")
    
    if d[0] == "F":
        btns = [[InlineKeyboardButton("Thumbnail Style", callback_data=f"S:THUMB:{d[1]}"),
                 InlineKeyboardButton("DP Style", callback_data=f"S:DP:{d[1]}")]]
        await q.edit_message_text(f"Font '{d[1]}' set! Style chunein:", reply_markup=InlineKeyboardMarkup(btns))
    
    elif d[0] == "S":
        await q.edit_message_text("Editing chalu hai... 🎨")
        res = make_edit(c.user_data.get('p'), c.user_data.get('t'), d[2], d[1])
        await q.message.reply_photo(open(res, 'rb'), caption="Ye lo bhai!")

# --- RUN ---
if __name__ == '__main__':
    keep_alive()
    app_bot = Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.ALL, handle_input))
    app_bot.add_handler(CallbackQueryHandler(button))
    app_bot.run_polling()
