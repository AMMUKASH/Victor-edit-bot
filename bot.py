import os
import random
import requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# --- RENDER KEEP-ALIVE SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    Thread(target=run).start()

# --- CONFIGURATION ---
# @BotFather se liya hua asli token yahan daalein
TOKEN = "8285451307:AAH43YwSEXc_0JX5ES-RfUU_Ms8562izdzI" 
FONT_DIR = "fonts"

# --- IMAGE PROCESSING ENGINE ---
def process_graphics(input_path, text, font_name, mode):
    if input_path:
        img = Image.open(input_path).convert("RGBA")
    else:
        # Background color for text-only messages
        bg = (random.randint(10, 50), random.randint(10, 50), random.randint(10, 50))
        img = Image.new('RGB', (1080, 1080), color=bg).convert("RGBA")
    
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    try:
        font_path = os.path.join(FONT_DIR, font_name)
        font = ImageFont.truetype(font_path, int(h/10))
    except:
        font = ImageFont.load_default()

    # Style Selection
    txt_color = "yellow" if mode == "THUMB" else "white"
    
    # Draw Text with Shadow/Stroke
    draw.text((w/2, h - h//5), text, fill=txt_color, font=font, anchor="ms", stroke_width=4, stroke_fill="black")

    out_path = "output.png"
    img.convert("RGB").save(out_path)
    return out_path

# --- TELEGRAM HANDLERS ---
async def start(update, context):
    await update.message.reply_text("👋 Hello! Photo bhej kar caption mein naam likhein, ya sirf text message bhejien.")

async def handle_msg(update, context):
    user_text = update.message.caption or update.message.text
    if not user_text:
        await update.message.reply_text("Bhai, kuch naam toh likho!")
        return

    context.user_data['text'] = user_text
    
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive("input.png")
        context.user_data['has_img'] = True
    else:
        context.user_data['has_img'] = False

    # Check for fonts in folder
    if not os.path.exists(FONT_DIR):
        await update.message.reply_text("Error: 'fonts' folder nahi mila!")
        return
        
    all_fonts = [f for f in os.listdir(FONT_DIR) if f.endswith('.ttf')]
    if not all_fonts:
        await update.message.reply_text("Error: Fonts folder khali hai!")
        return

    # Create Buttons for Fonts
    keyboard = [[InlineKeyboardButton(f"Font: {f}", callback_data=f"F:{f}")] for f in all_fonts]
    await update.message.reply_text("Ek Font select karein:", reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data.split(":")
    
    if data[0] == "F":
        f_name = data[1]
        btns = [[InlineKeyboardButton("Thumbnail Style", callback_data=f"S:THUMB:{f_name}"),
                 InlineKeyboardButton("DP Style", callback_data=f"S:DP:{f_name}")]]
        await query.edit_message_text(f"Font '{f_name}' selected. Ab Style chunein:", reply_markup=InlineKeyboardMarkup(btns))
    
    elif data[0] == "S":
        mode, f_name = data[1], data[2]
        await query.edit_message_text("Processing... 🎨")
        
        text = context.user_data.get('text', 'Victor Edit')
        path = "input.png" if context.user_data.get('has_img') else None
        
        result = process_graphics(path, text, f_name, mode)
        await query.message.reply_photo(photo=open(result, 'rb'), caption="Ye lijiye aapki edit!")

# --- MAIN ---
if name == 'main':
    keep_alive()
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(filters.ALL, handle_msg))
    bot.add_handler(CallbackQueryHandler(callback_handler))
    bot.run_polling()
