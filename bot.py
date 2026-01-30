import os
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# --- RENDER SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Free AI Generator is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    Thread(target=run).start()

# --- CONFIG ---
TOKEN = "8285451307:AAH43YwSEXc_0JX5ES-RfUU_Ms8562izdzI"

# --- FREE AI GENERATION ENGINE ---
def generate_ai_image(prompt):
    # Pollinations AI use kar rahe hain jo bilkul free hai
    # Prompt ko URL friendly banana
    formatted_prompt = prompt.replace(" ", "%20")
    # AI Model: Flux ya Realistic (Free API)
    url = f"https://pollinations.ai/p/{formatted_prompt}?width=1024&height=1024&seed={os.urandom(4).hex()}&model=flux"
    
    response = requests.get(url)
    if response.status_code == 200:
        with open("ai_generated.jpg", "wb") as f:
            f.write(response.content)
        return "ai_generated.jpg"
    return None

# --- TELEGRAM HANDLERS ---
async def start(update, context):
    await update.message.reply_text("🔥 **ʙᴀʙʏ, ʀᴜᴋᴏ ɴᴀ ban gaya hai!**\n\nJo bhi image chahiye, bas likh kar bhejo.\nExample: 'Victoria name logo professional red neon'")

async def handle_ai_request(update, context):
    user_prompt = update.message.text
    status = await update.message.reply_text(f"🚀 AI '{user_prompt}' par kaam kar raha hai... Thoda wait karo.")

    try:
        image_path = generate_ai_image(user_prompt)
        if image_path:
            await update.message.reply_photo(photo=open(image_path, 'rb'), caption=f"✅ Ye lo bhai aapka  Image!\nPrompt: {user_prompt}")
        else:
            await update.message.reply_text("❌ ᴠɪᴄᴛᴏʀ server busy hai, thodi der baad try karo.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error aagaya: {e}")
    
    await status.delete()

# --- MAIN ---
if __name__ == '__main__':
    keep_alive()
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_request))
    bot.run_polling()
