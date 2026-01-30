import os
import random
import requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# --- RENDER KO JAGA KE RAKHNE KE LIYE FLASK ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURATION ---
TOKEN = "8285451307:AAH43YwSEXc_0JX5ES-RfUU_Ms8562izdzI" # @BotFather wala token
FONT_PATH = "font.ttf" 

# --- IMAGE EDITING LOGIC ---
def process_graphics(input_path, text, mode="DP"):
    if input_path:
        img = Image.open(input_path).convert("RGBA")
    else:
        # Auto-Background Generator (Random Colors)
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(150, 255))
        img = Image.new('RGB', (1080, 1080), color=color).convert("RGBA")
    
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    # Font setup
    try:
        font = ImageFont.truetype(FONT_PATH, int(h/12))
    except:
        font = ImageFont.load_default()

    # Style Setting
    fill_color = "yellow" if mode == "THUMB" else "white"
    
    # Text Drawing (Center Bottom)
    draw.text((w/2, h-h//6), text, fill=fill_color, font=font, anchor="ms", stroke_width=4, stroke_fill="black")

    output = "result.png"
    img.convert("RGB").save(output)
    return output

# --- BOT HANDLERS ---
async def start(update, context):
    await update.message.reply_text("👋 Hello! Photo bhej kar caption mein naam likhein, ya sirf apna naam message karein.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        # Photo download karein
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive("user_img.png")
        context.user_data['text'] = update.message.caption or "Victor Edit"
        
        # Style selection buttons
        btns = [[InlineKeyboardButton("Thumbnail Style", callback_data='THUMB'),
                 InlineKeyboardButton("DP Style", callback_data='DP')]]
        await update.message.reply_text("Kaunsa style chahiye?", reply_markup=InlineKeyboardMarkup(btns))
    elif update.message.text:
        # Sirf naam aaya toh background khud banayega
        path = process_graphics(None, update.message.text)
        await update.message.reply_photo(open(path, 'rb'), caption="✨ Aapka Background ready hai!")

async def callback(update, context):
    query = update.callback_query
    await query.answer()
    mode = query.data
    text = context.user_data.get('text', 'Victor Edit')
    
    await query.edit_message_text("Processing... ⏳")
    path = process_graphics("user_img.png", text, mode)
    await query.message.reply_photo(open(path, 'rb'), caption=f"Done! Style: {mode}")

# --- MAIN RUN ---
if __name__ == '__main__':
    keep_alive() # Render worker start
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_message))
    bot_app.add_handler(CallbackQueryHandler(callback))
    print("Bot is starting...")
    bot_app.run_polling()
