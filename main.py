import discord
from discord.ext import commands, tasks
import os
from flask import Flask
from threading import Thread
import requests
import time

# 1. إعداد خادم Flask
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and kicking!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. وظيفة التنبيه الذاتي (Self-Ping)
def ping_self():
    # انتظر قليلاً حتى يبدأ السيرفر بالعمل
    time.sleep(30)
    # استبدل 'your-app-name' باسم تطبيقك في Render
    # أو سيحاول الكود استنتاجه من البيئة إذا كان متاحاً
    url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost')}"
    
    while True:
        try:
            requests.get(url)
            print("Successfully pinged self!")
        except Exception as e:
            print(f"Ping failed: {e}")
        # انتظر 10 دقائق (600 ثانية) قبل التنبيه القادم
        time.sleep(600)

def keep_alive():
    # تشغيل خادم Flask
    t1 = Thread(target=run)
    t1.start()
    # تشغيل التنبيه الذاتي
    t2 = Thread(target=ping_self)
    t2.daemon = True
    t2.start()

# 3. إعدادات البوت
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} جاهز للعمل!')

# --- أضف بقية أوامر البوت هنا ---

if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    bot.run(token)
