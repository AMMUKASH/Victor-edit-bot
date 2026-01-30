import os
import random
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# --- FLASK SERVER FOR RENDER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURATION ---
TOKEN = "8285451307:AAH43YwSEXc_0JX5ES-RfUU_Ms8562izdzI"
LOGO_PATH = "my_logo.png" 
FONT_PATH = "font.ttf" 

# --- EDITING LOGIC ---
def process_graphics(input_path, text, mode="DP"):
    if input_path:
        img = Image.open(input_path).convert("RGBA")
    else:
        # Auto-Background Generator
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(150, 255))
        img = Image.new('RGB', (1080, 1080), color=color).convert("RGBA")
    
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    try:
        font = ImageFont.truetype(FONT_PATH, int(h/10))
    except:
        font = ImageFont.load_default()

    # Style setting
    fill_color = "yellow" if mode == "THUMB" else "white"
    draw.text((w/2, h-150), text, fill=fill_color, font=font, anchor="ms", stroke_width=4, stroke_fill="black")

    # Logo add karein (agar file hai toh)
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo.thumbnail((w/6, h/6))
        img.paste(logo, (20, 20), logo)

    output = "result.png"
    img.convert("RGB").save(output)
    return output

# --- BOT HANDLERS ---
async def start(update, context):
    await update.message.reply_text("Photo bhejiye caption ke saath, ya sirf apna naam likh kar bhejiye!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive("user_img.png")
        context.user_data['text'] = update.message.caption or "Edit"
        
        btns = [[InlineKeyboardButton("Thumbnail", callback_data='THUMB'),
                 InlineKeyboardButton("DP Style", callback_data='DP')]]
        await update.message.reply_text("Style chunein:", reply_markup=InlineKeyboardMarkup(btns))
    else:
        # Sirf text aaya toh auto-background
        path = process_graphics(None, update.message.text)
        await update.message.reply_photo(open(path, 'rb'), caption="Aapki Graphic taiyaar hai! 🔥")

async def callback(update, context):
    query = update.callback_query
    await query.answer()
    path = process_graphics("user_img.png", context.user_data.get('text', 'Edit'), query.data)
    await query.message.reply_photo(open(path, 'rb'))

# --- MAIN ---
if name == 'main':
    keep_alive() # Render ko jagaane ke liye
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_message))
    bot_app.add_handler(CallbackQueryHandler(callback))
    bot_app.run_polling()
