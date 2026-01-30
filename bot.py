import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- RENDER KEEP-ALIVE ---
app = Flask('')
@app.route('/')
def home(): return "AI Custom Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    Thread(target=run).start()

# --- CONFIGURATION ---
TOKEN = "8285451307:AAH43YwSEXc_0JX5ES-RfUU_Ms8562izdzI" 
FONT_DIR = "fonts"

def get_font(h, size_div=7):
    try:
        f_name = [f for f in os.listdir(FONT_DIR) if f.endswith('.ttf')][0]
        return ImageFont.truetype(os.path.join(FONT_DIR, f_name), int(h/size_div))
    except:
        return ImageFont.load_default()

# --- AI NEON ENGINE ---
def ai_custom_edit(img_path, user_cmd):
    words = user_cmd.split()
    name = words[0]
    
    # Default Settings
    glow_color = (255, 0, 0, 255) # Default Red
    text_color = "white"
    y_pos_factor = 0.5 # Center
    
    cmd_lower = user_cmd.lower()

    # --- COLOR SELECTION LOGIC ---
    colors = {
        "red": (255, 0, 0, 255),
        "blue": (0, 200, 255, 255),
        "green": (0, 255, 100, 255),
        "pink": (255, 0, 200, 255),
        "yellow": (255, 255, 0, 255),
        "purple": (150, 0, 255, 255),
        "gold": (255, 215, 0, 255),
        "cyan": (0, 255, 255, 255)
    }
    
    for c_name, c_val in colors.items():
        if c_name in cmd_lower:
            glow_color = c_val
            break

    # --- POSITION LOGIC ---
    if "top" in cmd_lower: y_pos_factor = 0.25
    if "bottom" in cmd_lower: y_pos_factor = 0.8

    # Image Processing
    img = Image.open(img_path).convert("RGBA") if img_path else Image.new('RGBA', (1080, 1080), (15, 15, 15, 255))
    w, h = img.size
    draw = ImageDraw.Draw(img)
    font = get_font(h)
    y_pos = h * y_pos_factor

    # --- APPLY NEON GLOW ---
    if "neon" in cmd_lower:
        glow_layer = Image.new("RGBA", img.size, (0,0,0,0))
        glow_draw = ImageDraw.Draw(glow_layer)
        # Thick Glow Line
        glow_draw.text((w/2, y_pos), name, fill=glow_color, font=font, anchor="ms", stroke_width=25)
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(15))
        img.alpha_composite(glow_layer)

    # --- MAIN TEXT ---
    draw.text((w/2, y_pos), name, fill=text_color, font=font, anchor="ms", stroke_width=2, stroke_fill="black")

    out = "custom_ai_output.png"
    img.convert("RGB").save(out)
    return out

# --- HANDLERS ---
async def handle_msg(update, context):
    cmd = update.message.caption or update.message.text
    if not cmd: return
    
    status = await update.message.reply_text(f"🤖 AI: Creating {cmd} style...")
    
    path = None
    if update.message.photo:
        path = "input.png"
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive(path)

    try:
        result = ai_custom_edit(path, cmd)
        await update.message.reply_photo(photo=open(result, 'rb'), caption=f"✨ Done! Style: {cmd}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
    await status.delete()

if __name__ == '__main__':
    keep_alive()
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(MessageHandler(filters.ALL, handle_msg))
    bot.run_polling()
